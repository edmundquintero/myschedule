from myschedule.settings.base import *

DEBUG = TEMPLATE_DEBUG = True

DATABASE_ENGINE = 'mysql'
DATABASE_NAME = 'myschedule'
DATABASE_USER = 'myschedule'
DATABASE_PASSWORD = 'myschedule'

# In development, use the database for sessions, and disable caching.
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
# Enabled caching - will be switching to memcached.
CACHE_BACKEND = 'locmem://'

# MEDIA_ROOT = j(app_root, 'media')
# MEDIA_URL = APP_NAME + '/media/'

CPAPI_URL_FORMAT = 'http://10.9.4.26:5025/cpapi/?%s'
#CPAPI_URL_FORMAT = 'http://pas1-central.cpcc.edu/cpapi/?%s'
CPAPI_KEY = "myschedule_key"
ODS_API_HOST = 'te409-05.cpcc.edu:8080'
MYSCHEDULE_API_HOST = 'te409-05.cpcc.edu:8080'

HAYSTACK_SITECONF = 'myschedule.search_sites'
HAYSTACK_SEARCH_ENGINE = 'whoosh'
HAYSTACK_WHOOSH_PATH = j(app_root, 'haystack_index')
