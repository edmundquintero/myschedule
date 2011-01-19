from myschedule.settings.base import *

DEBUG = TEMPLATE_DEBUG = True

DATABASE_ENGINE = 'mysql'
DATABASE_NAME = 'myschedule'
DATABASE_USER = 'myschedule'
DATABASE_PASSWORD = 'myschedule'

# In development, use the database for sessions, and disable caching.
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
# Enabled caching - if you don't have memcached installed, switch to locmem.
# CACHE_BACKEND = 'locmem://'
CACHE_BACKEND = 'memcached://127.0.0.1:11211/'
# Specify cache refresh rate in minutes (view will convert to seconds)
CACHE_REFRESH_RATE = 2

# MEDIA_ROOT = j(app_root, 'media')
# MEDIA_URL = APP_NAME + '/media/'

CPAPI_URL_FORMAT = 'http://10.9.4.26:5025/cpapi/?%s'
#CPAPI_URL_FORMAT = 'http://pas1-central.cpcc.edu/cpapi/?%s'
CPAPI_KEY = "myschedule_key"
ODS_API_HOST = 'te409-05.cpcc.edu:8080'
MYSCHEDULE_API_HOST = 'te409-05.cpcc.edu:8080'

HAYSTACK_SITECONF = 'myschedule.search_sites'
HAYSTACK_SEARCH_ENGINE = 'solr'
HAYSTACK_SOLR_URL = 'http://te409-04.cpcc.edu:8983/solr'
HAYSTACK_INCLUDE_SPELLING = True
HAYSTACK_WHOOSH_PATH = j(app_root, 'haystack_index')
