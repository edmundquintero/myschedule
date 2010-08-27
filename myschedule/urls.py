# from django.conf import settings
from django.conf.urls.defaults import include, patterns, url
# from django.contrib import admin

from myschedule import views, cart

# admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^display_cart/', cart.display_cart, name='display_cart'),
    url(r'^delete_cartitem/(\d+)/$', cart.delete_cartitem, name='delete_cartitem'),
    url(r'^show_course_results/', views.show_course_results, name='show_course_results'),
    url(r'^show_section_results/(\w{3})/([\d\w]+)/$', views.show_section_results, name='show_section_results'),
    # url(r'^admin/', include(admin.site.urls)),
)

# if settings.DEBUG:
#     urlpatterns += patterns('',
#         url(r'^media/(?P<path>.*)$', 'django.views.static.serve',
#             {'document_root': settings.MEDIA_ROOT}, name='media'),
#     )
