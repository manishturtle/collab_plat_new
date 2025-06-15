from django.contrib.auth import get_user_model
from rest_framework import serializers
from django.utils import timezone
from ...shared.models import TenantUserModel as User
from ..models import ChatChannel, ChannelParticipant, ChatMessage, MessageReadStatus
from ..selectors import get_unread_message_count


class ISODateTimeField(serializers.DateTimeField):
    """Custom DateTimeField that handles ISO format strings and datetime objects."""
    def to_representation(self, value):
        if not value:
            return None
        if isinstance(value, str):
            return value
        return value.isoformat()


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for user representation in chat.
    Includes basic user information and online status.
    """
    full_name = serializers.SerializerMethodField()
    is_online = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 
            'email', 
            'first_name', 
            'last_name',
            'full_name',
            'is_online'
        ]
        read_only_fields = fields
    
    def get_full_name(self, obj):
        return obj.get_full_name() or obj.email
    
    def get_is_online(self, obj):
        # TODO: Implement actual online status logic
        return False


class ChannelParticipantSerializer(serializers.ModelSerializer):
    """
    Serializer for channel participants.
    Includes user details and role in the channel.
    """
    user = UserSerializer(read_only=True)
    created_at = ISODateTimeField(read_only=True)
    
    class Meta:
        model = ChannelParticipant
        fields = [
            'id',
            'user',
            'role',
            'created_at',
            'user_id',
            'channel_id'
        ]
        read_only_fields = fields

class ChatMessageSerializer(serializers.ModelSerializer):
    """
    Serializer for chat messages.
    Includes sender details and read status.
    """
    sender = UserSerializer(read_only=True)
    is_own = serializers.SerializerMethodField()
    read_by = serializers.SerializerMethodField()
    created_at = ISODateTimeField(read_only=True)
    updated_at = ISODateTimeField(read_only=True)
    
    class Meta:
        model = ChatMessage
        fields = [
            'id',
            'content',
            'sender',
            'is_own',
            'read_by',
            'created_at',
            'updated_at',
            'content_type',
            'file_url',
            'parent_id',
            'channel_id',
            'user_id'
        ]
        read_only_fields = fields
    
    def get_is_own(self, obj):
        request = self.context.get('request')
        return request and obj.sender_id == request.user.id
    
    def get_read_by(self, obj):
        return list(obj.read_statuses.values_list('user__email', flat=True))


class ChatChannelSerializer(serializers.ModelSerializer):
    """
    Serializer for chat channels.
    Includes participants and last message details.
    """
    participations = ChannelParticipantSerializer(many=True, read_only=True)
    participants = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=User.objects.all(),
        write_only=True,
        required=False
    )
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    created_at = ISODateTimeField(read_only=True)
    updated_at = ISODateTimeField(read_only=True)
    
    class Meta:
        model = ChatChannel
        fields = [
            'id',
            'name',
            'channel_type',
            'participants',
            'participations',
            'last_message',
            'unread_count',
            'created_at',
            'updated_at',
            'host_application_id',
            'context_object_type',
            'context_object_id',
            'created_by',
            'updated_by',
            'company_id',
            'client_id'
        ]
        read_only_fields = [
            'id', 
            'created_at', 
            'updated_at',
            'participations',
            'last_message',
            'unread_count',
            'created_by',
            'updated_by',
            'company_id',
            'client_id'
        ]
    
    def get_last_message(self, obj):
        last_message = obj.messages.order_by('-created_at').first()
        if last_message:
            return ChatMessageSerializer(
                last_message,
                context=self.context
            ).data
        return None
    
    def get_unread_count(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return 0
        return get_unread_message_count(obj.id, request.user)
    
    def validate(self, data):
        """
        Validate channel data before creation.
        """
        channel_type = data.get('channel_type', self.instance.channel_type if self.instance else None)
        participants = data.get('participants', [])
        
        if channel_type == ChatChannel.ChannelType.DIRECT and len(participants) != 1:
            raise serializers.ValidationError(
                "Direct messages must have exactly one other participant"
            )
            
        return data
    
    def create(self, validated_data):
        """
        Create a new channel with participants.
        """
        from ..services import create_channel
        
        participants = validated_data.pop('participants', [])
        channel = create_channel(
            user=self.context['request'].user,
            name=validated_data.get('name'),
            participants=participants,
            channel_type=validated_data.get('channel_type', ChatChannel.ChannelType.GROUP),
            context_data={
                'host_application_id': validated_data.get('host_application_id'),
                'context_object_type': validated_data.get('context_object_type'),
                'context_object_id': validated_data.get('context_object_id'),
            }
        )
        return channel