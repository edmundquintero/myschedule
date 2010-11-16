from django.conf.urls.defaults import *
from piston.resource import Resource
from myschedule.api.handlers import MyScheduleHandler

myschedule_handler = Resource(MyScheduleHandler)

urlpatterns = patterns('',
   url(r'^courseupdate/', myschedule_handler),
)
