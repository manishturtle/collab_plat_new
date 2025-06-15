"""
ASGI config for config project.

It exposes the ASGI callable as a module-level variable named ``application``.
"""

import os
import django
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator

# Set the default Django settings module for the 'asgi' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Initialize Django ASGI application
django.setup()
django_asgi_app = get_asgi_application()

# Import WebSocket routing after Django setup
# This is done here to ensure all models are loaded
try:
    from apps.chat.routing import websocket_urlpatterns as chat_websocket_urlpatterns
    from apps.chat.middleware import JWTAuthMiddlewareStack
    
    # Define WebSocket URL patterns
    websocket_urlpatterns = []
    websocket_urlpatterns += chat_websocket_urlpatterns
    
    # Create the ASGI application with WebSocket support
    application = ProtocolTypeRouter({
        "http": django_asgi_app,
        "websocket": AllowedHostsOriginValidator(
            JWTAuthMiddlewareStack(
                URLRouter(websocket_urlpatterns)
            )
        )
    })
    
except Exception as e:
    # Fallback to HTTP-only if WebSocket setup fails
    print(f"Warning: WebSocket setup failed: {str(e)}")
    application = django_asgi_app
