from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.generic.simple import direct_to_template
from django.conf import settings
from django.utils import simplejson as json
from haystack.views import SearchView

from cpsite import ods
from cpsite.decorators import groups_required

from myschedule import models, forms

"""
    What is a cart?
    The cart represents the schedule that is currently being edited
    (having courses added and removed).
"""

@login_required
@groups_required(['Students'])
def schedule_login(request, next):
    """
        Instead of sign in links calling login, pass the user through here
        so can save a schedule they were working on before they signed in and
        can check for an existing saved schedule.
    """
    if request.user.is_authenticated():
        # First check to see if the user already has a saved schedule in the table.
        # If they have a saved schedule and have a cart, then will need to
        # reconcile the two.
        saved_sections = []
        try:
            cart = models.Schedule.objects.get(owner=request.user)
            saved_sections = cart.sections.split("/")
            saved_sections.remove('')
        except:
            pass
        if not request.session.has_key('Cart') and saved_sections:
            # Just need to create the cart session variable and load it.
            request.session['Cart'] = saved_sections
        elif request.session.has_key('Cart'):
            cart_sections = request.session['Cart']
            if saved_sections:
                # Compare previously saved items to the cart. Add any
                # saved items that aren't already in it to the cart.
                # Possible TODO: check to see if the section is still active
                # before adding it to the cart.
                for item in saved_sections:
                    if item not in cart_sections:
                        cart_sections.append(item)
            # Update the cart session variable
            request.session['Cart'] = cart_sections
            save_cart(request)
    return redirect(next)

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
        course = get_object_or_404(models.Section, section_code=section)
        course = course.course
        correlation = models.Correlation()
        correlation.criterion = request.session['current_query']
        if request.session.has_key('previous_query'):
            if request.session['previous_query'] not in settings.BLACKLIST:
                correlation.species = models.Correlation.WRONG_TERM
                correlation.criterion = correlation.criterion + '|' + request.session['previous_query']
            del request.session['previous_query']
            del request.session['current_query']
            request.session.modified = True
        else:
            correlation.species = models.Correlation.SUCCESSFUL_SEARCH
        correlation.course = course
        correlation.save()
        course.add_count = course.add_count + 1
        course.save()

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

def delete_cartitem(request):
    """
        Deletes the specified course section from the cart.
    """
    section = request.POST['section']
    if request.session.has_key('Cart'):
        sections = request.session['Cart']
        sections.remove(section)
        request.session['Cart'] = sections
        if request.user.is_authenticated():
            save_cart(request)
    return HttpResponse()

def conflict_resolution(cart_items, sections):
    """
        Checks for any conflicts between the sections on the schedule.
        Presently, just for classes with overlapping times.
        TODO: Check section status??
    """
    conflicting_sections = []
    conflicted_meetings = []
    for section in sections:
        test_section = get_object_or_404(models.Section,
                                         section_code=section)
        test_meetings = test_section.meeting_set.all()
        for item in cart_items:
            section_data = item['section_data']
            meeting_data = item['meeting_data']
            if test_section.section_code != section_data.section_code:
                cs_sections = []
                for section_code in conflicting_sections:
                    cs_sections.append(section_code['section_code'])
                if test_section not in cs_sections:
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
                                            conflicted_meetings.append(comparison_meeting.id)

                        if len(conflicted_meetings)>0:
                            conflicting_sections.append({"section_code":test_section.section_code,
                                                     "conflicted_meetings":conflicted_meetings})
    return conflicting_sections

def get_conflicts(request):
    sections = request.session['Cart']
    cart_items = models.Section.objects.filter(section_code__in=sections)
    conflicts = conflict_resolution_new(cart_items)
    json_data = {'conflicts':conflicts}
    json_data = json.dumps(json_data, indent=2)
    return HttpResponse(json_data)

