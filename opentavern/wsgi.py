import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "opentavern.settings")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

if "herokuapp" in os.environ:
    from dj_static import Cling

    application = Cling(get_wsgi_application())
