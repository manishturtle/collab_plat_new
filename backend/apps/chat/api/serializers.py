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
    # Context fields are optional and will be set based on channel_type
    host_application_id = serializers.CharField(
        max_length=100, 
        required=False, 
        allow_blank=True, 
        allow_null=True,
        default=None
    )
    context_object_type = serializers.CharField(
        max_length=100, 
        required=False, 
        allow_blank=True, 
        allow_null=True,
        default=None
    )
    context_object_id = serializers.CharField(
        max_length=255, 
        required=False, 
        allow_blank=True, 
        allow_null=True,
        default=None
    )
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
        """
        Validate and pre-process channel data before creation.
        Sets default values for different channel types.
        """
        channel_type = data.get('channel_type')
        participants = data.get('participants', [])
        request = self.context.get('request')
        
        if not channel_type:
            raise serializers.ValidationError({
                'detail': 'channel_type is required',
                'code': 'missing_channel_type'
            })
        
        # Convert empty strings to None for context fields
        for field in ['host_application_id', 'context_object_type', 'context_object_id']:
            if field in data and data[field] == '':
                data[field] = None
        
        # Common validations based on channel type
        if channel_type == 'direct':
            # Direct chats have minimal requirements - just need one participant
            if len(participants) != 1:
                raise serializers.ValidationError({
                    'detail': 'Direct message must have exactly one participant (other than yourself)',
                    'code': 'invalid_participant_count'
                })
            
            # Set default values for direct messages
            data['host_application_id'] = 'direct_chat'
            data['context_object_type'] = 'direct_message'
            
            # Generate a consistent ID for direct messages between the same users
            participant_id = participants[0].id if hasattr(participants[0], 'id') else participants[0]
            user_ids = sorted([request.user.id, participant_id])
            data['context_object_id'] = f"direct_{user_ids[0]}_{user_ids[1]}"
            
            # Set a default name if not provided
            if not data.get('name'):
                data['name'] = f"Direct Chat ({request.user.id} & {participant_id})"
            
        elif channel_type == 'group':
            # Group chats require a name
            if not data.get('name'):
                raise serializers.ValidationError({
                    'detail': 'Group name is required',
                    'code': 'missing_group_name'
                })
                
            # Set default values for group chats
            data['host_application_id'] = data.get('host_application_id') or 'group_chat'
            data['context_object_type'] = data.get('context_object_type') or 'group'
            
            # Generate a context_object_id if not provided
            if not data.get('context_object_id'):
                data['context_object_id'] = f"group_{request.user.id}_{data['name'].lower().replace(' ', '_')}"
        
        elif channel_type == 'contextual_object':
            # Contextual chats require specific fields
            required_fields = ['host_application_id', 'context_object_type', 'context_object_id']
            missing = [field for field in required_fields if not data.get(field)]
            if missing:
                raise serializers.ValidationError({
                    'detail': f'Missing required fields for contextual chat: {", ".join(missing)}',
                    'code': 'missing_required_fields',
                    'fields': missing
                })
                
            # Name is required for contextual objects
            if not data.get('name'):
                raise serializers.ValidationError({
                    'detail': 'Name is required for contextual chat',
                    'code': 'missing_name'
                })
        
        else:
            raise serializers.ValidationError({
                'detail': f'Invalid channel_type: {channel_type}. Must be one of: direct, group, contextual_object',
                'code': 'invalid_channel_type',
                'allowed_types': ['direct', 'group', 'contextual_object']
            })
        
        return data
        
    def create(self, validated_data):
        participants = validated_data.pop('participants', [])
        request = self.context.get('request')
        
        # For direct messages, check if a channel already exists between these users
        if validated_data.get('channel_type') == 'direct' and participants:
            try:
                # Get the participant ID (already validated in the validate method)
                participant_id = participants[0].id if hasattr(participants[0], 'id') else participants[0]
                
                # Look for an existing direct message channel between these users
                existing_channel = ChatChannel.objects.filter(
                    channel_type='direct',
                    host_application_id='direct_chat',
                    context_object_type='direct_message',
                    context_object_id=validated_data['context_object_id']
                ).first()
                
                if existing_channel:
                    # Ensure the current user is a participant
                    if not ChannelParticipant.objects.filter(
                        channel=existing_channel,
                        user_id=request.user.id
                    ).exists():
                        self._add_participants(existing_channel, [request.user.id], request.user)
                    
                    # Ensure the other participant is still a participant
                    if not ChannelParticipant.objects.filter(
                        channel=existing_channel,
                        user_id=participant_id
                    ).exists():
                        self._add_participants(existing_channel, [participant_id], request.user)
                    
                    return existing_channel
                    
            except Exception as e:
                logger.warning(f"Error checking for existing direct message channel: {str(e)}")
        
        # If we get here, either it's not a direct message or no existing channel was found
        try:
            # Create the channel - ensure we're using IDs not user objects
            channel = ChatChannel.objects.create(
                **validated_data,
                created_by=request.user.id,
                updated_by=request.user.id
            )
            
            # Add participants
            self._add_participants(channel, participants, request.user)
            
            return channel
            
        except Exception as e:
            # Handle unique constraint violation
            if 'unique_contextual_chat' in str(e):
                # Try to find the existing channel
                existing = ChatChannel.objects.filter(
                    host_application_id=validated_data.get('host_application_id'),
                    context_object_type=validated_data.get('context_object_type'),
                    context_object_id=validated_data.get('context_object_id')
                ).first()
                
                if existing:
                    # Ensure the current user is a participant
                    if not ChannelParticipant.objects.filter(
                        channel=existing,
                        user_id=request.user.id
                    ).exists():
                        self._add_participants(existing, [request.user.id], request.user)
                    
                    # Ensure other participants are added
                    for participant in participants:
                        participant_id = participant.id if hasattr(participant, 'id') else participant
                        if not ChannelParticipant.objects.filter(
                            channel=existing,
                            user_id=participant_id
                        ).exists():
                            self._add_participants(existing, [participant_id], request.user)
                    
                    return existing
            
            # Re-raise the exception if we couldn't handle it
            raise serializers.ValidationError({
                'detail': 'A chat with these parameters already exists',
                'code': 'channel_exists'
            })

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