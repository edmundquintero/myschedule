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

def conflict_resolution(sections):
    """
        Checks for any conflicts between the sections on the schedule.
        Presently, just for classes with overlapping times.
    """
    cart_items = get_section_data(sections)
    conflicting_sections = []
    for section in sections:
        test_section = get_object_or_404(models.Section,
                                         section_code=section)
        test_meetings = test_section.meeting_set.all()
        for item in cart_items:
            section_data = item['section_data']
            meeting_data = item['meeting_data']
            if test_section.section_code != section_data.section_code:
                if test_section not in conflicting_sections:
                    if ((test_section.start_date <= section_data.start_date and
                         section_data.start_date <= test_section.end_date) or
                        (test_section.start_date <= section_data.end_date and
                         section_data.end_date <= test_section.end_date) or
                        (section_data.start_date <= test_section.start_date and
                         test_section.start_date <= section_data.end_date) or
                        (section_data.start_date <= test_section.end_date and
                         test_section.end_date <= section_data.end_date)):
                        # the sections start / end dates have some overlap so
                        # continue checking for potential conflict
                        for test_meeting in test_meetings:
                            for comparison_meeting in meeting_data:
                                # Check to see if the meetings have any days in common
                                commondays = "".join(filter(lambda x: x in comparison_meeting.days_of_week,
                                    test_meeting.days_of_week))
                                if commondays:
                                    # Check to see if the meeting times overlap
                                    if ((test_meeting.start_time <= comparison_meeting.start_time and
                                         comparison_meeting.start_time <= test_meeting.end_time) or
                                        (test_meeting.start_time <= comparison_meeting.end_time and
                                         comparison_meeting.end_time <= test_meeting.end_time) or
                                        (comparison_meeting.start_time <= test_meeting.end_time and
                                         test_meeting.start_time <= comparison_meeting.end_time) or
                                        (comparison_meeting.start_time <= test_meeting.end_time and
                                         test_meeting.end_time <= comparison_meeting.end_time)):
                                            conflicting_sections.append(test_section.section_code)
    return conflicting_sections

def get_section_data(sections):
    """
        Get the section and course data for a list of sections.
    """
    cart_items=[]
    for section in sections:
        item={}
        item={}
        section_data = get_object_or_404(models.Section,
                                  section_code=section)
        course_data = section_data.course
        meeting_data = section_data.meeting_set.all()
        item = dict({"section_data":section_data, "course_data":course_data, "meeting_data":meeting_data})
        cart_items.append(item)
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
    conflicting_sections = []
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
        conflicting_sections = conflict_resolution(sections)
    else:
        cart_items = []
    return direct_to_template(request,
                              'myschedule/display_cart.html',
                              {'cartitems':cart_items,
                               'conflicting_sections':conflicting_sections}
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
        meeting_data = item['meeting_data']
        message = (
            "Course: %s %s %s  " % (course_data.prefix,
                                  course_data.course_number,
                                  course_data.title) +
            "Section: %s \n" % (section_data.section_number) +
            "Instructor: %s \n" % (section_data.instructor_name) +
            "Campus: %s \n" % (section_data.campus))
        for meeting in meeting_data:
            message = message + (
                "Type: %s \n" % (meeting.meeting_type) +
                "Building / Room: %s %s \n" % (meeting.building, meeting.room) +
                "Meeting Days & Times: %s %s - %s \n" % (meeting.days_of_week, meeting.start_time, meeting.end_time)
            )
        message = message + (
            "View book information at %s. \n" % (section_data.book_link)
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

