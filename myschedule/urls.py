# from django.conf import settings
from django.conf.urls.defaults import include, patterns, url
# from django.contrib import admin
from haystack.views import SearchView
from haystack.query import SearchQuerySet

# admin.autodiscover()
sqs = SearchQuerySet().order_by('popularity')
urlpatterns = patterns('',
    url(r'^api/', include('myschedule.api.urls')),
)

urlpatterns += patterns('myschedule.views',
    url(r'^$', 'index', name='index'),
    url(r'^search/', SearchView(load_all=False, searchqueryset=sqs), name='haystack_search'),
    url(r'^old_search/', 'old_search', name='old_search'),
    url(r'^old_search/([\w ]*)/$', 'old_search', name='old_search'),
    url(r'^show_courses/', 'show_courses', name='show_courses'),
    url(r'^show_sections/(\w{3})/([\d\w]+)/([\w]+)/$', 'show_sections', name='show_sections'),
    url(r'^update_courses/', 'update_courses', name='update_courses'),
    # url(r'^admin/', include(admin.site.urls)),
)

urlpatterns += patterns('myschedule.views.cart',
    url(r'^display_cart/', 'display_cart', name='display_cart'),
    url(r'^display_cart/((?:\w{3}-[\d\w]+-[\d\w]+-\w{2}-\d{4}/?)+)*$', 'display_cart', name='display_cart'),
    url(r'^delete_cartitem/(\w{3}-[\d\w]+-[\d\w]+-\w{2}-\d{4})/$', 'delete_cartitem', name='delete_cartitem'),
    url(r'^show_schedule/', 'show_schedule', name='show_schedule'),
    url(r'^cart/add/$', 'add_item', name='add_item'),
    url(r'^schedule/email/$', 'email_schedule', name='email_schedule'),
    url(r'^schedule/calendar/$', 'get_calendar_data', name='get_calendar_data'),
    url(r'^schedule_login/([\w/]+)/$', 'schedule_login', name='schedule_login'),
)

# if settings.DEBUG:
#     urlpatterns += patterns('',
#         url(r'^media/(?P<path>.*)$', 'django.views.static.serve',
#             {'document_root': settings.MEDIA_ROOT}, name='media'),
#     )
