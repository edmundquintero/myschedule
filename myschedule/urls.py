# from django.conf import settings
from django.conf.urls.defaults import include, patterns, url
# from django.contrib import admin

#from myschedule import views, cart

# admin.autodiscover()

urlpatterns = patterns('myschedule.views',
    url(r'^$', 'index', name='index'),
    url(r'^search/$', 'search', name='search'),
    url(r'^search/([\w ]*)/$', 'search', name='search'),
    url(r'^show_courses/', 'show_courses', name='show_courses'),
    url(r'^show_sections/(\w{3})/([\d\w]+)/([\w]+)/$', 'show_sections', name='show_sections'),
    # url(r'^admin/', include(admin.site.urls)),
)

urlpatterns += patterns('myschedule.views.cart',
    url(r'^display_cart/((?:\w{3}-[\d\w]+-[\d\w]+-\w{2}-\d{4}/?)+)*$', 'display_cart', name='display_cart'),
    url(r'^delete_cartitem/(\w{3}-[\d\w]+-[\d\w]+-\w{2}-\d{4})/$', 'delete_cartitem', name='delete_cartitem'),
    url(r'^show_schedule/', 'show_schedule', name='show_schedule'),
    url(r'^delete_schedule/([\d]+)/$', 'delete_schedule', name='delete_schedule'),
    url(r'^cart/add/$', 'add_item', name='add_item'),
    url(r'^cart/get/$', 'get_cart', name='get_cart'),
    url(r'^cart/set/$', 'set_cart', name='set_cart'),
    url(r'^cart/save/$', 'save_cart', name='save_cart'),
    url(r'^schedule/email/$', 'email_schedule', name='email_schedule'),
)

# if settings.DEBUG:
#     urlpatterns += patterns('',
#         url(r'^media/(?P<path>.*)$', 'django.views.static.serve',
#             {'document_root': settings.MEDIA_ROOT}, name='media'),
#     )
