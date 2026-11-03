import os
import sys

# Add backend directory to sys.path
backend_dir = os.path.join(os.path.dirname(__file__), '..', 'backend')
sys.path.insert(0, os.path.abspath(backend_dir))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'truck_router_backend.settings')

from django.core.wsgi import get_wsgi_application
app = get_wsgi_application()
