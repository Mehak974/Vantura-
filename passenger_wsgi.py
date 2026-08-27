import os
import sys

# Add your project directory to the sys.path
# This ensures that passenger can find your Django project
sys.path.insert(0, os.path.dirname(__file__))

# Set the Django settings module
os.environ['DJANGO_SETTINGS_MODULE'] = 'brenve_project.settings'

# Enable PostgreSQL production config
os.environ['ENV'] = 'production'

# Setup Django and get the WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
