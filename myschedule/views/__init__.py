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
    search = forms.search_form()
    return direct_to_template(request,
                              'myschedule/index.html',
                              {'search':search})

def old_search(request, search_text=None):
    """
        Handles processing for Search button and saved searches.
    """
    if search_text is None:
        if request.method == 'POST':
            search_text = request.POST['search_text']

    # TODO: perform the search!
    return redirect('show_courses')

def show_courses(request):
    """
        Displays course search results template.
    """
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

def show_sections(request, course_id):
    """
        Display section results template for specified course.
    """
    sections = models.Section.objects.filter(course__course_code=course_id, term='FA', year='2010')

    search = forms.search_form()

    return direct_to_template(request,
            'myschedule/section_results.html',
            {'sections':sections,
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

