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

def schedule_login(request):
    """
        This view handles some post login processing.
        Saves a schedule the user was working on before they signed in and
        can check for an existing saved schedule.
    """
    section_count = 0
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
                for item in saved_sections:
                    if item not in cart_sections:
                        if len(cart_sections) < 14:
                            cart_sections.append(item)
            # Update the cart session variable
            request.session['Cart'] = cart_sections
            save_cart(request)
        if request.session.has_key('Cart'):
            section_count = models.Section.objects.filter(section_code__in=request.session['Cart']).count()
    # Return the user back to the page they were on prior to signing in unless
    # they were on the index page. If they signed in on the index page and had
    # a previously saved schedule (with current course sections), they will
    # get redirected to the show_schedule view so they can see their schedule.
    if request.session.has_key('next_view'):
        if request.session['next_view'] == '/myschedule/' and section_count > 0:
            next = '/myschedule/show_schedule/'
        else:
            next = request.session['next_view']
    else:
        next = '/myschedule/'
    return redirect(next)

def get_terms(request):
    """
        Called from javascript to get term start and end dates
        for selected term.
    """
    json_data = {'start_date':'', 'end_date':''}
    try:
        filter_term = request.POST['term']
        for term in settings.AVAILABLE_TERMS:
            if term['display_term'] == filter_term:
                json_data = {'start_date':term['start_date'],
                         'end_date':term['end_date']}
                break
    except:
        pass
    json_data = json.dumps(json_data, indent=2)
    return HttpResponse(json_data)

def add_item(request):
    """
        Adds the selected course section to the cart session variable.
    """
    section_data = {}
    if request.POST.has_key('section'):
        section = request.POST['section']
        errors = ''
        sections = []
        if request.session.has_key('Cart'):
            sections = request.session['Cart']
        if section not in sections:
            if len(sections) >= 14:
                # Due to the limitation imposed by the field size, limit the number of sections added to the schedule.
                section_data = {}
                errors = "The maximum allowed sections have been added to your schedule.  Additional sections cannot be added unless other sections are first removed."
            else:
                sections.append(section)
                request.session['Cart'] = sections
                if request.user.is_authenticated():
                    save_cart(request)
                # Need course info to return to javascript and need to save
                # search data.
                course = get_object_or_404(models.Section, section_code=section)
                section_data = {'prefix': course.course.prefix,
                                'course_number': course.course.course_number,
                                'section_number': course.section_number,
                                'title': course.course.title}
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
    else:
        errors = "The application was unable to add this section to your schedule.  Reload the page and try again.  If the problem persists, please contact the help desk."
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
        try:
            # See if a schedule already exists for this user.
            cart = models.Schedule.objects.get(owner=request.user)
            cart.sections = sections_url
        except models.Schedule.DoesNotExist:
            cart = models.Schedule(owner=request.user,
                       sections=sections_url)
        finally:
            cart.save()
    return errors

def delete_cartitem(request):
    """
        Deletes the specified course section from the cart.
    """
    # Note the subtle difference between the two messages below ("your"/"the")
    json_data = {'message':'completed'}
    if request.POST.has_key('section'):
        section = request.POST['section']
        if request.session.has_key('Cart'):
            sections = request.session['Cart']
            if section in sections:
                sections.remove(section)
            request.session['Cart'] = sections
            if request.user.is_authenticated():
                save_cart(request)
        else:
            json_data = {'message':'This section may not have been removed from your schedule. Reload the page and try removing the section again.  Contact the help desk if the problem persists.'}
    else:
        json_data = {'message':'This section may not have been removed from the schedule. Reload the page and try removing the section again. Contact the help desk if the problem persists.'}
    json_data = json.dumps(json_data, indent=2)
    return HttpResponse(json_data)

def get_conflicts(request):
    """
        Called from javascript to recheck conflicts.
    """
    cart_items = []
    if request.session.has_key('Cart'):
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

