# from django.conf import settings
from django.conf.urls.defaults import include, patterns, url
# from django.contrib import admin

from myschedule import views, cart

# admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^display_cart/', cart.display_cart, name='display_cart'),
    url(r'^delete_cartitem/(\d+)/$', cart.delete_cartitem, name='delete_cartitem'),
    url(r'^show_courses/', views.show_courses, name='show_courses'),
    url(r'^show_sections/(\w{3})/([\d\w]+)/([\w]+)/$', views.show_sections, name='show_sections'),
    url(r'^query/((?:\w{3}-[\d\w]+-[\d\w]+-\w{2}-\d{4}/?)+)', views.query, name='query'),
    # url(r'^admin/', include(admin.site.urls)),
)

# if settings.DEBUG:
#     urlpatterns += patterns('',
#         url(r'^media/(?P<path>.*)$', 'django.views.static.serve',
#             {'document_root': settings.MEDIA_ROOT}, name='media'),
#     )
