from .settings_base import *

DEBUG = False
TEMPLATE_DEBUG = DEBUG

import dj_database_url
DATABASES['default'] = dj_database_url.config()

# Honor the 'X-Forwarded-Proto' header for request.is_secure()
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

ALLOWED_HOSTS = ['*']

# For heroku the user will be set to active after registration.
# This is done as there is no verification email being sent for now.
DEFAULT_USER_STATUS = True
