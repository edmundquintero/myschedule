from django.conf.urls.defaults import *
from piston.resource import Resource
from myschedule.api.handlers import MyScheduleHandler

myschedule_handler = Resource(MyScheduleHandler)

urlpatterns = patterns('',
   url(r'^seats/(?P<section_code>(\w{3}-[\d\w]+-[\d\w]+-\w{2}-\d{4}))/(?P<available_seats>[\d]+)/(?P<status>[\w/]+)/', myschedule_handler),
   url(r'^seats/(?P<section_code>(\w{3}-[\d\w]+-[\d\w]+-\w{2}-\d{4}))/', myschedule_handler),
)
