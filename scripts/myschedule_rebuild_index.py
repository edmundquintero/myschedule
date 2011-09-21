import sys, os
sys.path.append('/opt/wsgi-apps')
os.environ['DJANGO_SETTINGS_MODULE'] = 'myschedule_settings'

from django.conf import settings
from haystack.management.commands import rebuild_index

rebuild_index.Command().handle()
