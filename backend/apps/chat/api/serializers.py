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
    # Make context fields optional by setting required=False
    host_application_id = serializers.CharField(max_length=100, required=False, allow_blank=True, allow_null=True)
    context_object_type = serializers.CharField(max_length=100, required=False, allow_blank=True, allow_null=True)
    context_object_id = serializers.CharField(max_length=255, required=False, allow_blank=True, allow_null=True)
    name = serializers.CharField(max_length=255, required=False, allow_blank=True, allow_null=True)
    
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
        """Validate and pre-process channel data before creation."""
        channel_type = data.get('channel_type')
        participants = data.get('participants', [])
        request = self.context.get('request')
        
        # Common validations based on channel type
        if channel_type == 'direct':
            # Direct chats have minimal requirements - just need one participant
            if len(participants) != 1:
                raise serializers.ValidationError({
                    'detail': 'Direct message must have exactly one participant (other than yourself)'
                })
            
            # ALWAYS set default values - this makes these fields optional for the API
            # Set host_application_id
            data['host_application_id'] = 'direct_chat'
            
            # Set context_object_type
            data['context_object_type'] = 'direct_message'
            
            # Generate a consistent ID for direct messages between the same users
            # Extract the participant ID to ensure we're sorting integers, not objects
            participant_id = participants[0].id if hasattr(participants[0], 'id') else participants[0]
            user_ids = sorted([request.user.id, participant_id])
            data['context_object_id'] = f"direct_{user_ids[0]}_{user_ids[1]}"
            
            # Set a default name
            data['name'] = f"Direct Chat ({request.user.id} & {participant_id})"
            
        # For group chats
        elif channel_type == 'group':
            # Group chats require a name
            if not data.get('name'):
                raise serializers.ValidationError({
                    'detail': 'Group name is required'
                })
                
            # Apply defaults for context fields if not provided
            if 'host_application_id' not in data or not data['host_application_id']:
                data['host_application_id'] = 'group_chat'
                
            if 'context_object_type' not in data or not data['context_object_type']:
                data['context_object_type'] = 'group'
                
            if 'context_object_id' not in data or not data['context_object_id']:
                data['context_object_id'] = f"group_{request.user.id}_{data['name'].replace(' ', '_')}"
        
        # For contextual chats
        elif channel_type == 'contextual_object':
            # Contextual chats require specific fields
            required_fields = ['host_application_id', 'context_object_type', 'context_object_id', 'name']
            missing = [field for field in required_fields if not data.get(field)]
            if missing:
                raise serializers.ValidationError({
                    'detail': f'Missing required fields for contextual chat: {", ".join(missing)}'
                })
        
        else:
            raise serializers.ValidationError({
                'detail': f'Invalid channel_type: {channel_type}. Must be one of: direct, group, contextual_object'
            })
        
        return data
        
    def create(self, validated_data):
        participants = validated_data.pop('participants', [])
        request = self.context.get('request')
        
        # Create the channel - ensure we're using IDs not user objects
        channel = ChatChannel.objects.create(
            **validated_data,
            created_by=request.user.id,
            updated_by=request.user.id
        )
        
        # Add participants
        self._add_participants(channel, participants, request.user)
        
        return channel

    def _add_participants(self, channel, participant_ids, current_user):
        """Helper method to add participants to a channel"""
        from apps.shared.models import TenantUserModel as User
        
        # Get the current user ID to use in created_by and updated_by
        current_user_id = current_user.id if hasattr(current_user, 'id') else current_user
        
        # Add current user as admin if they're not already a participant
        if not ChannelParticipant.objects.filter(channel=channel, user_id=current_user_id).exists():
            try:
                # Ensure the user exists before creating the participant
                user = User.objects.get(id=current_user_id, is_active=True)
                ChannelParticipant.objects.create(
                    channel=channel,
                    user=user,  # Use the user object directly
                    role=ChannelParticipant.Role.ADMIN,
                    created_by=current_user_id,
                    updated_by=current_user_id
                )
            except User.DoesNotExist:
                # Skip if user doesn't exist
                pass
        
        # Add other participants
        for participant in participant_ids or []:
            # Extract ID if we have a User object, or use directly if already an ID
            user_id = participant.id if hasattr(participant, 'id') else participant
            
            # Skip if this is the current user or if user_id is None/empty
            if not user_id or user_id == current_user_id:
                continue
                
            try:
                # Get the user object to ensure it exists
                user = User.objects.get(id=user_id, is_active=True)
                
                # Create participant if they don't already exist in the channel
                ChannelParticipant.objects.get_or_create(
                    channel=channel,
                    user=user,  # Use the user object directly
                    defaults={
                        'role': ChannelParticipant.Role.MEMBER,
                        'created_by': current_user_id,
                        'updated_by': current_user_id
                    }
                )
            except User.DoesNotExist:
                # Skip if user doesn't exist
                continue