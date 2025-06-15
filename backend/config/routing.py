"""
WebSocket routing configuration for the project.

This file defines the WebSocket URL routing for the application.
"""
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator

# Import WebSocket URL patterns from apps
from apps.chat.routing import websocket_urlpatterns as chat_websocket_urlpatterns
from apps.chat.middleware import JWTAuthMiddlewareStack

# Combine all WebSocket URL patterns
websocket_urlpatterns = []
websocket_urlpatterns += chat_websocket_urlpatterns

# The root routing configuration
application = ProtocolTypeRouter({
    "http": None,  # HTTP is handled by Django's ASGI handler
    "websocket": AllowedHostsOriginValidator(
        JWTAuthMiddlewareStack(
            URLRouter(websocket_urlpatterns)
        )
    ),
})
