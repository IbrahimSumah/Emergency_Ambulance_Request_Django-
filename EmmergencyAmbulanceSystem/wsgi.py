"""
⚠️ DEPRECATED: This WSGI configuration file is no longer used.

This project has been migrated to ASGI (Asynchronous Server Gateway Interface).
WSGI (Web Server Gateway Interface) is deprecated for this application.

**DO NOT USE THIS FILE** - It is kept only for backward compatibility reference.

**Current Configuration:**
- Application now uses ASGI: `EmmergencyAmbulanceSystem.asgi.application`
- ASGI server: Daphne (configured in docker-compose.yml and Dockerfile)
- WebSocket support: Enabled via Django Channels
- Deployment: Use `daphne` or `uvicorn` ASGI servers, NOT Gunicorn

**Migration Date:** 2024
**Migration Status:** Complete - All WSGI references removed from settings.py

**If you need to use WSGI (not recommended):**
1. Uncomment WSGI_APPLICATION in settings.py
2. Use Gunicorn or uWSGI as the WSGI server
3. Note: WebSocket functionality will NOT work with WSGI

For more information on ASGI deployment, see:
- https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
- https://channels.readthedocs.io/
- MIGRATION_WSGI_TO_ASGI.md in project root
"""

import os
import warnings

# Issue deprecation warning if this file is imported
warnings.warn(
    "WSGI configuration is deprecated. This application uses ASGI. "
    "See EmmergencyAmbulanceSystem.asgi for the current configuration.",
    DeprecationWarning,
    stacklevel=2
)

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'EmmergencyAmbulanceSystem.settings')

# ⚠️ DEPRECATED: This application variable should not be used
# Use ASGI application instead: EmmergencyAmbulanceSystem.asgi.application
application = get_wsgi_application()
