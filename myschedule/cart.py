from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.views.generic.simple import direct_to_template
from django.conf import settings
from django.utils import simplejson as json

from cpsite import ods
# from cpsite.decorators import groups_required

from myschedule import models, forms
from myschedule.views import compose_booklink

def validate_section(request, section_to_add):
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

def add_item(request):
    """
        Adds the selected course section to the cart session variable.
    """
    # TODO: Reload sections (so schedule tab will appear) and hide the section they just added
    section = request.POST['section']
    errors = ''
    sections_url = ''
    if 'WorkingCart' in request.session:
        sections_url = request.session['WorkingCart']
    if section not in sections_url:
        # TODO: Run validation to check for conflicts.
        request.session['WorkingCart'] = sections_url + section + '/'
    json_data = {'errors':errors}
    json_data = json.dumps(json_data)
    # return JSON object to browser
    return HttpResponse(json_data)

@login_required
def save_schedule(request):
    if request.method == 'POST':
        description = request.POST['save_name']
        user = get_object_or_404(models.User, username=request.user)
        cart = models.Cart(owner=user,
                           description=description,
                           sections=request.session['WorkingCart'])
        cart.save()
        return redirect('show_schedule')
    return direct_to_template(request,
                              'myschedule/save.html',{})

def delete_cartitem(request, section):
    """
        Deletes the specified course section from the shopping cart.
    """
    #TODO: Re-run validation when they remove a section
    # TODO: Check for missing session variable
    sections = request.session['WorkingCart']
    request.session['WorkingCart'] = sections.replace(section+'/',"")
    return redirect('show_schedule')

def get_cartitems(request):
    """
        Returns items in the cart for a specific cart ID or user.
        TODO: Remove if don't need after switching to passing sections via url.
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

def get_section_data(sections):
    """
        Get the section and course data for a list of sections.
    """
    cart_items=[]
    for section in sections:
        item={}
        try:
            ods_spec_dict = {"key": settings.CPAPI_KEY,
                             "data": "sections",
                             "id": section}
            section_data = ods.get_data(ods_spec_dict)
            ods_spec_dict = {"key": settings.CPAPI_KEY,
                             "data": "course",
                             "prefix": section_data['prefix'],
                             "number": section_data['number']}
            # Returns a list TODO: Need to query this with course ID not prefix & number.
            course_data = ods.get_data(ods_spec_dict)[0]
            # Get the link to the book information TODO: replace hard-coded campus code with proper field when cpapi is updated to return location
            booklink = compose_booklink('1013', section_data['term'],
                              section_data['year'], section_data['prefix'],
                              section_data['number'], section_data['section'])

            item = dict({"section_data":section_data, "course_data":course_data, "booklink":booklink})
            cart_items.append(item)
        except:
            # TODO: Do something besides pass
            pass
    return cart_items

def show_schedule(request):
    """
        Processes selection of schedule tab.
    """
    # TODO: Check for missing session variable
    sections=request.session['WorkingCart']
    return HttpResponseRedirect(reverse('display_cart', args=[sections]))

def display_cart(request, sections):
    """
        Displays shopping cart template.
    """
    # TODO: get all the other information regarding a course section that
    # needs to be displayed
    sections = sections.split("/")
    sections.remove('')
    cart_items = get_section_data(sections)
    return direct_to_template(request,
                              'myschedule/display_cart.html',
                              {'cartitems':cart_items,
                               'is_display_cart':True}
                             )


