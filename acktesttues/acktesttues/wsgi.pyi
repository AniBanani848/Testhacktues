"""
WSGI config for acktesttues project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/wsgi/
"""

import os 
import sys

path = '/home/MEAh1/Testhacktues'
if path not in sys.path:
    sys.path.append(path)

if f"{path}/acktesttues" not in sys.path:
    sys.path.append(f"{path}/acktesttues")

os.environ.setdefault('DJANGO_SETTINGS_MODULE')
get_wsgi_application = None
try:
    from django.core.wsgi import get_wsgi_application
except ImportError:
    pass
else:
    application = get_wsgi_application()