def conflict_resolution_new(cart_items):
    """
        Checks for any conflicts between the sections on the schedule.
        Presently, just for classes with overlapping times.
        TODO: Check section status??
    """
    conflicting_sections = []
    conflicting_meetings = []
    test_items = cart_items
    for item in cart_items:
        if item.section_code not in conflicting_sections:
            for test_item in test_items:
                if test_item.section_code != item.section_code:
                    if ((test_item.start_date <= item.start_date and
                         item.start_date <= test_item.end_date) or
                        (test_item.start_date <= item.end_date and
                         item.end_date <= test_item.end_date) or
                        (item.start_date <= test_item.start_date and
                         test_item.start_date <= item.end_date) or
                        (item.start_date <= test_item.end_date and
                         test_item.end_date <= item.end_date)):
                        # the sections start / end dates have some overlap so
                        # continue checking for potential conflict
                        item_meetings = item.meeting_set.all()
                        test_meetings = test_item.meeting_set.all()
                        for item_meeting in item_meetings:
                            for test_meeting in test_meetings:
                                if item_meeting.id != test_meeting.id and item_meeting.id not in conflicting_meetings:
                                    # Check to see if the meetings have any days in common
                                    commondays = "".join(filter(lambda x: x in item_meeting.days_of_week,
                                        test_meeting.days_of_week))
                                    if commondays:
                                        # Check to see if the meeting times overlap
                                        if ((test_meeting.start_time <= item_meeting.start_time and
                                             item_meeting.start_time <= test_meeting.end_time) or
                                            (test_meeting.start_time <= item_meeting.end_time and
                                            item_meeting.end_time <= test_meeting.end_time) or
                                            (item_meeting.start_time <= test_meeting.end_time and
                                            test_meeting.start_time <= item_meeting.end_time) or
                                            (item_meeting.start_time <= test_meeting.end_time and
                                            test_meeting.end_time <= item_meeting.end_time)):
                                                conflicting_meetings.append(item_meeting.id)
                                                if item.section_code not in conflicting_sections:
                                                    conflicting_sections.append(item.section_code)
    conflicts = dict({"conflicting_sections":conflicting_sections,
                      "conflicting_meetings":conflicting_meetings})
    return conflicts

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

