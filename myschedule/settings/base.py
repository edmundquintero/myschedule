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

ODS_API_HOST = ''
MYSCHEDULE_API_HOST = ''

# Heuristic Search Data
HIGH_THRESHOLD = 1000
MEDIUM_THRESHOLD = 300
CRITERION_THRESHOLD = 10
HAYSTACK_SEARCH_RESULTS_PER_PAGE = 10
BLACKLIST = ['fuck', 'shit']