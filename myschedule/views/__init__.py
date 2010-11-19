#from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, redirect
from django.views.generic.simple import direct_to_template
from django.conf import settings

from cpsite import ods

import string

# from cpsite.decorators import groups_required

from myschedule import models, forms

def index(request):
    """
        Handles processing for the index template.
    """
    saved_schedules = get_schedules(request)
    search = forms.search_form()
    return direct_to_template(request,
                              'myschedule/index.html',
                              {'search':search})

def get_schedules(request):
    """
        Retrieves a list of the user's saved schedules (if they're logged in).
    """
    saved_schedules = []
    if not request.user.is_anonymous():
        saved_schedules = models.Schedule.objects.filter(
                                owner__username = request.user)
        request.session['SavedSchedules'] = saved_schedules
    return saved_schedules

def search(request, search_text=None):
    """
        Handles processing for Search button and saved searches.
    """
    if search_text is None:
        if request.method == 'POST':
            search_text = request.POST['search_text']
    searches = []
    if 'RecentSearches' in request.session:
        searches = request.session['RecentSearches']
    if search_text not in searches and search_text != None:
        searches.append(search_text)
        request.session['RecentSearches'] = searches
    # TODO: perform the search!
    return redirect('show_courses')

def compose_booklink(campus=None, term=None, year=None, course_prefix=None,
                     course_number=None, section=None):
    """
        Composes a link to the textbook publisher's web service.
    """
    store_campus_mapping = settings.BOOKLOOK_STORE_CAMPUS_MAPPING
    store_id = ''
    if campus != '' and campus != None:
        store_id = settings.BOOKLOOK_DEFAULT_STORE
        if campus in store_campus_mapping:
            store_id = store_campus_mapping[campus]
    if term.lower() in settings.BOOKLOOK_TERMS:
        term = settings.BOOKLOOK_TERMS[term.lower()]
    else:
        term = ''
    booklink=''
    if (store_id != '' and term != '' and year != '' and year != None
                and course_prefix != '' and course_prefix != None
                and course_number != '' and course_number != None):
        booklink = (''+settings.BOOKLOOK_URL +
                    '?sect-1=' + section +
                    '&bookstore_id-1=' + store_id +
                    '&dept-1=' + course_prefix +
                    '&course-1=' + course_number +
                    '&term_id-1=' + term + ' ' + year)
    return booklink

def show_courses(request):
    """
        Displays course search results template.
    """
    saved_schedules = get_schedules(request)
    # TODO: For now we'll just grab all mat courses via cpapi so we'll have
    # some courses to display.
    ods_spec_dict = {"key": settings.CPAPI_KEY,
                     "data": "course",
                     "prefix": 'MAT'}
    courses = ods.get_data(ods_spec_dict)
    active_courses = []
    for course in courses:
        if course.has_key('status') and string.upper(course['status'])=='AB':
            # TODO: Update this with actual seat availability.
            course['information']='Sections with seats remaining'
            active_courses.append(course)
    active_courses.sort(key=lambda c: (c['prefix'], c['number']))
    search = forms.search_form()
    return direct_to_template(request,
            'myschedule/course_results.html',
            {'courses':active_courses,
             'search':search}
    )


def show_sections(request, prefix, number, course_id):
    """
        Display section results template for specified course.
    """
    saved_schedules = get_schedules(request)
    # TODO: Can't retrieve a course or section records using course_id via
    # cpapi, so until this whole data thing gets figured out will have to
    # filter the lists to get the items for a particular course_id. Actually
    # can only filter the course - sections doesn't include the course ID.
    ods_spec_dict = {"key": settings.CPAPI_KEY,
                     "data": "course",
                     "prefix": prefix,
                     "number": number}
    courses = ods.get_data(ods_spec_dict)
    active_course = {}
    for course in courses:
        if course.has_key('id') and course['id'] == course_id:
            active_course = course
    # TODO: Get the section data
    ods_spec_dict = {"key": settings.CPAPI_KEY,
                     "data": "sections",
                     "prefix": prefix,
                     "number": number}

    sections = ods.get_data(ods_spec_dict)
    active_sections = []
    for section in sections:
        if string.upper(section['term'])=='FA' and section['year']=='2010':
            active_sections.append(section)
            # Get the link to the book information TODO: replace hard-coded campus code with proper field when cpapi is updated to return location
            section["booklink"] = compose_booklink('1013', section['term'],
                      section['year'], section['prefix'],
                      section['number'], section['section'])
            # TODO: When upgrade to django 1.2 can remove is_in_cart code and
            # just check in the template to see if the section is in the cart
            section['is_in_cart']=False
            if (request.session.has_key('WorkingCart')):
                if section['id'] in request.session['WorkingCart']:
                    section['is_in_cart']=True

    search = forms.search_form()

    return direct_to_template(request,
            'myschedule/section_results.html',
            {'course':active_course,
             'sections':active_sections,
             'search':search}
    )

def update_courses(request):
    """
        Calls the api to get current course data (includes sections and
        meetings) and uses that data to pass to the api that creates
        the records in the myschedule course, section, and meeting tables.
    """
    # TODO: Integration with ods api (since it doesn't exist yet, I'm just
    # reading existing data in the myschedule tables, deleting everything,
    # from the tables and reloading with the original data.
    # TODO: Error checking (here and in api)
    # TODO: Authentication
    # TODO: Return something useful
    import httplib

    from django.http import HttpResponse

    # Open the connection to the api that will provide the course data.
    conn = httplib.HTTPConnection(settings.ODS_API_HOST)

    # Retrieve the ods data (formatted as json).
    req = conn.request('GET','/myschedule/api/courseupdate/read')
    resp = conn.getresponse()  # expect resp.status=200
    data = resp.read()

    # Close the connect to the api.
    conn.close()

    # Open the connection to the myschedule api (has to be a different port
    # from where the app is running).
    conn = httplib.HTTPConnection(settings.MYSCHEDULE_API_HOST)

    # Empty the course, section, and meeting tables.
    req = conn.request('DELETE', '/myschedule/api/courseupdate/delete')
    resp = conn.getresponse()   # expect resp.status=204

    # Create the new data.
    headers = {'Content-type':'application/json'}
    req = conn.request('POST', '/myschedule/api/courseupdate/create', data, headers)
    resp = conn.getresponse()   # expect resp.status=201

    # Close the connection.
    conn.close()

    return HttpResponse('true')

