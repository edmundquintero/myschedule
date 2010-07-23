# from django.conf import settings
from django.conf.urls.defaults import include, patterns, url
# from django.contrib import admin

from myschedule import views

# admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    # url(r'^admin/', include(admin.site.urls)),
)

# if settings.DEBUG:
#     urlpatterns += patterns('',
#         url(r'^media/(?P<path>.*)$', 'django.views.static.serve',
#             {'document_root': settings.MEDIA_ROOT}, name='media'),
#     )
