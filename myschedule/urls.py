# from django.conf import settings
from django.conf.urls.defaults import include, patterns, url
# from django.contrib import admin

from myschedule import views, cart

# admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^display_cart/((?:\w{3}-[\d\w]+-[\d\w]+-\w{2}-\d{4}/?)+)*$', cart.display_cart, name='display_cart'),
    url(r'^delete_cartitem/(\w{3}-[\d\w]+-[\d\w]+-\w{2}-\d{4})/$', cart.delete_cartitem, name='delete_cartitem'),
    url(r'^show_courses/', views.show_courses, name='show_courses'),
    url(r'^show_sections/(\w{3})/([\d\w]+)/([\w]+)/$', views.show_sections, name='show_sections'),
    url(r'^show_schedule/', cart.show_schedule, name='show_schedule'),
    url(r'^save_schedule/', cart.save_schedule, name='save_schedule'),
    url(r'^delete_schedule/([\d]+)/$', cart.delete_schedule, name='delete_schedule'),
    url(r'^search/$', views.search, name='search'),
    url(r'^search/([\w ]*)/$', views.search, name='search'),
    url(r'^cart/add/$', cart.add_item, name='add_item'),
    url(r'^cart/get/$', cart.get_cart, name='get_cart'),
    url(r'^cart/set/$', cart.set_cart, name='set_cart'),
    url(r'^cart/save/$', cart.save_cart, name='save_cart'),
    url(r'^schedule/email/$', cart.email_schedule, name='email_schedule'),
    # url(r'^admin/', include(admin.site.urls)),
)

# if settings.DEBUG:
#     urlpatterns += patterns('',
#         url(r'^media/(?P<path>.*)$', 'django.views.static.serve',
#             {'document_root': settings.MEDIA_ROOT}, name='media'),
#     )
