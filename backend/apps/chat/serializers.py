"""Serializers for chat-related data models."""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import ChatChannel, ChatMessage, MessageReadStatus

User = get_user_model()


class UserStatusSerializer(serializers.ModelSerializer):
    """Serializer for user status and presence information."""
    id = serializers.IntegerField(read_only=True)
    avatar_url = serializers.SerializerMethodField()
    last_seen = serializers.DateTimeField(format='%Y-%m-%dT%H:%M:%S%z')
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'first_name', 'last_name', 'email',
            'is_online', 'last_seen', 'status', 'status_emoji', 'avatar_url'
        ]
        read_only_fields = fields
    
    def get_avatar_url(self, obj):
        """Get the avatar URL for the user.
        
        Handles various field names that might store user avatars.
        """
        # Check common avatar field names
        for field_name in ['avatar', 'profile_picture', 'photo', 'image']:
            if hasattr(obj, field_name):
                field_value = getattr(obj, field_name)
                if field_value and hasattr(field_value, 'url'):
                    request = self.context.get('request')
                    if request:
                        return request.build_absolute_uri(field_value.url)
                    return field_value.url
        
        # Default placeholder
        return None


class ChatChannelSerializer(serializers.ModelSerializer):
    """Serializer for chat channels."""
    id = serializers.UUIDField(read_only=True)
    is_private = serializers.BooleanField(read_only=True)
    unread_count = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()
    participants = UserStatusSerializer(many=True, read_only=True)
    channel_type = serializers.CharField(read_only=True)
    
    class Meta:
        model = ChatChannel
        fields = [
            'id', 'name', 'channel_type', 'is_private', 'created_at', 'updated_at',
            'unread_count', 'last_message', 'participants'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_unread_count(self, obj):
        """Get the number of unread messages for the current user."""
        request = self.context.get('request')
        user = request.user if request and hasattr(request, 'user') else None
        if not user or not hasattr(user, 'is_authenticated') or not user.is_authenticated:
            return 0
            
        return obj.messages.exclude(
            read_by=user
        ).count()
    
    def get_last_message(self, obj):
        """Get the most recent message in the channel."""
        last_message = obj.messages.order_by('-created_at').first()
        if not last_message:
            return None
            
        request = self.context.get('request')
        user = request.user if request and hasattr(request, 'user') else None
        
        return {
            'id': str(last_message.id),
            'content': last_message.content,
            'content_type': last_message.content_type,
            'user_id': str(last_message.user.id),  # Using id instead of public_id
            'username': last_message.user.username,
            'timestamp': last_message.created_at.isoformat(),
            'is_read': last_message.read_by.filter(
                id=user.id
            ).exists() if user and hasattr(user, 'is_authenticated') and user.is_authenticated else False
        }


class ChatMessageSerializer(serializers.ModelSerializer):
    """Serializer for chat messages."""
    id = serializers.IntegerField(read_only=True)  # Using IntegerField since it's a BigAutoField in the model
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    user_avatar = serializers.SerializerMethodField()
    timestamp = serializers.DateTimeField(source='created_at', read_only=True)
    is_own = serializers.SerializerMethodField()
    read_by = serializers.SerializerMethodField()
    
    class Meta:
        model = ChatMessage
        fields = [
            'id', 'content', 'content_type', 'user_id', 'username', 'user_avatar',
            'timestamp', 'is_own', 'read_by', 'updated_at'
        ]
        read_only_fields = fields
    
    def get_user_avatar(self, obj):
        """Get the avatar URL of the message sender.
        
        Handles various field names that might store user avatars.
        """
        if not obj.user:
            return None
            
        # Check common avatar field names
        for field_name in ['avatar', 'profile_picture', 'photo', 'image']:
            if hasattr(obj.user, field_name):
                field_value = getattr(obj.user, field_name)
                if field_value and hasattr(field_value, 'url'):
                    request = self.context.get('request')
                    if request:
                        return request.build_absolute_uri(field_value.url)
                    return field_value.url
        
        # Default placeholder
        return None
    
    def get_is_own(self, obj):
        """Check if the current user is the sender of the message."""
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return obj.user == request.user
    
    def get_read_by(self, obj):
        """Get list of user IDs who have read this message."""
        return list(obj.read_by.values_list('id', flat=True))


class MessageReadStatusSerializer(serializers.ModelSerializer):
    """Serializer for message read status."""
    user_id = serializers.IntegerField(source='user.id')
    username = serializers.CharField(source='user.username')
    read_at = serializers.DateTimeField(format='%Y-%m-%dT%H:%M:%S%z')
    
    class Meta:
        model = MessageReadStatus
        fields = ['user_id', 'username', 'is_read', 'read_at']
        read_only_fields = fields


class TypingStatusSerializer(serializers.Serializer):
    """Serializer for typing status updates."""
    user_id = serializers.UUIDField()
    username = serializers.CharField()
    is_typing = serializers.BooleanField()
    channel_id = serializers.UUIDField()
    timestamp = serializers.DateTimeField()


class PresenceUpdateSerializer(serializers.Serializer):
    """Serializer for presence updates."""
    user_id = serializers.UUIDField()
    is_online = serializers.BooleanField()
    status = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    status_emoji = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    last_seen = serializers.DateTimeField(required=False, allow_null=True)
