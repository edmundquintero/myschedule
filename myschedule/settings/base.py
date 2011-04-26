from cpsite.settings.base import *

INSTALLED_APPS.extend([
    # 'django.contrib.admin',
    'myschedule',
    'haystack',
])

app_root = d(d(__file__))
APP_STATIC_MEDIA = j(app_root, 'static')

LOGIN_URL = '/myschedule/login/'
CAS_REDIRECT_URL = '/myschedule/'
CAS_IGNORE_REFERER = False

APP_NAME = 'myschedule'
BASE_URL = APP_NAME + '/'

ADMINS.append(('Your Name', 'first.last@cpcc.edu'))

SESSION_COOKIE_NAME = 'myschedule_sessionid'

THEME = '3g'

DATABASES = {
    'default': {
        "ENGINE": "mysql",
        "NAME": "myschedule",
        "USER": "myschedule",
        "PASSWORD": "myschedule",
    }
}

HAYSTACK_SITECONF = 'myschedule.search_sites'
HAYSTACK_SEARCH_ENGINE = 'solr'
# Change haystack_solr_url before running update_index or rebuild_index
HAYSTACK_SOLR_URL = ''
HAYSTACK_INCLUDE_SPELLING = True
# Heuristic Search Data
HIGH_THRESHOLD = 1000
MEDIUM_THRESHOLD = 300
CRITERION_THRESHOLD = 10
HAYSTACK_SEARCH_RESULTS_PER_PAGE = 10
BLACKLIST = ['fuck', 'shit']

CPAPI_URL_FORMAT = 'http://pas1-central.cpcc.edu/cpapi/?%s'
CPAPI_KEY = ""

# data_credentials contains username and password expected to be received in
# header of bulk data push and seat count api
DATA_CREDENTIALS = []

CATALOG_URL = 'http://www.cpcc.edu/attending/catalog'

# The following parameters are used to establish the connection to schedule2webadvisor
# to submit the user's schedule to their preferred list in webadvisor.
S2W_KEY_LOCATION = ''
S2W_USER_AT_SERVER = 'snap2webadvisor@cis.cpcc.edu'
S2W_KNOWNHOSTS = ''
S2W_SEPARATOR = '}'
S2W_RETURN_VALUES = ['Success', 'Empty Arguments' , 'already registered', 'valid student', 'Academic Level']
S2W_DATATEL_URL = 'http://mycollege.cpcc.edu'
# When finished testing, set S2W_TEST_SECTIONS to empty string
S2W_TEST_SECTIONS = ''
# s2w_unavailable_begin and end time should both be empty string if there
# is no downtime for webadvisor (24 hour time format otherwise)
S2W_UNAVAILABLE_BEGIN = '03:00:00'
S2W_UNAVAILABLE_END = '07:30:00'
DOWNTIME_MESSAGE = 'Class registration is unavailable between 3:00AM and 7:30AM.'
