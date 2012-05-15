from cpsite.settings.base import *

INSTALLED_APPS.extend([
    # 'django.contrib.admin',
    'myschedule',
    'haystack',
])

app_root = d(d(__file__))
APP_STATIC_MEDIA = j(app_root, 'static')

LOGIN_URL = '/myschedule/login/'
CAS_REDIRECT_URL = '/myschedule/schedule_login/'

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

CPAPI_URL_FORMAT = 'http://pas1-central.cpcc.edu/cpapi/?%s'
CPAPI_KEY = ""

## Haystack settings
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

## Address to college catalog
CATALOG_URL = 'http://www.cpcc.edu/attending/catalog'

## schedule2webadvisor settings
S2W_KEY_LOCATION = ''
S2W_USER_AT_SERVER = 'snap2webadvisor@cis.cpcc.edu'
S2W_KNOWNHOSTS = ''
S2W_SEPARATOR = '}'
S2W_RETURN_VALUES = ['Success', 'Empty Arguments' , 'already registered', 'valid person', 'Academic Level']
S2W_DATATEL_URL = 'https://mycollege2.cpcc.edu/WebAdvisorST/WebAdvisor?CONSTITUENCY=WBST&type=P&pid=ST-WRGS'
# When finished testing, set S2W_TEST_SECTIONS to empty string
S2W_TEST_SECTIONS = ''
# s2w_unavailable_begin and end time should both be empty string if there
# is no downtime for webadvisor (24 hour time format otherwise)
S2W_UNAVAILABLE_BEGIN = '03:00:00'
S2W_UNAVAILABLE_END = '07:30:00'
S2W_DOWNTIME_MESSAGE = 'Class registration is unavailable between 3:00AM and 7:30AM.'
S2W_FAILURE_MESSAGE = 'Class registration is currently unavailable. This may be due to system maintenance. System maintenance occurs daily between 3:00AM and 7:30AM and on Fridays between 5:30PM and 8:00PM. Please contact the ITS Help Desk for assistance if you receive this message outside of a scheduled maintenance period.'
S2W_SUCCESS_MESSAGE = 'Your schedule was successfully added to your preferred list in MyCollege.  Select Continue to sign in to MyCollege and complete the registration process.'

## Authorization settings for course bulk data load and seat count updates
AUTH_IP_FOR_COURSE_UPDATE = []
AUTH_KEY_FOR_COURSE_UPDATE = ''
AUTH_IP_FOR_SEAT_UPDATE = []
AUTH_KEY_FOR_SEAT_UPDATE = ''

## Disclaimer or notification to be displayed on index page (typically for a non-production release).
SYSTEM_NOTIFICATION = ""

## Determines if link to feedback form should be displayed.
ALLOW_FEEDBACK = 'False'

## If available_terms should appear in a certain order, specify them in that order.
AVAILABLE_TERMS = [{'term':'su',
                    'year': '2012',
                    'display_term': 'Summer 2012',
                    'start_date': '05/21/2012',
                    'end_date': '07/19/2012'},
                    {'term':'fa',
                    'year': '2012',
                    'display_term': 'Fall 2012',
                    'start_date': '08/09/2012',
                    'end_date': '12/11/2012'},
                    {'term':'sp', 
                    'year': '2012', 
                    'display_term': 'Spring 2012',
                    'start_date': '01/07/2012',
                    'end_date': '05/08/2012'}
                   ]

HELP_SCREENCAST_URL = "http://www.youtube.com/watch?v=IKN4l1GxI3M"
