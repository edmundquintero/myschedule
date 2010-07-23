from myschedule.settings.base import *

DEBUG = TEMPLATE_DEBUG = True

DATABASE_ENGINE = 'mysql'
DATABASE_NAME = 'myschedule'
DATABASE_USER = 'myschedule'
DATABASE_PASSWORD = 'myschedule'

# In development, use the database for sessions, and disable caching.
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
CACHE_BACKEND = 'dummy://'

# MEDIA_ROOT = j(app_root, 'media')
# MEDIA_URL = APP_NAME + '/media/'
