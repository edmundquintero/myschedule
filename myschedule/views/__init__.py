#from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, redirect
from django.views.generic.simple import direct_to_template
from django.conf import settings
from django.http import HttpResponse
from cpsite import ods

import string
from datetime import datetime
import traceback
# from cpsite.decorators import groups_required

from myschedule import models, forms
from myschedule.views.cart import conflict_resolution

def index(request):
    """
        Handles processing for the index template.
    """
    return direct_to_template(request,
                              'myschedule/index.html')

def help(request):
    """
        Processes help link.
    """
    import os
    from django.conf import settings
    try:
        files = os.listdir(os.path.join(settings.APP_STATIC_MEDIA, 'help'))
    except OSError:
        files = None
    return direct_to_template(request, 'myschedule/help.html', {
        'files': files
    })

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
        course.add_count = course.add_count + 1
        course.save()

    # Get the sections currently in the cart (for displaying in sidebar)
    if request.session.has_key('Cart'):
        cart_items = models.Section.objects.filter(
			section_code__in=request.session['Cart'])
        conflicts = conflict_resolution(cart_items)
    else:
        cart_items = []
        conflicts = {}

    # Get the sections for the selected course
    sections = models.Section.objects.select_related().filter(course=course_id)

    return direct_to_template(request,
            'myschedule/section_results.html',
            {'sections':sections,
             'cart_items':cart_items,
             'conflicts':conflicts}
    )

def update_courses(request):
    """
        Receives and processes course data.
    """
    from django.utils import simplejson as json
    import base64

    status = 'Starting data load...\n'
    messages = ''

    if request.method == 'POST':
        try:
            # Use the raw post data so that it's not in the form of a django querydict
            # Read the post data first before attempting to check the authorization.
            # If a large amount of data is sent, the connection gets reset if try
            # to throw an error when checking authorization.
            post_data = request.raw_post_data

            if request.META.has_key('HTTP_AUTHORIZATION'):
                # Calling function needs to make sure to remove extraneous line
                # feed attached to encoded authorization string. Django does not
                # like it - post data will be messed up.

                authorization = request.META['HTTP_AUTHORIZATION']
                authorization = authorization.replace('Basic ','')
                credentials = base64.decodestring(authorization)
                credentials = credentials.split(':')
                # Compare the credentials passed in through the header to
                # those in the settings to verify calling application is
                # authorized
                if (credentials[0] != settings.DATA_CREDENTIALS[0] or
                        credentials[1] != settings.DATA_CREDENTIALS[1]):
                    raise ValueError("Invalid credentials")
            else:
                raise ValueError("Missing credentials")

        except:
            status = status + '\n' + traceback.format_exc()
        else:
            try:
                # Decode the data
                data = json.loads(post_data)
                received_count = len(data)
                if received_count == 0:
                    raise ValueError("No data received")

                # Drop temporary tables
                drop_temporary_tables()

                # Re-create temporary tables
                create_tables()

                # Load data into temporary tables
                messages, processed = load_temporary_tables(data)

                # Drop production section and meeting tables
                drop_production_tables()

                # Re-create production section and meeting tables
                create_tables()

                # Load data into production tables (copying over from temporary
                # tables)
                prod_processed = load_production_tables()

                # received_count, processed, and prod_processed should all be
                # the same
                if (received_count != processed or
                    received_count != prod_processed or
                    processed != prod_processed):
                    status = "%s\nReceived %s, processed into temp tables %s, processed into production tables %s" % (
                            status, received_count, processed, prod_processed)
            except:
                status = status + '\n' + traceback.format_exc()
    else:
        status = status + '\nInvalid request'

    if messages != '':
        status = status + '\n' + messages
    status = status + '\n...Ending data load'

    return HttpResponse(status, mimetype='text/plain')

def drop_temporary_tables():
    """
        Drops the temp tables - production tables won't be dropped
        until after data is loaded into temp tables.
    """
    from django.db import connection

    cursor = connection.cursor()
    cursor.execute("drop table myschedule_coursetemp")
    cursor.execute("drop table myschedule_sectiontemp")
    cursor.execute("drop table myschedule_meetingtemp")

    return

def drop_production_tables():
    """
        Drops the production section and meeting tables.
        The course table does not get dropped. Course records will
        be updated and new ones added.
    """
    from django.db import connection

    cursor = connection.cursor()
    cursor.execute("drop table myschedule_section")
    cursor.execute("drop table myschedule_meeting")

    return

def create_tables():
    """
        Calls syncdb to recreate dropped tables.
    """
    from django.core import management

    management.call_command('syncdb')

    return

