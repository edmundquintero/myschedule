from cpsite.settings.base import *

INSTALLED_APPS.extend([
    # 'django.contrib.admin',
    'myschedule',
])

app_root = d(d(__file__))
APP_STATIC_MEDIA = j(app_root, 'static')

LOGIN_URL = '/myschedule/login/'
CAS_REDIRECT_URL = '/myschedule/'

APP_NAME = 'myschedule'
BASE_URL = APP_NAME + '/'

ADMINS.append(('Your Name', 'first.last@cpcc.edu'))

SESSION_COOKIE_NAME = 'myschedule_sessionid'

THEME = '3g'

# Settings required to compose book link.
# Arguments are added to url in views.py
BOOKLOOK_URL='http://www.bkstr.com/webapp/wcs/stores/servlet/booklookServlet'
BOOKLOOK_DEFAULT_STORE='636'
# If the bookstores at any other campuses ever happen to get their own store ID
# with Follett, add it into the mapping variable below.  Currently only Levine
# has their own.  All others use the default store ID above.
BOOKLOOK_STORE_CAMPUS_MAPPING={'2007':'637'}
BOOKLOOK_TERMS={'fa':'Fall','sp':'Spring','su':'Summer'}
