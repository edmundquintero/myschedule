from django.conf.urls.defaults import *
from piston.resource import Resource
from myschedule.api.handlers import MyScheduleHandler, TestHandler

myschedule_handler = Resource(MyScheduleHandler)
test_handler = Resource(TestHandler)

urlpatterns = patterns('',
   url(r'^courseupdate/', myschedule_handler),
   url(r'^getcourses/', test_handler),
)
