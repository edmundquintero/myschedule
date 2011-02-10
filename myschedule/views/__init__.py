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
from myschedule.views.cart import conflict_resolution

def index(request):
    """
        Handles processing for the index template.
    """
    return direct_to_template(request,
                              'myschedule/index.html')

def show_sections(request, course_id):
    """
        Display section results template for specified course.
    """
    # Help make future searches smarter - save query and update course add_count.
    if request.session.has_key('current_query'):
        course = get_object_or_404(models.Course, id=course_id)
        correlation = models.Correlation()
        correlation.criterion = request.session['current_query']
        if request.session.has_key('previous_query'):
            if request.session['previous_query'] not in settings.BLACKLIST:
                correlation.species = models.Correlation.WRONG_TERM
                correlation.criterion = correlation.criterion + '|' + request.session['previous_query']
            del request.session['previous_query']
        else:
            correlation.species = models.Correlation.SUCCESSFUL_SEARCH
        # Store the value of the current query in another session variable that
        # be used to display the last query value in the search field on the
        # pages other than search. (Can't just not delete the current_query
        # session variable - unfortunate things will happen.)
        request.session['q_value'] = request.session['current_query']
        del request.session['current_query']
        request.session.modified = True
        correlation.course = course
        correlation.save()
        course.add_count = str(int(course.add_count) + 1)
        course.save()

    # Get the sections currently in the cart (for displaying in sidebar)
    if request.session.has_key('Cart'):
        cart_items = models.Section.objects.filter(
			section_code__in=request.session['Cart'])
        conflicts = conflict_resolution(cart_items)
    else:
        cart_items = []
        conflicts = {}

    # Get the sections for the selected course TODO: What to do about term and year???
    sections = models.Section.objects.select_related().filter(course=course_id)

    return direct_to_template(request,
            'myschedule/section_results.html',
            {'sections':sections,
             'cart_items':cart_items,
             'conflicts':conflicts}
    )

def update_courses(request):
    """
        Calls the ods api to get current course data (includes sections and
        meetings) and passes that data to the api that creates the records
        in the myschedule course, section, and meeting temporary tables.
    """
    # TODO: Error checking (here and in api)
    # TODO: Authentication??
    # TODO: Return something useful
    import httplib
    import urllib

    from django.http import HttpResponse

    ## Drop temporary tables, section, and meeting tables.
    drop_tables()

    ## Recreate dropped tables.
    create_tables()

    # Retrieve the ods data (formatted as json).
    req = urllib.urlopen(settings.ODS_API_URL)
    data = req.read()

    # Open the connection to the myschedule api (has to be a different port
    # from where the app is running).
    conn = httplib.HTTPConnection(settings.MYSCHEDULE_API_HOST)

    # Add the new data into the temp tables.
    headers = {'Content-type':'application/json'}
    req = conn.request('POST', '/myschedule/api/courseupdate/create', data, headers)
    resp = conn.getresponse()   # expect resp.status=201

    # Close the connection.
    conn.close()

    ## Update courses and create section and meeting records.
    load_courses()

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
                contact_hours=tempsection.contact_hours,
                credit_hours=tempsection.credit_hours,
                ceus=tempsection.ceus,
                tuition=tempsection.tuition,
                delivery_type=tempsection.delivery_type,
                note=tempsection.note,
                book_link=tempsection.book_link,
                session=tempsection.session,
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


