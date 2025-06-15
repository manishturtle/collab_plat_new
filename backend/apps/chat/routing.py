from django.urls import re_path
from . import consumers

# WebSocket URL patterns
websocket_urlpatterns = [
    # WebSocket connection for chat messages
    re_path(r'ws/chat/(?P<channel_id>[\w-]+)/$', consumers.ChatConsumer.as_asgi()),
    
    # WebSocket connection for user presence
    re_path(r'ws/presence/$', consumers.PresenceConsumer.as_asgi()),
    
    # WebSocket connection for typing indicators
    re_path(r'ws/typing/(?P<channel_id>[\w-]+)/$', consumers.TypingConsumer.as_asgi()),
]
