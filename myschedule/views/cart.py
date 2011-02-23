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

from time import strftime

"""
    What is a cart?
    The cart represents the schedule that is currently being edited
    (having courses added and removed).
"""

@login_required
#@groups_required(['Students'])
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
    # Need course info to return to javascript and need to save
    # search data.
    course = get_object_or_404(models.Section, section_code=section)
    if request.session.has_key('current_query'):
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
    section_data = {'prefix': course.course.prefix,
                    'course_number': course.course.course_number,
                    'section_number': course.section_number,
                    'title': course.course.title}

    json_data = {'section_data':section_data, 'errors':errors}
    json_data = json.dumps(json_data, indent=2)
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

def get_conflicts(request):
    """
        Called from javascript to recheck conflicts.
    """
    sections = request.session['Cart']
    cart_items = models.Section.objects.filter(section_code__in=sections)
    conflicts = conflict_resolution(cart_items)
    json_data = {'conflicts':conflicts}
    json_data = json.dumps(json_data, indent=2)
    return HttpResponse(json_data)

def conflict_resolution(cart_items):
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
                                    commondays = "".join(filter(lambda x: x in item_meeting.days_of_week.upper(),
                                        test_meeting.days_of_week.upper()))
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
    conflicts = {}
    cart_items = []
    if not request.session.has_key('Cart') and sections_url == None:
        return redirect('index')
    elif not request.session.has_key('Cart') and sections_url != None:
        sections = sections_url.split("/")
        sections.remove('')
        request.session['Cart'] = sections
    # TODO: get all the other information regarding a course section that
    # needs to be displayed (still need seat count and actual contact hours)
    sections = request.session['Cart']

    if sections != [] and sections != None:
        cart_items = models.Section.objects.filter(
                section_code__in=sections).order_by('end_date','section_code')
        conflicts = conflict_resolution(cart_items)

    return direct_to_template(request,
                              'myschedule/display_cart.html',
                              {'cart_items':cart_items,
                               'conflicts':conflicts}
                             )

def email_schedule(request):
    """
        Called from javascript to email schedule to addressees passed from
        javascript.
    """
    from django.core.mail import send_mail
    from django.template import loader, Context

    errors = ''
    sections = []
    sections_url = ''
    try:
        email_addresses = request.POST['email_addresses']
        to_addressees = email_addresses.split(",")
        to_addressees.remove('')

        if 'Cart' in request.session:
            sections = request.session['Cart']
            for item in sections:
                sections_url = sections_url + item + '/'
            if sections != []:
                cart_items = models.Section.objects.filter(
                    section_code__in=sections).order_by('end_date','section_code')
                app_host = request.get_host()
                schedule_url = reverse('display_cart',args=[sections_url])
                schedule_url = "http://%s%s" % (app_host, schedule_url)
                text_template = loader.get_template('myschedule/email.txt')
                c = Context(dict({'schedule_url':schedule_url, 'cart_items':cart_items}))
                email_message = text_template.render(c)
                if email_message != "":
                    send_mail('CPCC schedule',
                        email_message,
                        "myschedule@cpcc.edu",
                        to_addressees,
                        auth_user=None,
                        auth_password=None)
            else:
                raise ValueError("No classes in schedule.")
    except Exception, e:
        errors = 'Received error "%s" when trying to send email.' % (e)

    json_data = {'errors':errors}
    json_data = json.dumps(json_data)
    # return JSON object to browser
    return HttpResponse(json_data)

def get_calendar_data(request):
    """
        Returns schedule data to calling javascript function which will use
        the data to update the calendar display.
    """
    json_data = {}
    temp_data = []
    conflicts = []
    cart_items = []
    if request.session.has_key('Cart'):
        sections = request.session['Cart']
        if sections != [] and sections != None:
            cart_items = models.Section.objects.filter(section_code__in=sections)
            conflicts = conflict_resolution(cart_items)
    for item in cart_items:
        for meeting in item.meeting_set.all():
            # start date and end date must be sent in the format m/d/Y so IE can
            # convert it to a date (of course the other browsers are not so
            # picky)
            temp_data.append({'section':item.section_code,
                              'weekdays':meeting.days_of_week.upper(),
                              'start_date':item.start_date.strftime("%m/%d/%Y"),
                              'end_date':item.end_date.strftime("%m/%d/%Y"),
                              'start_hour':meeting.start_time.hour,
                              'start_minute':meeting.start_time.minute,
                              'end_hour':meeting.end_time.hour,
                              'end_minute':meeting.end_time.minute}
                            )

    json_data = {"meetings":temp_data,"conflicts":conflicts}
    json_data = json.dumps(json_data, indent=2)

    return HttpResponse(json_data)

class SQSSearchView(SearchView):
    def extra_context(self):
        extra = super(SQSSearchView, self).extra_context()
        extra['spelling_suggestion'] = self.searchqueryset.spelling_suggestion()
        # Needs the cart_items to display in sidebar and the conflicts so
        # know if need to display a warning message to user.
        if self.request.session.has_key('Cart'):
            cart_items = models.Section.objects.filter(
                section_code__in=self.request.session['Cart']).order_by(
                'end_date','section_code')
            conflicts = conflict_resolution(cart_items)
        else:
            cart_items = []
            conflicts = {}
        extra['cart_items'] = cart_items
        extra['conflicts'] = conflicts
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

