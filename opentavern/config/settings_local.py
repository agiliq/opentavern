from .settings_base import *

DEBUG = True
TEMPLATE_DEBUG = DEBUG

INSTALLED_APPS += (
    'django_extensions',
)


ALLOWED_HOSTS = ('*')
