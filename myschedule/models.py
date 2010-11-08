from django.db import models
from django.contrib.auth.models import User

class Schedule(models.Model):
    """
        Stores the user's saved schedules. Sections is a url parameter containing
        the sections for the schedule.
    """

    owner = models.ForeignKey(User, blank=True, null=True)
    description = models.CharField(max_length=50,
                help_text='Brief description that identifies this schedule.')
    sections = models.CharField(max_length=300)
    def __unicode__(self):
        return self.description


class Course(models.Model):
    """Course information, preformulated in the API"""
    course_code = models.CharField(max_length=10, blank=False)
    prefix = models.CharField(max_length=10, blank=False)
    course_number = models.CharField(max_length=10, blank=False)
    title = models.TextField(max_length=1000, blank=False)
    description = models.TextField(max_length=4000, blank=False)
    academic_level = models.CharField(max_length=255, blank=False)
    credit_type = models.CharField(max_length=255, blank=False)
    credit_hours = models.CharField(max_length=10, blank=False)
    contact_hours = models.CharField(max_length=10, blank=False)
    department = models.CharField(max_length=255, blank=False)
    note = models.TextField(max_length=1000, blank=False)


class Section(models.Model):
    """Section specific information, preformulated in the API"""
    course = models.ForeignKey(Course)
    section_code = models.CharField(max_length=10, blank=False)
    section_number = models.CharField(max_length=10, blank=False)
    term = models.CharField(max_length=4, blank=False)
    year = models.CharField(max_length=4, blank=False)
    campus = models.CharField(max_length=100, blank=False)
    synonym = models.CharField(max_length=10, blank=False)
    start_date = models.DateField(blank=False)
    end_date = models.DateField(blank=False)
    credit_hours = models.CharField(max_length=10, blank=False)
    ceus = models.CharField(max_length=10, blank=False)
    tuition = models.CharField(max_length=10, blank=False)
    delivery_type = models.CharField(max_length=255, blank=False)
    note = models.TextField(max_length=7000, blank=False)
    book_link = models.CharField(max_length=255, blank=False)
    session = models.CharField(max_length=255, blank=False)
    status = models.CharField(max_length=255, blank=False)
    instructor_name = models.CharField(max_length=510, blank=False)
    instructor_link = models.CharField(max_length=255, blank=False)


class Meeting(models.Model):
    """Meeting specific information, related to a Section, preformulated in the API"""
    section = models.ForeignKey(Section, blank=False)
    start_time = models.DateTimeField(blank=False)
    end_time = models.DateTimeField(blank=False)
    meeting_type = models.CharField(max_length=255, blank=False)
    days_of_week = models.CharField(max_length=15, blank=False)
    building = models.CharField(max_length=10, blank=False)
    room = models.CharField(max_length=10, blank=False)