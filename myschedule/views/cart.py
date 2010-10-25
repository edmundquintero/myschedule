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
from myschedule.views import compose_booklink, get_schedules


"""
    What is a cart?
    The cart represents the schedule that is currently being edited
    (having courses added and removed).
"""

def add_item(request):
    """
        Adds the selected course section to the cart session variable.
    """
    section = request.POST['section']
    errors = ''
    sections_url = ''
    if 'WorkingCart' in request.session:
        sections_url = request.session['WorkingCart']
    if section not in sections_url:
        # TODO: Run validation to check for conflicts.
        request.session['WorkingCart'] = sections_url + section + '/'
    if request.session.has_key('SelectedScheduleName'):
        # Contents of a saved schedule were changed - remove the schedule name
        # from the session variable so "unsaved schedule" message will display.
        request.session.pop('SelectedScheduleName')
    json_data = {'errors':errors}
    json_data = json.dumps(json_data)
    # return JSON object to browser
    return HttpResponse(json_data)

def save_cart(request):
    """
        Saves the user's working schedule (cart).  Will overwrite an existing
        schedule with the same name.
    """
    errors = ''
    if request.method == 'POST':
        description = request.POST['save_name']
        try:
            # See if a schedule with this name already exists.
            # TODO: This is not case sensitive.  To make it case sensitive
            # will require changing mysql setting.
            cart = models.Schedule.objects.get(
                           owner=request.user, description=description)
            cart.sections = request.session['WorkingCart']
        except models.Schedule.DoesNotExist:
            cart = models.Schedule(owner=request.user,
                           description=description,
                           sections=request.session['WorkingCart'])
        cart.save()
        # WorkingCart now contains the contents of a saved schedule.  Set the
        # SelectedScheduleName session variable so the name of the schedule
        # the user is viewing can be displayed on the page.
        request.session['SelectedScheduleName'] = cart.description

    json_data = {'errors':errors}
    json_data = json.dumps(json_data)
    # return JSON object to browser
    return HttpResponse(json_data)

def delete_cartitem(request, section):
    """
        Deletes the specified course section from the shopping cart.
    """
    #TODO: Re-run validation when they remove a section
    if request.session.has_key('WorkingCart'):
        sections = request.session['WorkingCart']
        request.session['WorkingCart'] = sections.replace(section+'/',"")
    if request.session.has_key('SelectedScheduleName'):
        # Contents of a saved schedule were changed - remove the schedule name
        # from the session variable so "unsaved schedule" message will display.
        request.session.pop('SelectedScheduleName')
    return redirect('show_schedule')

@login_required
def delete_schedule(request, cart_id):
    """
        Deletes a saved schedule from the table.
    """
    cart_instance = get_object_or_404(models.Schedule,
                                      id=cart_id,
                                      owner=request.user)
    if (request.session.has_key('SelectedScheduleName') and
        request.session.has_key('SelectedScheduleName') == cart_instance.description):
        # Contents of a saved schedule were changed - remove the schedule name
        # from the session variable so "unsaved schedule" message will display.
        request.session.pop('SelectedScheduleName')

    cart_instance.delete()

    return redirect('show_schedule')


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

def get_cart(request):
    """
        Retrieves the values in the WorkingCart and SavedSchedules session
        variables and returns them to the javascript function.
    """
    working_cart = ''
    saved_schedules = []
    if 'WorkingCart' in request.session:
        working_cart = request.session['WorkingCart']
    if 'SavedSchedules' in request.session:
        for schedule in request.session['SavedSchedules']:
            temp = {'description': schedule.description,
                    'sections': schedule.sections}
            saved_schedules.append(temp)
    json_data = {'cart_sections':working_cart, 'saved_schedules':saved_schedules}
    json_data = json.dumps(json_data, indent=2)
    # return JSON object to browser
    return HttpResponse(json_data)

def set_cart(request):
    """
        Sets session['WorkingCart'] to new value.
    """
    errors = ''
    try:
        selected_schedule_name = request.POST['selected_schedule_name']
        saved_schedules = request.session['SavedSchedules']
        selected_schedule = saved_schedules.get(description=selected_schedule_name)
        request.session['WorkingCart'] = selected_schedule.sections
        # WorkingCart now contains the contents of a saved schedule.  Set the
        # SelectedScheduleName session variable so the name of the schedule
        # the user is viewing can be displayed on the page.
        request.session['SelectedScheduleName'] = selected_schedule.description
    except:
        errors = 'An error occurred while updating the cart.'
    json_data = {'errors':errors}
    json_data = json.dumps(json_data)
    # return JSON object to browser
    return HttpResponse(json_data)

def show_schedule(request):
    """
        Processes selection of schedule tab.
    """
    if request.session.has_key('WorkingCart'):
        sections=request.session['WorkingCart']
    else:
        sections = ""
    return HttpResponseRedirect(reverse('display_cart', args=[sections]))

def display_cart(request, sections=None):
    """
        Displays shopping cart template.
    """
    saved_schedules = get_schedules(request)
    if not request.session.has_key('WorkingCart'):
        # Only way this should happen is if the user logs out from
        # the display_cart page - in which case we don't want to proceed.
        return redirect('index')
    # TODO: get all the other information regarding a course section that
    # needs to be displayed
    if sections != "" and sections != None:
        sections = sections.split("/")
        sections.remove('')
        cart_items = get_section_data(sections)
    else:
        cart_items = []
    return direct_to_template(request,
                              'myschedule/display_cart.html',
                              {'cartitems':cart_items}
                             )

def email_schedule(request):
    """
        Processes javascript request to email schedule.
    """
    from django.core.mail import send_mail
    from datetime import date
    email_addresses = request.POST['email_addresses']
    to_addressees = email_addresses.split(",")
    to_addressees.remove('')
    errors = ''
    sections_url = ''
    if 'WorkingCart' in request.session:
        sections_url = request.session['WorkingCart']
    sections = sections_url.split("/")
    sections.remove('')
    schedule = get_section_data(sections)
    app_host = request.get_host()
    schedule_url = reverse('display_cart',args=[sections_url])
    email_message = "View this schedule online at http://%s%s.\n\n" % (app_host, schedule_url)
    for item in schedule:
        course_data = item['course_data']
        section_data = item['section_data']
        booklink = item['booklink']
        message = (
            "Course: %s %s %s \n" % (course_data['prefix'],
                                  course_data['number'],
                                  course_data['title']) +
            "Section: %s \n" % (section_data['section']) +
            "Instructor: %s %s \n" % (section_data['instructor_first_name'],
                                      section_data['instructor_last_name']) +
            "Campus: \n"  +
            "Building / Room: \n" +
            "Meeting Days & Times: \n"
        )
        email_message = email_message + message + '\n'
    if email_message != "":
        send_mail('CPCC schedule',
                  email_message,
                  "myschedule@cpcc.edu",
                  to_addressees,
                  auth_user=None,
                  auth_password=None)
    json_data = {'errors':errors}
    json_data = json.dumps(json_data)
    # return JSON object to browser
    return HttpResponse(json_data)

