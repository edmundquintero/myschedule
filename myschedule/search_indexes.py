from haystack.indexes import *
from haystack import site
from myschedule import models

class CourseIndex(SearchIndex):
    text = CharField(document=True, use_template=True)
    prefix = CharField(model_attr='prefix')
    course_number = CharField(model_attr='prefix')
    title = CharField(model_attr='title')
    description = CharField(model_attr='description')
    popularity = CharField(model_attr='popularity')

    def get_queryset(self):
        return models.Course.objects.all()


site.register(models.Course, CourseIndex)
