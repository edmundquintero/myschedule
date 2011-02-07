#from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, redirect
from django.views.generic.simple import direct_to_template
from django.conf import settings
from django.http import HttpResponse
from cpsite import ods

import string

# from cpsite.decorators import groups_required

from myschedule import models, forms

def index(request):
    """
        Handles processing for the index template.
    """
    search = forms.search_form({"query":"ex. math, bus 121, mec"})
    return direct_to_template(request,
                              'myschedule/index.html',
                              {'search':search})

def old_search(request, query=None):
    """
        Handles processing for Search button and saved searches.
    """
    if query is None:
        if request.method == 'POST':
            query = request.POST['query']

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
    if request.session.has_key('Cart'):
        cart_items = models.Section.objects.filter(
			section_code__in=request.session['Cart'])
    else:
	cart_items = []

    sections = models.Section.objects.select_related().filter(course__course_code=course_id, term='FA', year='2010')
    search = forms.search_form()

    return direct_to_template(request,
            'myschedule/section_results.html',
            {'sections':sections,
             'cart_items':cart_items,
             'search':search}
    )

def update_courses(request):
    """
        Calls the ods api to get current course data (includes sections and
        meetings) and passes that data to the api that creates the records
        in the myschedule course, section, and meeting temporary tables.
    """
    # TODO: Integration with ods api (since it doesn't exist yet, I'm just
    # reading existing data in the myschedule tables, deleting everything,
    # from the tables and reloading with the original data.
    # TODO: Error checking (here and in api)
    # TODO: Authentication
    # TODO: Return something useful
    import httplib

    from django.http import HttpResponse

    ## Drop temporary tables, section, and meeting tables.
    drop_tables()

    ## Recreate dropped tables.
    create_tables()

    ## Load data in temp tables
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

    # Empty the course, section, and meeting temp tables.
    #req = conn.request('DELETE', '/myschedule/api/courseupdate/delete')
    #resp = conn.getresponse()   # expect resp.status=204

    # Add the new data into the temp tables.
    headers = {'Content-type':'application/json'}
    req = conn.request('POST', '/myschedule/api/courseupdate/create', data, headers)
    resp = conn.getresponse()   # expect resp.status=201

    # Close the connection.
    conn.close()

    ## Update courses and create section and meeting records.
    load_courses(request)

    return HttpResponse('true')

def drop_tables():
    """
        Drops the temp tables and the section and meeting table.
        The course table does not get dropped. Course records will
        be updated and new ones added.
    """
    from django.db import connection
    cursor = connection.cursor()
    errors = ''
    try:
        cursor.execute("drop table myschedule_coursetemp")
        cursor.execute("drop table myschedule_sectiontemp")
        cursor.execute("drop table myschedule_meetingtemp")
        cursor.execute("drop table myschedule_section")
        cursor.execute("drop table myschedule_meeting")
    except:
        errors = 'An error occurred with the table drop.'
    return errors

def create_tables():
    """
        Calls syncdb to recreate dropped tables.
    """
    from django.core import management
    errors = ''
    try:
        management.call_command('syncdb')
    except:
        errors = 'An error occurred with the sync.'
    return errors

def load_courses():
    """
        Iterate through the latest data in the coursetemp model. If the course
        isn't in the course model, add it, otherwise update it. Add it's
        associated sections and meetings to the section and meeting models.
    """
    count=0
    tempcourses = models.CourseTemp.objects.select_related().all()
    for tempcourse in tempcourses:
        try:
            course = models.Course.objects.get(course_code = tempcourse.course_code)
        except models.Course.DoesNotExist:
            course = models.Course()

        course.course_code=tempcourse.course_code
        course.prefix=tempcourse.prefix
        course.course_number=tempcourse.course_number
        course.title=tempcourse.title
        course.description=tempcourse.description
        course.academic_level=tempcourse.academic_level
        course.credit_type=tempcourse.credit_type
        course.credit_hours=tempcourse.credit_hours
        course.contact_hours=tempcourse.contact_hours
        course.department=tempcourse.department
        course.note=tempcourse.note

        course.save()

        for tempsection in tempcourse.sectiontemp_set.all():
            section = models.Section(
                course=course,
                section_code=tempsection.section_code,
                section_number=tempsection.section_number,
                term=tempsection.term,
                year=tempsection.year,
                campus=tempsection.campus,
                synonym=tempsection.synonym,
                start_date=tempsection.start_date,
                end_date=tempsection.end_date,
                credit_hours=tempsection.credit_hours,
                ceus=tempsection.ceus,
                tuition=tempsection.tuition,
                delivery_type=tempsection.delivery_type,
                note=tempsection.note,
                book_link=tempsection.book_link,
                status=tempsection.status,
                instructor_name=tempsection.instructor_name,
                instructor_link=tempsection.instructor_link)
            section.save()
            for tempmeeting in tempsection.meetingtemp_set.all():
                meeting = models.Meeting(
                    section=section,
                    start_time=tempmeeting.start_time,
                    end_time=tempmeeting.end_time,
                    meeting_type=tempmeeting.meeting_type,
                    days_of_week=tempmeeting.days_of_week,
                    building=tempmeeting.building,
                    room=tempmeeting.room)
                meeting.save()
        count = count + 1
    return HttpResponse(str(count))


