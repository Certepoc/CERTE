"""
WSGI config for CERTE project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CERTE.settings')

# Create the WSGI application
application = get_wsgi_application()

# For Vercel, you may need to define the handler
handler = application  # This line is crucial for Vercel
