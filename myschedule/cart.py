# from django.contrib.auth.decorators import login_required
# from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.generic.simple import direct_to_template

# from cpsite import ods
# from cpsite.decorators import groups_required

from myschedule import models, forms

def add_cartitem(request, section):
    """
        Adds the specified course section to the user's shopping cart.
        If this is the first item added, create the cart record before
        adding the cartitem.
    """
    #TODO: Perform validations (check to see if already in cart, etc).
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

def delete_cartitem(itemID):
    """
        Deletes the specified course section from the shopping cart.
    """
    cart_item = []
    try:
        cart_item = models.CartItem.objects.get(id=itemID)
        cart_item.delete()
    except models.CartItem.DoesNotExist:
        # Should mean it was already deleted so don't raise a 404.
        pass
    return cart_item

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
    return cart_items

def display_cart(request):
    """
        Displays shopping cart template.
    """
    # TODO: get all the other information regarding a course section that
    # needs to be displayed
    cart_items = get_cartitems(request)
    return direct_to_template(request,
                              'myschedule/display_cart.html',
                              {'cartitems':cart_items}
                             )

