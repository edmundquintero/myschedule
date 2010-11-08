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

# Settings required to compose book link.
# Arguments are added to booklook url in view.
# Important! In order to get the book iframe to consistently load in the
# dialog in IE, I had to use the secure booklook url.  If it doesn't seem
# to work on staging or production (or causes mixed content warnings) try
# switching back to http (if IE thinks the local server is secure, then
# it expects the external site to be secure and vice versa???).
BOOKLOOK_URL='https://www.bkstr.com/webapp/wcs/stores/servlet/booklookServlet'
BOOKLOOK_DEFAULT_STORE='636'
# If the bookstores at any other campuses ever happen to get their own store ID
# with Follett, add it into the mapping variable below.  Currently only Levine
# has their own.  All others use the default store ID above.
BOOKLOOK_STORE_CAMPUS_MAPPING={'2007':'637'}
BOOKLOOK_TERMS={'fa':'Fall','sp':'Spring','su':'Summer'}