def load_temporary_tables(data):
    messages = ''
    processed = 0
    for item in data:
        try:
            messages = "%s \n\n Course %s %s %s" % (messages,
                        item['course_code'], item['prefix'],
                        item['course_number'])
            course = models.CourseTemp(
                        course_code=item['course_code'],
                        prefix=item['prefix'],
                        course_number=item['course_number'],
                        title=item['title'],
                        description=item['description'],
                        academic_level=item['academic_level'],
                        department=item['department'],
                        note=item['note']
                    )
            course.save()
            if item['sectiontemp_set'] != []:
                for section in item['sectiontemp_set']:
                    new_section = models.SectionTemp(course=course,
                        section_code=section['section_code'],
                        section_number=section['section_number'],
                        term=section['term'],
                        year=section['year'],
                        campus=section['campus'],
                        synonym=section['synonym'],
                        start_date=datetime.strptime(section['start_date'], "%Y-%m-%d"),
                        end_date=datetime.strptime(section['end_date'], "%Y-%m-%d"),
                        contact_hours=section['contact_hours'],
                        credit_hours=section['credit_hours'],
                        ceus=section['ceus'],
                        tuition=section['tuition'],
                        delivery_type=section['delivery_type'],
                        note=section['note'],
                        book_link=section['book_link'],
                        session=section['session'],
                        status=section['status'],
                        instructor_name=section['instructor_name'],
                        instructor_link=section['instructor_link'])
                    new_section.save()
                    if section['meetingtemp_set'] != []:
                        for meeting in section['meetingtemp_set']:
                            new_meeting = models.MeetingTemp(section=new_section,
                                start_time=format_time(meeting['start_time']),
                                end_time=format_time(meeting['end_time']),
                                meeting_type=meeting['meeting_type'],
                                days_of_week=meeting['days_of_week'],
                                building=meeting['building'],
                                room=meeting['room'])
                            new_meeting.save()
            processed = processed + 1
        except Warning:
            # If a warning is triggered, it is most likely due to invalid
            # characters in the data (i.e. copyright symbol).
            messages = messages + '\n\n' + traceback.format_exc()

    return messages, processed

def load_production_tables():
    """
        Iterate through the latest data in the coursetemp model. If the course
        isn't in the course model, add it, otherwise update it. Add it's
        associated sections and meetings to the section and meeting models.
    """
    prod_processed = 0
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
        prod_processed = prod_processed + 1
    return prod_processed

def format_time(time_value):
    if time_value == "":
        time_value = "00:00"
    return datetime.strptime(time_value,"%H:%M")

def update_seats(request):
    """
        Receives and processes data containing current seat count and
        statuses for course sections.
    """
    from django.utils import simplejson as json
    import base64

    status = 'Starting data load...\n'
    messages = ''

    if request.method == 'POST':
        try:
            # Use the raw post data so that it's not in the form of a django querydict
            # Read the post data first before attempting to check the authorization.
            # If a large amount of data is sent, the connection gets reset if try
            # to throw an error when checking authorization.
            post_data = request.raw_post_data

            if request.META.has_key('HTTP_AUTHORIZATION'):
                # Calling function needs to make sure to remove extraneous line
                # feed attached to encoded authorization string. Django does not
                # like it - post data will be messed up.

                authorization = request.META['HTTP_AUTHORIZATION']
                authorization = authorization.replace('Basic ','')
                credentials = base64.decodestring(authorization)
                credentials = credentials.split(':')
                # Compare the credentials passed in through the header to
                # those in the settings to verify calling application is
                # authorized
                if (credentials[0] != settings.DATA_CREDENTIALS[0] or
                        credentials[1] != settings.DATA_CREDENTIALS[1]):
                    raise ValueError("Invalid credentials")
            else:
                raise ValueError("Missing credentials")

        except:
            status = status + '\n' + traceback.format_exc()
        else:
            try:
                # Decode the data
                data = json.loads(post_data)
                received_count = len(data)
                if received_count == 0:
                    raise ValueError("No data received")

                # Load data into temporary tables
                messages, processed = load_seats(data)

                # received_count, processed, and prod_processed should all be
                # the same
                if (received_count != processed):
                    status = "%s\nReceived %s, processed into production tables %s" % (
                            status, received_count, processed)
            except:
                status = status + '\n' + traceback.format_exc()
    else:
        status = status + '\nInvalid request'

    if messages != '':
        status = status + '\n' + messages
    status = status + '\n\n...Ending data load'

    return HttpResponse(status, mimetype='text/plain')

def load_seats(data):
    messages = ''
    processed = 0
    for item in data:
        messages = "%s \n\n Section %s" % (messages, item['section_code'])
        try:
            section = models.Section.objects.get(section_code=item['section_code'])
            section.available_seats = item['available_seats']
            section.status = item['status']
            section.save()
            processed = processed + 1
        except models.Section.DoesNotExist:
            messages = '%s \n Section %s not found.' % (messages, item['section_code'])
        except:
            messages = messages + '\n\n' + traceback.format_exc()

    return messages, processed

def update_popularity(request):
    """
        Runs the update_popularity method against all courses to update
        popularity based on add_count.

        Update indexes after running this!
    """
    courses = models.Course.objects.all()
    for course in courses:
        course.update_popularity()
    return HttpResponse()
