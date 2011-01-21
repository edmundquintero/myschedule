from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

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


class CourseAbstract(models.Model):
    """
        Abstract model for courses.  Table is not created for this
        model - it is inherited by Course and CourseTemp models.
    """
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
    note = models.TextField(max_length=1000, blank=True)

    class Meta:
        abstract = True

    def __unicode__(self):
        return self.title


class Course(CourseAbstract):
    """
        Course information, preformulated in the API
    """
    HIGH = 'a'
    MEDIUM = 'm'
    LOW = 'z'
    POPULARITY_CHOICES = (
        (HIGH, 'High'),
        (MEDIUM, 'Medium'),
        (LOW, 'Low'),
    )
    add_count = models.CharField(max_length=10, blank=False, default='0')
    popularity = models.CharField(max_length=1, blank=False, default=LOW, choices=POPULARITY_CHOICES)

    def update_popularity(self):
        if self.add_count > settings.HIGH_THRESHOLD:
            self.popularity = Course.HIGH
        elif self.add_count > settings.MEDIUM_THRESHOLD:
            self.popularity = Course.MEDIUM
        else:
            self.popularity = Course.LOW
        self.save()

    def correlation_slug(self):
        correlations = self.correlation_set.all()
        slug = ''
        if correlations.count() > settings.CRITERION_THRESHOLD:
            for correlation in correlations:
                slug = slug + ' ' + correlation.easy_view()
        return slug


class CourseTemp(CourseAbstract):
    """
        Creates a temporary table to hold course records retrieved
        by the courseupdate api.
    """
    pass


class SectionAbstract(models.Model):
    """
        Abstract model for sections.  Table is not created for this
        model - it is inherited by Section and SectionTemp models.
    """

    section_code = models.CharField(max_length=25, blank=False)
    section_number = models.CharField(max_length=10, blank=False)
    term = models.CharField(max_length=4, blank=False)
    year = models.CharField(max_length=4, blank=False)
    campus = models.CharField(max_length=100, blank=False)
    synonym = models.CharField(max_length=10, blank=False)
    start_date = models.DateField(blank=False)
    end_date = models.DateField(blank=False)
    credit_hours = models.CharField(max_length=10, blank=False)
    ceus = models.CharField(max_length=10, blank=True)
    tuition = models.CharField(max_length=10, blank=False)
    delivery_type = models.CharField(max_length=255, blank=False)
    note = models.TextField(max_length=7000, blank=True)
    book_link = models.CharField(max_length=255, blank=False)
    session = models.CharField(max_length=255, blank=False)
    status = models.CharField(max_length=255, blank=False)
    instructor_name = models.CharField(max_length=510, blank=True)
    instructor_link = models.CharField(max_length=255, blank=True)

    class Meta:
        abstract = True

    def __unicode__(self):
        return self.section_code


class Section(SectionAbstract):
    """
        Section specific information, preformulated in the API
    """
    course = models.ForeignKey(Course)
    pass


class SectionTemp(SectionAbstract):
    """
        Creates a temporary table to hold section records retrieved by the
        courseupdate api.
    """
    course = models.ForeignKey(CourseTemp)
    pass


class MeetingAbstract(models.Model):
    """
        Abstract model for meetings.  Table is not created for this
        model - it is inherited by Meeting and MeetingTemp models.
    """

    start_time = models.TimeField(blank=False)
    end_time = models.TimeField(blank=False)
    meeting_type = models.CharField(max_length=255, blank=False)
    days_of_week = models.CharField(max_length=15, blank=False)
    building = models.CharField(max_length=10, blank=True)
    room = models.CharField(max_length=10, blank=True)

    class Meta:
        abstract = True


class Meeting(MeetingAbstract):
    """
        Meeting specific information, related to a Section, preformulated in the API
    """
    section = models.ForeignKey(Section, blank=False)
    pass


class MeetingTemp(MeetingAbstract):
    """
        Creates a temporary table to hold meeting records retrieved by the
        courseupdate api.
    """
    section = models.ForeignKey(SectionTemp, blank=False)
    pass


class Correlation(models.Model):
    SUCCESSFUL_SEARCH = 'ss' # Searched one time, found the course
    WRONG_TERM = 'wt' # Could be mispelling, abbr., related term not found in the text
    SPECIES_CHOICES = (
        (SUCCESSFUL_SEARCH, 'Successful one time search'),
        (WRONG_TERM, 'Wrong/Corrected query term'),
    )
    species = models.CharField(max_length=20, blank=False, choices=SPECIES_CHOICES)
    criterion = models.TextField(max_length=1000, blank=True)
    course = models.ForeignKey(Course, blank=False)

    def __unicode__(self):
        return self.criterion

    def easy_view(self):
        if self.species == Correlation.WRONG_TERM:
            criterion = self.criterion.split('|')[1]
        elif self.species == Correlation.SUCCESSFUL_SEARCH:
            criterion = self.criterion.split('|')[0]
        return criterion
