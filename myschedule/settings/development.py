from myschedule.settings.base import *

DEBUG = TEMPLATE_DEBUG = True

DATABASES = {
    'default': {
        "ENGINE": "mysql",
        "NAME": "myschedule",
        "USER": "myschedule",
        "PASSWORD": "myschedule",
    }
}

# In development, use the database for sessions, and disable caching.
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
# Enabled caching - if you don't have memcached installed, switch to locmem.
# CACHE_BACKEND = 'locmem://'
# CACHE_BACKEND = 'memcached://127.0.0.1:11211/'
# Specify cache refresh rate in minutes (view will convert to seconds)
#CACHE_REFRESH_RATE = 2

# MEDIA_ROOT = j(app_root, 'media')
# MEDIA_URL = APP_NAME + '/media/'

CPAPI_URL_FORMAT = 'http://te409-05.cpcc.edu:5025/cpapi/?%s'
#CPAPI_URL_FORMAT = 'http://pas1-central.cpcc.edu/cpapi/?%s'
CPAPI_KEY = "myschedule_key"

DATA_CREDENTIALS = ['testuser', 'testpass']

HAYSTACK_SITECONF = 'myschedule.search_sites'
HAYSTACK_SEARCH_ENGINE = 'solr'
# Change me before running update_index or rebuild_index
HAYSTACK_SOLR_URL = 'http://te409-05.cpcc.edu:8983/solr'
HAYSTACK_INCLUDE_SPELLING = True

# The following parameters are used to establish the connection to schedule2webadvisor
# and submit the user's schedule to their preferred list in webadvisor.
S2W_KEY_LOCATION = '/home/sje0388e/projects/django/myschedule/.ssh/privkey'
S2W_USER_AT_SERVER = 'snap2webadvisor@cis.cpcc.edu'
S2W_KNOWNHOSTS = '/home/sje0388e/projects/django/myschedule/.ssh/knownhosts'
S2W_SEPARATOR = '}'
S2W_RETURN_VALUES = ['Success', 'Empty Arguments' , 'already registered', 'valid student', 'Academic Level']
#S2W_DATATEL_URL = 'https://watest-central.cpcc.edu/WADEV/WADEV'
S2W_DATATEL_URL = 'http://mycollege.cpcc.edu/WATESTHR/WATESTHR'
#S2W_DATATEL_URL = 'http://mycollege.cpcc.edu'
# When finished testing, set S2W_TEST_SECTIONS to empty string
S2W_TEST_SECTIONS = '70359}69664'
# S2W_TEST_SECTIONS = ''
S2W_UNAVAILABLE_BEGIN = '03:00:00'
S2W_UNAVAILABLE_END = '07:30:00'
DOWNTIME_MESSAGE = 'Class registration is unavailable between 3:00AM and 7:30AM.'
