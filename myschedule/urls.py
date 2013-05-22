# from django.conf import settings
from django.conf.urls.defaults import include, patterns, url
# from django.contrib import admin
from myschedule.views.cart import SQSSearchView
from haystack.query import SearchQuerySet
from myschedule import models
from myschedule.forms import FilterSearchForm

# admin.autodiscover()
sqs = SearchQuerySet()

urlpatterns = patterns('myschedule.views',
    url(r'^$', 'index', name='index'),
    url(r'^help/$', 'help', name='help'),
    url(r'^courseapi/', 'cart.courseAPI', name='haystack_course_api'),
    url(r'^search/', SQSSearchView(load_all=False, searchqueryset=sqs, form_class=FilterSearchForm), name='haystack_search'),
    url(r'^sectionsapi/([\w]+)/$', 'sectionsAPI', name='sectionsapi'),
    url(r'^show_sections/([\w]+)/$', 'show_sections', name='show_sections'),
    url(r'^update_courses/', 'update_courses', name='update_courses'),
    url(r'^update_seats/', 'update_seats', name='update_seats'),
    url(r'^map/$', 'show_map', name='show_map'),
    # url(r'^admin/', include(admin.site.urls)),
)

urlpatterns += patterns('myschedule.views.cart',
    url(r'^display_cart/((?:\w{3}-[\d\w]+-[\d\w]+-\w{2}-\d{4}/?)+)*$', 'display_cart', name='display_cart'),
    url(r'^display_cart/', 'display_cart', name='display_cart'),
    url(r'^schedule/delete/$', 'delete_cartitem', name='delete_cartitem'),
    url(r'^show_schedule/', 'show_schedule', name='show_schedule'),
    url(r'^cart/add/$', 'add_item', name='add_item'),
    url(r'^schedule/register/', 'register', name='register'),
    url(r'^schedule/email/$', 'email_schedule', name='email_schedule'),
    url(r'^schedule/calendar/$', 'get_calendar_data', name='get_calendar_data'),
    url(r'^schedule/conflicts/$', 'get_conflicts', name='get_conflicts'),
    url(r'^schedule_login/$', 'schedule_login', name='schedule_login'),
    url(r'^schedule/terms/$', 'get_terms', name='get_terms'),
)

# if settings.DEBUG:
#     urlpatterns += patterns('',
#         url(r'^media/(?P<path>.*)$', 'django.views.static.serve',
#             {'document_root': settings.MEDIA_ROOT}, name='media'),
#     )