def get_section_data(sections, include_seats=True):
    """
        Get the section, course, and meeting data for a list of sections.
        Will optionally get the seat count information.
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
            section_item = dict({"section_data":section_data,
                            "course_data":course_data,
                            "meeting_data":meeting_data})
            cache.add(section, section_item, 60*settings.CACHE_REFRESH_RATE)
        else:
            section_data = section_item['section_data']
            course_data = section_item['course_data']
        seat_counts = []
        # Seat count data isn't cached in this application (may be cached
        # externally).
        if include_seats:
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
        section_item['seat_count'] = seat_count
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
    elif request.user.is_authenticated():
        try:
            cart = models.Schedule.objects.get(owner=request.user)
            sections_url = cart.sections
        except:
            return redirect('index')
    return redirect('display_cart', sections_url)

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
        cart_items = models.Section.objects.filter(section_code__in=sections)
        conflicts = conflict_resolution_new(cart_items)
    else:
        cart_items = []

    search = forms.search_form()

    return direct_to_template(request,
                              'myschedule/display_cart.html',
                              {'cart_items':cart_items,
                               'conflicts':conflicts,
                               'search':search}
                             )

def email_schedule(request):
    """
        Processes javascript request to email schedule.
    """
    from django.core.mail import send_mail
    from datetime import date
    from time import strftime
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
    cart_items = models.Section.objects.filter(section_code__in=sections)
    app_host = request.get_host()
    schedule_url = reverse('display_cart',args=[sections_url])
    email_message = "View this schedule online at http://%s%s.\n\n" % (app_host, schedule_url)
    for item in cart_items:
        message = (
            "%s %s - %s %s \n" % (item.course.prefix,
                                  item.course.course_number,
                                  item.section_number,
                                  item.course.title) +
            "Synonym: %s \n" % (item.synonym) +
            "Instructor: %s \n" % (item.instructor_name) +
            "Meets: %s \n" % (item.campus))
        for meeting in item.meeting_set.all():
            message = message + (
                "       %s - %s %s   %s %s - %s \n" % (
                meeting.meeting_type,
                meeting.building,
                meeting.room,
                meeting.days_of_week.upper().replace('R','Th').replace('U','Su'),
                meeting.start_time.strftime("%I:%M %p"),
                meeting.end_time.strftime("%I:%M %p"))
            )
        message = message + (
            "View book information at %s. \n" % (item.book_link)
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
    sections = []
    if request.session.has_key('Cart'):
        sections = request.session['Cart']
    if sections != [] and sections != None:
        cart_items = models.Section.objects.filter(section_code__in=sections)
        conflicting_sections = conflict_resolution_new(cart_items)
    else:
        cart_items = []
    json_data = []
    for item in cart_items:
        meeting_data = item.meeting_set.all()
        for meeting in meeting_data:
            temp_section = (item.course.prefix + ' ' +
                            item.course.course_number +' ' +
                            item.section_number)
            temp_time = meeting.start_time
            while temp_time <= meeting.end_time:
                if 'm' in meeting.days_of_week:
                    meeting_day = 'Mo'
                    data = {'day':meeting_day, 'hour':temp_time.hour, 'minute':temp_time.minute, 'section':temp_section}
                    json_data.append(data)
                if 't' in meeting.days_of_week:
                    meeting_day = 'Tu'
                    data = {'day':meeting_day, 'hour':temp_time.hour, 'minute':temp_time.minute, 'section':temp_section}
                    json_data.append(data)
                if 'w' in meeting.days_of_week:
                    meeting_day = 'We'
                    data = {'day':meeting_day, 'hour':temp_time.hour, 'minute':temp_time.minute, 'section':temp_section}
                    json_data.append(data)
                if 'r' in meeting.days_of_week:
                    meeting_day = 'Th'
                    data = {'day':meeting_day, 'hour':temp_time.hour, 'minute':temp_time.minute, 'section':temp_section}
                    json_data.append(data)
                if 'f' in meeting.days_of_week:
                    meeting_day = 'Fr'
                    data = {'day':meeting_day, 'hour':temp_time.hour, 'minute':temp_time.minute, 'section':temp_section}
                    json_data.append(data)
                if 's' in meeting.days_of_week:
                    meeting_day = 'Sa'
                    data = {'day':meeting_day, 'hour':temp_time.hour, 'minute':temp_time.minute, 'section':temp_section}
                    json_data.append(data)
                if 'u' in meeting.days_of_week:
                    meeting_day = 'Su'
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
    

class SQSSearchView(SearchView):
    def extra_context(self):
        extra = super(SQSSearchView, self).extra_context()
        extra['spelling_suggestion'] = self.searchqueryset.spelling_suggestion()
        return extra
    
    def __call__(self, request):
        if 'q' in request.GET:
            if 'current_query' in request.session:
                if request.session['current_query'] == request.GET['q'].lower():
                    return super(SQSSearchView, self).__call__(request)
                request.session['previous_query'] = request.session['current_query'].lower()
            request.session['current_query'] = request.GET['q'].lower()
            request.session.modified = True
        return super(SQSSearchView, self).__call__(request)

def delete_this_before_production(request, id):
    if request.session.has_key('current_query'):
        course = get_object_or_404(models.Course, id=id)
        correlation = models.Correlation()
        correlation.criterion = request.session['current_query']
        if request.session.has_key('previous_query'):
            if request.session['previous_query'] not in settings.BLACKLIST:
                correlation.species = models.Correlation.WRONG_TERM
                correlation.criterion = correlation.criterion + '|' + request.session['previous_query']
            del request.session['previous_query']    
        else:
            correlation.species = models.Correlation.SUCCESSFUL_SEARCH
        del request.session['current_query']
        request.session.modified = True
        correlation.course = course
        correlation.save()
        course.add_count = str(int(course.add_count) + 1)
        course.save()
        words = 'Good Jorb! Add Count for %s: %s' % (course.title, course.add_count)
        return HttpResponse('Good Jorb! Add Count for %s: %s\nCorrelation: criterion - %s / species - %s' % (course.title, course.add_count, correlation.criterion, correlation.species))
    else:
        return HttpResponse('Well, that didn\'t work')
