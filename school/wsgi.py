"""
WSGI config for school project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os, sys

from django.core.wsgi import get_wsgi_application

from dotenv import load_dotenv
load_dotenv()

if not os.getenv("DEBUG"):
	PATH_PROD_WSGI = os.getenv('PATH_PROD_WSGI')
	sys.path.append(PATH_PROD_WSGI)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school.settings')

application = get_wsgi_application()
