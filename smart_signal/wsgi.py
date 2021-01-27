"""
WSGI config for smart_signal project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/howto/deployment/wsgi/
"""

import os
import sys

sys.path.append('/home/ssp/ecubesolutions.in/venv/smart_signal/smart_signal')
os.environ.setdefault("PYTHON_EGG_CACHE", "/home/ssp/ecubesolutions.in/venv/smart_signal/egg_cache")

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "smart_signal.settings")

application = get_wsgi_application()


