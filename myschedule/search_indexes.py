from haystack.indexes import *
from haystack import site
from myschedule import models
from django.template import defaultfilters

class CourseIndex(SearchIndex):
    """
	Sort fields need to be defined as type string in solr schema.xml.
        Hence the reason for duplicating the course_number and title fields.
        If build_solr_schema is used to re-generate the schema.xml file,
        make sure to manually change the type for course_number_sort and
        title_sort from type text to type string.  If you don't, sorting
        by title will not work (index out of bounds error from solr)
        and sorting by course number will be incorrect.
    """
    text = CharField(document=True, use_template=True)
    primary_key = CharField(model_attr='pk')
    prefix = CharField(model_attr='prefix')
    course_number = CharField(model_attr='course_number')
    course_number_sort = CharField(model_attr='course_number')
    title = CharField(model_attr='title')
    title_sort = CharField(model_attr='title')
    description = CharField(model_attr='description')
    campuses = MultiValueField()
    delivery_types = MultiValueField()
    start_dates = MultiValueField()
    end_dates = MultiValueField()
    popularity = CharField(model_attr='popularity')
    
    def prepare_campuses(self, obj):
        return [section.campus for section in obj.section_set.all()]
    def prepare_delivery_types(self, obj):
        return [section.delivery_type for section in obj.section_set.all()]
    def prepare_start_dates(self, obj):
        return [section.start_date for section in obj.section_set.all()]
    def prepare_end_dates(self, obj):
        return [section.end_date for section in obj.section_set.all()]
    def get_queryset(self):
        return models.Course.objects.all()


site.register(models.Course, CourseIndex)
