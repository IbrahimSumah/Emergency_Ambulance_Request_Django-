"""
ASGI config for EmmergencyAmbulanceSystem project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os

# Set Django settings module FIRST
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'EmmergencyAmbulanceSystem.settings')

# Initialize Django application - this sets up Django and loads all apps
from django.core.asgi import get_asgi_application
django_asgi_app = get_asgi_application()

# NOW it's safe to import Django models/apps because Django is initialized
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import emergencies.routing

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter(
            emergencies.routing.websocket_urlpatterns
        )
    ),
})
