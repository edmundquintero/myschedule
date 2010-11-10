from piston.handler import BaseHandler
from piston.utils import rc, validate

from myschedule.models import Course, Section, Meeting

class MyScheduleHandler(BaseHandler):
    model = Course
    #fields = ('title', 'content', ('comments', ('content',)))
    fields = ('course_code', 'prefix', 'course_number', 'title', 'description', 'academic_level', 'credit_type', 'credit_hours', 'contact_hours' , 'department', 'note')
    def create(self, request):
        if request.content_type:
            data = request.data

            course = self.model(
                course_code=data['course_code'],
                prefix=data['prefix'],
                course_number=data['course_number'],
                title=data['title'],
                description=data['description'],
                academic_level=data['academic_level'],
                credit_type=data['credit_type'],
                credit_hours=data['credit_hours'],
                contact_hours=data['contact_hours'],
                department=data['department'],
                note=data['note']
            )
            course.save()

            #for comment in data['comments']:
            #    Comment(parent=em, content=comment['content']).save()

            # section
            # meeting
            return rc.CREATED
        else:
            super(Course, self).create(request)

    def delete(self, request):
        # delete all existing records in the model
        self.model.objects.all.delete()

class TestHandler(BaseHandler):
    allowed_methods = ('GET',)
    fields = ('course_code', 'prefix', 'course_number', 'title', 'description', 'academic_level', 'credit_type', 'credit_hours', 'contact_hours' , 'department', 'note')
    model = Course

    def read(self, request):
        return self.model.objects.all()