def show_schedule(request):
    """
        Processes selection of view full schedule button.
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
    request.session['next_view'] = request.path
    return redirect('display_cart', sections_url)

def display_cart(request, sections_url=None):
    """
        Displays shopping cart template (schedule).
    """
    from datetime import datetime

    conflicts = {}
    cart_items = []
    if not request.session.has_key('Cart') and sections_url == None:
        return redirect('index')
    elif not request.session.has_key('Cart') and sections_url != None:
        sections = sections_url.split("/")
        if '' in sections:
            sections.remove('')
        request.session['Cart'] = sections
    sections = request.session['Cart']

    if sections != [] and sections != None:
        cart_items = models.Section.objects.filter(
                section_code__in=sections).order_by('end_date','section_code')
        conflicts = conflict_resolution(cart_items)

    downtime_message = ''
    if (settings.S2W_UNAVAILABLE_BEGIN != '' and settings.S2W_UNAVAILABLE_END != ''):
        current_time = datetime.now()
        downtime_begin = datetime.strptime(settings.S2W_UNAVAILABLE_BEGIN,'%H:%M:%S')
        downtime_end = datetime.strptime(settings.S2W_UNAVAILABLE_END,'%H:%M:%S')
        if (current_time.time() >= downtime_begin.time() and
            current_time.time() <= downtime_end.time()):
            downtime_message = settings.S2W_DOWNTIME_MESSAGE

    request.session['next_view'] = '/myschedule/show_schedule/'

    # Initialize the search form.
    current_time = datetime.now()
    initial_values = {
        'campus':'all',
        'delivery_method':'all',
        'academic_level':'all',
        'start_date':current_time.date().strftime("%m/%d/%Y")}
    current_time = datetime.now()
    request.session['sort_order'] = ''
    search_form = forms.FilterSearchForm(initial=initial_values)
    return direct_to_template(request,
                              'myschedule/display_cart.html',
                              {'cart_items':cart_items,
                               'conflicts':conflicts,
                               's2w_datatel_url':settings.S2W_DATATEL_URL,
                               'downtime_message':downtime_message,
                               's2w_success_message':settings.S2W_SUCCESS_MESSAGE,
                               'allow_feedback':settings.ALLOW_FEEDBACK,
                               'form': search_form,
                               'filters_set':filter_check(request)}
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
            # Start date and end date must be sent in the format m/d/Y so IE can
            # convert it to a date (of course the other browsers are not so
            # picky).
            # The fancy math on the start minute and end minute are to ensure
            # all the times are rounded to the nearest 5 minute increment
            # (rounds down) since the calendar is laid out in five minute
            # increments. Some classes seem  to have peculiar start and end
            # times.
            temp_data.append({'section':item.section_code,
                              'weekdays':meeting.days_of_week.upper(),
                              'start_date':item.start_date.strftime("%m/%d/%Y"),
                              'end_date':item.end_date.strftime("%m/%d/%Y"),
                              'start_hour':meeting.start_time.hour,
                              'start_minute':round(meeting.start_time.minute/5)*5,
                              'end_hour':meeting.end_time.hour,
                              'end_minute':round(meeting.end_time.minute/5)*5}
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
        extra['catalog_url'] = settings.CATALOG_URL
        extra['filters_set'] = filter_check(self.request)
        return extra

    def get_results(self):
        """
           Replaces django haystack SearchView.getresults(). Do not subclass with
           searchqueryset = super(SQSSearchView, self).get_results(), because it
           does not allow the query (q) to be blank.  If the q is blank, we want it
           to return all courses.  It was only making the call to self.form.search()
           if a value for q was specified.
        """
        if self.form.is_valid():
            searchqueryset = self.form.search()
            if searchqueryset != []:
                if 'sort_order' in self.request.GET:
                    if self.request.GET['sort_order'] == 'prefix':
                        searchqueryset = searchqueryset.order_by('prefix','course_number_sort')
                    elif self.request.GET['sort_order'] == 'title':
                        searchqueryset = searchqueryset.order_by('title_sort')
            return searchqueryset
        return []

    def __call__(self, request):
        if 'q' in request.GET:
            try:
                if 'all_courses' in request.GET:
                    request.session['all_courses'] = request.GET['all_courses']
                else:
                    request.session['all_courses'] = ''
                if 'sort_order' in request.GET:
                    request.session['sort_order'] = request.GET['sort_order']
                else:
                    request.session['sort_order'] = ''
                request.session['campus_filter'] = request.GET['campus']
                request.session['delivery_method_filter'] = request.GET['delivery_method']
                request.session['academic_level'] = request.GET['academic_level']
                request.session['start_date_filter'] = request.GET['start_date']
                request.session['end_date_filter'] = request.GET['end_date']
            except:
                pass
            if 'current_query' in request.session:
                if request.session['current_query'] == request.GET['q'].lower():
                    return super(SQSSearchView, self).__call__(request)
                request.session['previous_query'] = request.session['current_query'].lower()
            request.session['current_query'] = request.GET['q'].lower()
            # Also save current query in q_value session variable for use in
            # initializing value in search box on non-course search results
            # pages. Can't use current_query for that purpose as it gets
            # deleted later. 
            request.session['q_value'] = request.GET['q'].lower()
            request.session.modified = True

        request.session['next_view'] = request.get_full_path()
        return super(SQSSearchView, self).__call__(request)

def register(request):
    """
        Called from javascript to submit the student's schedule to datatel.

        The display_cart template does not show the option to begin registration
        unless the user is authenticated and in the students group.
    """
    from schedule2webadvisor import WebAdvisorCreator
    from datetime import datetime

    status = 'error'
    errors = ''
    # Get their colleague ID.
    student = []
    student_id = ''
    try:
        ods_spec_dict = {"key": settings.CPAPI_KEY,
                         "data": "student",
                         "username": request.user.username}
        student = ods.get_data(ods_spec_dict)
        if student is None or len(student) == 0:
            errors = "Unable to retrieve student information. "
        else:
            student_id = student['colleague']
    except:
        errors = "An error occurred while retrieving student data. "

    # Verify registration is open.
    if (errors == '' and settings.S2W_UNAVAILABLE_BEGIN != ''
        and settings.S2W_UNAVAILABLE_END != ''):
        current_time = datetime.now()
        downtime_begin = datetime.strptime(settings.S2W_UNAVAILABLE_BEGIN,'%H:%M:%S')
        downtime_end = datetime.strptime(settings.S2W_UNAVAILABLE_END,'%H:%M:%S')
        if (current_time.time() >= downtime_begin.time() and
            current_time.time() <= downtime_end.time()):
            errors = settings.S2W_DOWNTIME_MESSAGE

    # Compose the string of sections to send to datatel (sending section
    # colleague IDs)
    if errors == '':
        sections_to_register = ''
        conflicts = []
        cart_items = []
        # separator will be the separator required by datatel (plan to place this in settings)
        separator = settings.S2W_SEPARATOR
        if request.session.has_key('Cart'):
            sections = request.session['Cart']
            if sections != [] and sections != None:
                cart_items = models.Section.objects.filter(section_code__in=sections,status='Active')
                #conflicts = conflict_resolution(cart_items)
        if cart_items != []:
            for item in cart_items:
                if sections_to_register != '':
                    sections_to_register = sections_to_register + separator
                sections_to_register= sections_to_register + item.section_colleague_id
        else:
            errors = ("No sections were found. Cannot submit schedule.")
    # If there are test sections specified in settings, override value of sections_to_register.
    if settings.S2W_TEST_SECTIONS != '':
        sections_to_register = settings.S2W_TEST_SECTIONS

    # Submit the user's schedule to their preferred list in datatel.
    if errors == '':
        web_ad = WebAdvisorCreator()
        output = web_ad(student_id, sections_to_register)
        output_list = output.split('\n')
        message = ''
        possible_return_values = settings.S2W_RETURN_VALUES
        for return_value in possible_return_values:
            for item in output_list:
                if return_value in item:
                    message = item
                    break
            if message != '':
                break
        if message == '':
            message = settings.S2W_FAILURE_MESSAGE
        if 'Success' not in message:
            errors = message
        else:
            status = 'ok'
    # Return the data to the calling javascript function.
    json_data = {'errors':errors, 'status':status}
    json_data = json.dumps(json_data)
    # return JSON object to browser
    return HttpResponse(json_data)

def filter_check(request):
    """
       Checks to see if any search filters, sorting, etc. were applied
    """
    try:
        if ((request.session.has_key('campus_filter') and request.session['campus_filter'] != 'all') or
            (request.session.has_key('delivery_method_filter') and request.session['delivery_method_filter'] != 'all') or
            (request.session.has_key('academic_level') and request.session['academic_level'] != 'all') or
            (request.session.has_key('start_date_filter') and request.session['start_date_filter'] != '') or
            (request.session.has_key('end_date_filter') and request.session['end_date_filter'] != '') or
            (request.session.has_key('all_courses') and request.session['all_courses'] == 'on') or
            (request.session.has_key('sort_order') and request.session['sort_order'] != '')):
            return True
    except:
        pass
    return False


