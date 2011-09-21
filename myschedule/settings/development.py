from myschedule.settings.base import *

DEBUG = TEMPLATE_DEBUG = True

# In development, use the database for sessions, and disable caching.
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
# Enabled caching - if you don't have memcached installed, switch to locmem.
# CACHE_BACKEND = 'locmem://'
# CACHE_BACKEND = 'memcached://127.0.0.1:11211/'
# Specify cache refresh rate in minutes (view will convert to seconds)
#CACHE_REFRESH_RATE = 2

# MEDIA_ROOT = j(app_root, 'media')
# MEDIA_URL = APP_NAME + '/media/'

CPAPI_URL_FORMAT = 'http://te410-02.cpcc.edu:5025/cpapi/?%s'
CPAPI_KEY = "myschedule_key"

DATA_CREDENTIALS = ['testuser', 'testpass']

# Change me before running update_index or rebuild_index
HAYSTACK_SOLR_URL = 'http://te410-02.cpcc.edu:8983/solr'

S2W_KEY_LOCATION = '/home/sje0388e/projects/django/myschedule/.ssh/privkey'
S2W_KNOWNHOSTS = '/home/sje0388e/projects/django/myschedule/.ssh/knownhosts'
#S2W_DATATEL_URL = 'https://watest-central.cpcc.edu/WADEV/WADEV'
S2W_DATATEL_URL = 'http://mycollege.cpcc.edu/WATESTHR/WATESTHR'
#S2W_DATATEL_URL = 'http://mycollege.cpcc.edu'
# When finished testing, set S2W_TEST_SECTIONS to empty string
S2W_TEST_SECTIONS = '70359}69664'

AUTH_IP_FOR_COURSE_UPDATE = ['10.9.4.25','10.9.4.56']
AUTH_KEY_FOR_COURSE_UPDATE = 'test_key'
AUTH_IP_FOR_SEAT_UPDATE = ['10.9.4.25','10.9.4.56']
AUTH_KEY_FOR_SEAT_UPDATE = 'test_key'
