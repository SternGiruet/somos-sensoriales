"""
Configuración WSGI para el proyecto Gestión Sensorial.
Expone el invocable WSGI como una variable de nivel de módulo llamada 'application'.
"""
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

application = get_wsgi_application()
