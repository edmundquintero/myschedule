# from django.contrib.auth.decorators import login_required
# from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.generic.simple import direct_to_template
from django.conf import settings

from cpsite import ods
# from cpsite.decorators import groups_required

from myschedule import models, forms
from myschedule.views import compose_booklink

define validate_section(request, section_to_add):
    """
        Specialized validation checking for conflicts between the section
        the user is attempting to add to the cart and the sections already
        in the cart.
    """
    # TODO: Need to call this via javascript
    conflicts = []
    if 'cartID' in request.session and not request.session['cartID'] == None:
        cart_items = models.CartItem.objects.filter(
                                cart_id=request.session['cartID'])
        # check to see if the section is already in the cart
        section_query = cart_items.filter(section=section_to_add)
        if section_query != []:
            conflicts.append('Course section ' +
                              section_to_add +
                             ' is already in your cart.')
        # TODO:check for conflicts with class times of items already in cart

    # TODO:check for available seats

    return conflicts

def add_cartitem(request, section):
    """
        Adds the specified course section to the user's shopping cart.
        If this is the first item added, create the cart record before
        adding the cartitem.
    """
    if 'cartID' not in request.session or request.session['cartID'] == None:
        # Cart does not exist for this user or session so create it first.
        # Cart only has an owner if the user logged in.
        if not request.user.is_anonymous():
            user = get_object_or_404(models.User, username=request.user)
        else:
            user = None
        cart = models.Cart(owner=user)
        cart.save()
        request.session['cartID'] = cart.id

    cart_item = models.CartItem(cart_id=request.session['cartID'],
                               section=section)
    cart_item.save()
    return cart_item

def delete_cartitem(request, itemID):
    """
        Deletes the specified course section from the shopping cart.
    """
    #TODO: Eventually want to call this from javascript
    #TODO: Re-run validation when they remove a section
    cart_item = []
    try:
        cart_item = models.CartItem.objects.get(id=itemID)
        cart_item.delete()
    except models.CartItem.DoesNotExist:
        # Should mean it was already deleted so don't raise a 404.
        pass
    return redirect('display_cart')

def get_cartitems(request):
    """
        Returns items in the cart for a specific cart ID or user.
    """
    cart_items = []
    # Use cartID if we have one to get items for a specific cart.
    if 'cartID' in request.session and request.session['cartID'] is not None:
        cart_items = models.CartItem.objects.filter(
                        cart=request.session['cartID'])
    else:
        # If there was no cart ID get cart via user ID if user logged in.
        # Currently assumes user can only have one cart.
        if not request.user.is_anonymous():
            user = get_object_or_404(models.User, username=request.user)
            cart_items = models.CartItem.objects.filter(cart__owner=user)
    # Get additional section and meeting data via cpapi
    for item in cart_items:
        try:
            ods_spec_dict = {"key": settings.CPAPI_KEY,
                             "data": "sections",
                             "id": item.section}
            section_data = ods.get_data(ods_spec_dict)
            item.section_data = section_data
            ods_spec_dict = {"key": settings.CPAPI_KEY,
                             "data": "course",
                             "prefix": section_data['prefix'],
                             "number": section_data['number']}
            # Returns a list TODO: handle more than one item?
            course_data = ods.get_data(ods_spec_dict)[0]
            item.course_data = course_data
            # Get the link to the book information TODO: replace hard-coded campus code with proper field when cpapi is updated to return location
            item.booklink = compose_booklink('1013', section_data['term'],
                              section_data['year'], section_data['prefix'],
                              section_data['number'], section_data['section'])
        except:
            # TODO: Do something besides pass
            pass
    return cart_items

def display_cart(request):
    """
        Displays shopping cart template.
    """
    # TODO: get all the other information regarding a course section that
    # needs to be displayed
    # TODO: remove setting of cartID - for testing only
    request.session['cartID']=1
    cart_items = get_cartitems(request)
    return direct_to_template(request,
                              'myschedule/display_cart.html',
                              {'cartitems':cart_items}
                             )

