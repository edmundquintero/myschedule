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
    sections = []
    if request.session.has_key('Cart'):
        sections = request.session['Cart']
    if section not in sections:
        sections.append(section)
        request.session['Cart'] = sections
    if request.user.is_authenticated():
        save_cart(request)
    json_data = {'errors':errors}
    json_data = json.dumps(json_data)
    # return JSON object to browser
    return HttpResponse(json_data)

def save_cart(request):
    """
        Saves the user's working schedule (cart).
    """
    errors = ''
    sections_url = ''
    if request.session.has_key('Cart'):
        for item in request.session['Cart']:
            sections_url = sections_url + item + '/'
    if sections_url != '':
        try:
            # See if a schedule already exists for this user.
            cart = models.Schedule.objects.get(owner=request.user)
            cart.sections = sections_url
        except models.Schedule.DoesNotExist:
            cart = models.Schedule(owner=request.user,
                           sections=sections_url)
        except:
            #TODO: error handling
            print 'failure'
        cart.save()
    return errors

def delete_cartitem(request, section):
    """
        Deletes the specified course section from the cart.
    """
    #TODO: Re-run validation when they remove a section
    if request.session.has_key('Cart'):
        sections = request.session['Cart']
        sections.remove(section)
        request.session['Cart'] = sections
        if request.user.is_authenticated():
            save_cart(request)
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
        section_data = get_object_or_404(models.Section,
                                  section_code=section)
        course_data = section_data.course
        meeting_data = section_data.meeting_set.all()
        item = dict({"section_data":section_data, "course_data":course_data, "meeting_data":meeting_data})
        cart_items.append(item)
    return cart_items

def show_schedule(request):
    """
        Processes selection of schedule tab.
    """
    sections_url = ""
    if request.session.has_key('Cart'):
        for item in request.session['Cart']:
            sections_url = sections_url + item + '/'
    else:
        sections_url = None
    return HttpResponseRedirect(reverse('display_cart', args=[sections_url]))

def display_cart(request, sections_url=None):
    """
        Displays shopping cart template.
    """

    conflicting_sections = []
    if not request.session.has_key('Cart') and sections_url == None:
        return redirect('index')
    elif not request.session.has_key('Cart') and sections_url != None:
        sections = sections_url.split("/")
        sections.remove('')
        request.session['Cart'] = sections
    # TODO: get all the other information regarding a course section that
    # needs to be displayed
    sections = request.session['Cart']

    if sections != [] and sections != None:
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
    sections = []
    sections_url = ''
    if 'Cart' in request.session:
        sections = request.session['Cart']
        for item in sections:
            sections_url = sections_url + item + '/'
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

