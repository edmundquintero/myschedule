from haystack.indexes import *
from haystack import site
from myschedule import models
from django.template import defaultfilters

class CourseIndex(SearchIndex):
    text = CharField(document=True, use_template=True)
    primary_key = CharField(model_attr='pk')
    prefix = CharField(model_attr='prefix')
    course_number = CharField(model_attr='course_number')
    title = CharField(model_attr='title')
    title_slug = CharField(model_attr='title')
    description = CharField(model_attr='description')
    campuses = MultiValueField()
    delivery_types = MultiValueField()
    start_dates = MultiValueField()
    end_dates = MultiValueField()
    popularity = CharField(model_attr='popularity')
    
    def prepare_title_slug(self, obj):
        return "%s" %  defaultfilters.slugify(obj.title)
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
