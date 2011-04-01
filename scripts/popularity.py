import sys, os
sys.path.append('/opt/wsgi-apps')
os.environ['DJANGO_SETTINGS_MODULE'] = 'myschedule_settings'

from django.conf import settings
from myschedule.views import update_popularity

update_popularity()
