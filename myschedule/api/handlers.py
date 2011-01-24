from datetime import datetime

from piston.handler import BaseHandler
from piston.utils import rc, validate

from myschedule.models import CourseTemp, SectionTemp, MeetingTemp

class MyScheduleHandler(BaseHandler):
    """
        Handler for reading, deleting and creating course and associated
        section and meeting data.

        In order for piston to traverse foreign key relationships, you must use
        the related name for the child.  Unless the related name is overridden
        in the model, it should be modelname_set.  So in the case of the
        section model, it is referred to as section_set.

        To test
        -------
        In the interactive shell (python appmanage.py shell) issue the
        following commands:
        from django.test import Client
        c=Client()
        temp1=c.get('/myschedule/api/courseupdate/read')
        temp2=c.delete('/myschedule/api/courseupdate/delete')
        temp3=c.post('/myschedule/api/courseupdate/create',temp1.content,content_type='application/json')

        Might need to eventually add piston to installed_apps in settings and
        run syncdb to create it's tables.  For now it's not needed (I think it
        may be needed if add in authorization support).
    """

    allowed_methods = ('GET', 'POST', 'DELETE',)
    fields = ('course_code',
              'prefix',
              'course_number',
              'title',
              'description',
              'academic_level',
              'credit_type',
              'credit_hours',
              'contact_hours',
              'department',
              'note',
              ('sectiontemp_set',
                ('section_code',
                 'section_number',
                 'term',
                 'year',
                 'campus',
                 'synonym',
                 'start_date',
                 'end_date',
                 'credit_hours',
                 'ceus',
                 'tuition',
                 'delivery_type',
                 'note',
                 'book_link',
                 'session',
                 'status',
                 'instructor_name',
                 'instructor_link',
                 ('meetingtemp_set',
                    ('start_time',
                     'end_time',
                     'meeting_type',
                     'days_of_week',
                     'building',
                     'room')
                 )
                )
              )
             )
    model = CourseTemp

    def read(self, request):
        """
            Returns all records in course model formatted as json (follows
            foreign key relationships and retrieves section and meeting
            data as well).
        """
        courses = self.model.objects.all()
        return courses

    def create(self, request):
        """
            Creates course records and associated section and meeting records
            based on json formatted data submitted via request.
        """
        if request.content_type:
            if request.data:
                data = request.data
                for item in data:
                    course = self.model(
                        course_code=item['course_code'],
                        prefix=item['prefix'],
                        course_number=item['course_number'],
                        title=item['title'],
                        description=item['description'],
                        academic_level=item['academic_level'],
                        credit_type=item['credit_type'],
                        credit_hours=item['credit_hours'],
                        contact_hours=item['contact_hours'],
                        department=item['department'],
                        note=item['note']
                    )
                    course.save()
                    if item['sectiontemp_set'] != []:
                        for section in item['section_set']:
                            new_section = SectionTemp(course=course,
                                section_code=section['section_code'],
                                section_number=section['section_number'],
                                term=section['term'],
                                year=section['year'],
                                campus=section['campus'],
                                synonym=section['synonym'],
                                start_date=section['start_date'],
                                end_date=section['end_date'],
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
                                for meeting in section['meeting_set']:
                                    new_meeting = MeetingTemp(section=new_section,
                                        start_time=datetime.strptime(meeting['start_time'],"%H:%M:%S"),
                                        end_time=datetime.strptime(meeting['end_time'],"%H:%M:%S"),
                                        meeting_type=meeting['meeting_type'],
                                        days_of_week=meeting['days_of_week'],
                                        building=meeting['building'],
                                        room=meeting['room'])
                                    new_meeting.save()
            # TODO: check value of rc.CREATED in loop and then handle appropriately when it is not equal to CREATED
            return rc.CREATED
        else:
            super(CourseTemp, self).create(request)

    def delete(self, request):
        """
            Deletes all existing records in the course, section, and meeting
            models.
        """
        courses = self.model.objects.all()
        courses.delete()
        return rc.DELETED

