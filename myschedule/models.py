from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

from time import strftime

class Schedule(models.Model):
    """
        Stores the user's saved schedules. Sections is a url parameter containing
        the sections for the schedule.
    """

    owner = models.ForeignKey(User)
    description = models.CharField(max_length=50,
                help_text='Brief description that identifies this schedule.')
    sections = models.CharField(max_length=300, blank=True)

    def __unicode__(self):
        return "%s" % self.owner.username


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
    department = models.CharField(max_length=255, blank=False)
    note = models.TextField(max_length=1000, blank=True)
    prerequisites = models.CharField(max_length=100, blank=True)
    corequisites = models.CharField(max_length=100, blank=True)

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
    add_count = models.IntegerField(default=0)
    popularity = models.CharField(max_length=1, blank=False, default=LOW, choices=POPULARITY_CHOICES)

    def _get_prerequisites(self):
        """
            Returns a list of dictionaries containing prerequisite course objects.
        """
        course_codes = self.prerequisites.split(',')
        prerequisite_courses = []
        for course_code in course_codes:
            try:
                prereq_course = Course.objects.select_related().get(course_code=course_code)
                prereq = {'course_code':course_code,
                          'prereq_course':prereq_course}
                prerequisite_courses.append(prereq)
            except:
                pass
        return prerequisite_courses
    prerequisite_courses = property(_get_prerequisites)

    def _get_corequisites(self):
        """
            Returns a list of dictionaries containing corequisite course objects.
        """
        course_codes = self.corequisites.split(',')
        corequisite_courses = []
        for course_code in course_codes:
            try:
                coreq_course = Course.objects.select_related().get(course_code=course_code)
                coreq = {'course_code':course_code,
                         'coreq_course':coreq_course}
                corequisite_courses.append(coreq)
            except:
                pass
        return corequisite_courses
    corequisite_courses = property(_get_corequisites)

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

    def boost(self, species, weight, primary_criterion, secondary_criterion=None):
        if int(weight) > 0:
            correlation = Correlation()
            correlation.course = self
            correlation.criterion = primary_criterion
            if species in Correlation.SPECIES_CHOICES:
                if species == Correlation.WRONG_TERM:
                    if secondary_criterion:
                        correlation.species = species
                    else:
                        correlation.species = Correlation.SUCCESSFUL_SEARCH
                else:
                    correlation.species = species
            else:
                if secondary_criterion:
                    correlation.species = Correlation.WRONG_TERM
                else:
                    correlation.species = Correlation.SUCCESSFUL_SEARCH
            if secondary_criterion:
                correlation.criterion = correlation.criterion + '|' + secondary_criterion
            correlation.save()
            weight = int(weight)
            while weight > 0:
                correlation.clone()
                weight = weight - 1
        self.add_count = self.add_count + weight
        self.save()


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
    section_colleague_id = models.CharField(max_length=10, blank=False)
    term = models.CharField(max_length=4, blank=False)
    year = models.CharField(max_length=4, blank=False)
    campus = models.CharField(max_length=100, blank=False)
    synonym = models.CharField(max_length=10, blank=False)
    start_date = models.DateField(blank=False)
    end_date = models.DateField(blank=False)
    contact_hours = models.CharField(max_length=10, blank=False)
    credit_hours = models.CharField(max_length=10, blank=False)
    ceus = models.CharField(max_length=10, blank=True)
    tuition = models.CharField(max_length=10, blank=False)
    delivery_type = models.CharField(max_length=255, blank=False)
    note = models.TextField(max_length=7000, blank=True)
    book_link = models.CharField(max_length=510, blank=False)
    session = models.CharField(max_length=255, blank=False)
    status = models.CharField(max_length=255, blank=False)
    instructor_name = models.CharField(max_length=510, blank=True)
    instructor_link = models.CharField(max_length=255, blank=True)
    available_seats = models.IntegerField(blank=True, null=True)

    class Meta:
        abstract = True

    def __unicode__(self):
        return self.section_code


class Section(SectionAbstract):
    """
        Section specific information, preformulated in the API
    """
    course = models.ForeignKey(Course)

    def is_online(self):
        """
            Returns True if all meetings soociated with this section are online.
            Will be used in section template to display Online for the campus
            instead of Other Off Campus Location.
        """
        is_online = True
        meetings = Meeting.objects.filter(section=self.id)
        for meeting in meetings:
           if meeting.is_online() == False:
              is_online = False
        return is_online


class SectionTemp(SectionAbstract):
    """
        Creates a temporary table to hold section records retrieved by the
        courseupdate api.
    """
    course = models.ForeignKey(CourseTemp)


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

    def is_online(self):
        if (self.start_time.strftime("%H:%M:%S") == '00:00:00' and
                self.end_time.strftime("%H:%M:%S") == '00:00:00'):
            return True
        return False


class MeetingTemp(MeetingAbstract):
    """
        Creates a temporary table to hold meeting records retrieved by the
        courseupdate api.
    """
    section = models.ForeignKey(SectionTemp, blank=False)


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

    def clone(self):
        clone = Correlation()
        clone.species = self.species
        clone.criterion = self.criterion
        clone.course = self.course
        clone.save()
        return clone
