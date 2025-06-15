"""Chat application for real-time messaging and collaboration."""

# Default app config
default_app_config = 'apps.chat.apps.ChatConfig'

# Note: Avoid importing models, serializers, or other app components here
# to prevent circular imports. Import them directly in the modules where they are needed.

__all__ = [
    # Serializers
    'UserStatusSerializer',
    'ChatChannelSerializer',
    'ChatMessageSerializer',
    'MessageReadStatusSerializer',
    'TypingStatusSerializer',
    'PresenceUpdateSerializer',
    
    # Consumers
    'ChatConsumer',
    'PresenceConsumer',
    'TypingConsumer',
    
    # Models
    'ChatChannel',
    'ChatMessage',
    'MessageReadStatus',
    'UserChannelState'
]