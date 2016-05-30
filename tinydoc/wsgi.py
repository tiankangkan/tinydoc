"""
WSGI config for test_of_lin project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/howto/deployment/wsgi/
"""

import os
import sys
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tinydoc.settings")
os.environ.setdefault("PYTHON_EGG_CACHE", "/tmp/.python-eggs")

project = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, project)

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
