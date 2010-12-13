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
    if request.session.has_key('current_query'):
        correlation = models.Correlation()
        correlation.criterion = request.session['current_query'].strip('|')
        if request.session.has_key('previous_query'):
            correlation.species = models.Correlation.WRONG_TERM
            correlation.criterion = correlation.criterion + '|' + request.session['previous_query']
            del request.session['previous query']
            request.session.modified = True
        else:
            correlation.species = models.Correlation.SUCCESSFUL_SEARCH
        correlation.course = section.course
        correlation.save()

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

def conflict_resolution(cart_items, sections):
    """
        Checks for any conflicts between the sections on the schedule.
        Presently, just for classes with overlapping times.
    """
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

def get_seats(informer_url, term, year, course_prefix, course_number,
              course_section=None):
    """
        Calls informer to retrieve the current seat counts for the specified
        course (and optional section).  Returns data in json format.

        TODOs: Make it a standalone api once we figure out where it needs to
        reside.  Add caching???
    """
    import urllib2
    from datetime import datetime

    informer_url = (informer_url + '?prefix=' + course_prefix +
                                   '&number=' + course_number +
                                   '&term=' + term +
                                   '&year=' + year)
    if course_section:
        informer_url = informer_url + '&section=' + course_section
    json_list=[]
    try:
        resp = urllib2.urlopen(informer_url)
        counts = resp.read()
        counts_list = counts.split(';')
        counts_list.remove('\r\n')
        for item in counts_list:
            temp_list = item.split(',')
            json_list.append({'prefix':temp_list[0],
                              'number':temp_list[1],
                              'section':temp_list[2],
                              'year':temp_list[3],
                              'term':temp_list[4],
                              'status':temp_list[5],
                              'seats':temp_list[6]})
    except:
        # In the event it was unable to retrieve a seat count
        # schedule builder will display a "seat count not available" message.
        pass
    json_data = json.dumps(json_list, indent=2)
    return json_data

def get_section_data(sections):
    """
        Get the section and course data for a list of sections.
    """
    from django.core.cache import cache

    cart_items=[]
    for section in sections:
        section_item={}
        # Check to see if the data for this section has been cached. If not,
        # query the model.
        section_item = cache.get(section)
        if section_item is None:
            section_data = get_object_or_404(models.Section,
                                  section_code=section)
            course_data = section_data.course
            meeting_data = section_data.meeting_set.all()
            # TODO: When get_seats is switched to external api, update this call.
            seat_counts = get_seats('http://watrain.cpcc.edu/SeatCount/SeatCount',
                                section_data.term.upper(),
                                section_data.year,
                                course_data.prefix,
                                course_data.course_number,
                                section_data.section_number)
            seat_counts = json.loads(seat_counts)
            if len(seat_counts) == 1:
                for item in seat_counts:
                   seat_count = item['seats'] + ' seat(s) available'
            else:
                seat_count = 'Seat count unavailable'
            section_item = dict({"section_data":section_data,
                     "course_data":course_data,
                     "meeting_data":meeting_data,
                     "seat_count": seat_count})
            # TODO: put the caching time limit in a setting.
            cache.add(section, section_item, 60*2)
        cart_items.append(section_item)
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
        conflicting_sections = conflict_resolution(cart_items, sections)
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

def get_calendar_data(request):
    import datetime
    current_date = datetime.date.today()
    difference = datetime.timedelta(minutes=5)
    sections = request.session['Cart']
    if sections != [] and sections != None:
        cart_items = get_section_data(sections)
        conflicting_sections = conflict_resolution(cart_items, sections)
    else:
        cart_items = []
    json_data = []
    for item in cart_items:
        item_course_data = item['course_data']
        item_section_data = item['section_data']
        item_meeting_data = item['meeting_data']
        for meeting in item_meeting_data:
            temp_section = (item_course_data.prefix + ' ' +
                            item_course_data.course_number +' ' +
                            item_section_data.section_number)
            temp_time = meeting.start_time
            while temp_time <= meeting.end_time:
                if 'm' in meeting.days_of_week:
                    meeting_day = 'Mo'
                    data = {'day':meeting_day, 'hour':temp_time.hour, 'minute':temp_time.minute, 'section':temp_section}
                    json_data.append(data)
                if 'tr' in meeting.days_of_week:
                    meeting_day = 'Th'
                    data = {'day':meeting_day, 'hour':temp_time.hour, 'minute':temp_time.minute, 'section':temp_section}
                    json_data.append(data)
                if 'w' in meeting.days_of_week:
                    meeting_day = 'We'
                    data = {'day':meeting_day, 'hour':temp_time.hour, 'minute':temp_time.minute, 'section':temp_section}
                    json_data.append(data)
                if 't' in meeting.days_of_week and not 'r' in meeting.days_of_week:
                    # TODO: Work with this.  Would have a problem if it meets on tuesday and thursday.
                    meeting_day = 'Tu'
                    data = {'day':meeting_day, 'hour':temp_time.hour, 'minute':temp_time.minute, 'section':temp_section}
                    json_data.append(data)
                if 'f' in meeting.days_of_week:
                    meeting_day = 'Fr'
                    data = {'day':meeting_day, 'hour':temp_time.hour, 'minute':temp_time.minute, 'section':temp_section}
                    json_data.append(data)
                if 'su' in meeting.days_of_week:
                    meeting_day = 'Su'
                    data = {'day':meeting_day, 'hour':temp_time.hour, 'minute':temp_time.minute, 'section':temp_section}
                    json_data.append(data)
                if 's' in meeting.days_of_week and not 'u' in meeting.days_of_week:
                    # TODO: Work with this.  Would have a problem if it meets on tuesday and thursday.
                    meeting_day = 'S'
                    data = {'day':meeting_day, 'hour':temp_time.hour, 'minute':temp_time.minute, 'section':temp_section}
                    json_data.append(data)
                # Take existing time and convert into datetime object.
                current_datetime = datetime.datetime(current_date.year,
                                      current_date.month, current_date.day,
                                      temp_time.hour, temp_time.minute,
                                      temp_time.second)
                # Increment time by 5 minutes.
                new_datetime = current_datetime + difference
                # Reset value of temp_time.
                temp_time = new_datetime.time()

    json_data = json.dumps(json_data, indent=2)
    return HttpResponse(json_data)

