from typing import List, Optional, Dict, Any
import uuid
from django.db import transaction
from django.utils import timezone
from django.conf import settings
from apps.shared.models import TenantUserModel as User
from .models import ChatChannel, ChannelParticipant, ChatMessage, MessageReadStatus
from .selectors import get_channel_by_id

@transaction.atomic
def create_channel(channel_type, participants, name=None, host_application_id=None,
                 context_object_type=None, context_object_id=None, created_by=None):
    """
    Service function to create different types of channels
    
    Args:
        channel_type (str): Type of channel ('direct', 'group', 'contextual_object')
        participants (list): List of user IDs to add as participants
        name (str): Channel name (required for group and contextual channels)
        host_application_id (str): ID of the host application
        context_object_type (str): Type of the context object
        context_object_id (str): ID of the context object
        created_by (User): User creating the channel
    
    Returns:
        ChatChannel: The created or existing channel
    """
    from .models import ChatChannel, ChannelParticipant
    
    # Validate input
    if not created_by:
        raise ValueError("created_by user is required")
    
    if channel_type not in [t[0] for t in ChatChannel.ChannelType.choices]:
        raise ValueError(f"Invalid channel_type. Must be one of: {[t[0] for t in ChatChannel.ChannelType.choices]}")
    
    if channel_type == 'direct':
        if len(participants) != 1:
            raise ValueError("Direct messages must have exactly one participant")
        
        # For direct messages, check if a channel already exists between these users
        other_user_id = participants[0]
        existing_channel = _get_existing_dm_channel(created_by.id, other_user_id)
        if existing_channel:
            return existing_channel
            
        # Get the other user for naming the channel
        try:
            other_user = User.objects.get(id=other_user_id)
            name = f"{other_user.get_full_name() or other_user.email}"
        except User.DoesNotExist:
            name = "Direct Message"
    
    elif channel_type in ['group', 'contextual_object'] and not name:
        raise ValueError("Name is required for group and contextual channels")
    
    # Create the channel
    channel = ChatChannel.objects.create(
        channel_type=channel_type,
        name=name,
        host_application_id=host_application_id or 'chat_app',
        context_object_type=context_object_type or f"{channel_type}_channel",
        context_object_id=context_object_id or str(uuid.uuid4()),
        created_by=created_by.id,
        updated_by=created_by.id
    )
    
    # Add participants - for direct messages, include both users
    participant_ids = [created_by.id] + participants if channel_type == 'direct' else participants
    
    for user_id in participant_ids:
        try:
            user = User.objects.get(id=user_id)
            ChannelParticipant.objects.get_or_create(
                channel=channel,
                user=user,
                defaults={
                    'role': ChannelParticipant.Role.ADMIN if user == created_by else ChannelParticipant.Role.MEMBER,
                    'created_by': created_by.id,
                    'updated_by': created_by.id
                }
            )
        except User.DoesNotExist:
            continue
    
    return channel

def _get_existing_dm_channel(user1_id, user2_id):
    """
    Check if a direct message channel already exists between two users.
    """
    from .models import ChatChannel, ChannelParticipant
    
    # Get all direct message channels where both users are participants
    user1_channels = set(ChannelParticipant.objects.filter(
        user_id=user1_id,
        channel__channel_type='direct'
    ).values_list('channel_id', flat=True))
    
    user2_channels = set(ChannelParticipant.objects.filter(
        user_id=user2_id,
        channel__channel_type='direct'
    ).values_list('channel_id', flat=True))
    
    # Find common channels (channels where both users are participants)
    common_channel_ids = user1_channels.intersection(user2_channels)
    
    if common_channel_ids:
        # Return the first common channel
        return ChatChannel.objects.get(id=next(iter(common_channel_ids)))
    
    return None
    
@transaction.atomic
def send_message(
    *, 
    channel_id: str, 
    user: User, 
    content: str,
    **kwargs
) -> ChatMessage:
    """
    Send a message to a channel.
    """
    # Verify user has access to the channel
    channel = get_channel_by_id(channel_id, user)
    if not channel:
        raise ValueError("Channel not found or access denied")
    
    # Ensure user is a participant in the channel
    if not channel.participations.filter(user=user).exists():
        raise ValueError("User is not a participant in this channel")
    
    # Create the message
    message = ChatMessage.objects.create(
        channel=channel,
        user=user,  # Using user instead of sender to match the model
        content=content,
        created_by=user.id,
        updated_by=user.id,
        **kwargs
    )
    
    # Update channel's updated_at to reflect new activity
    ChatChannel.objects.filter(id=channel_id).update(
        updated_at=timezone.now(),
        updated_by=user.id
    )
    
    return message

def mark_messages_as_read(channel_id: str, user: User) -> int:
    """
    Mark all messages in a channel as read for a user.
    Updates UserChannelState with the latest read message.
    Returns the number of messages marked as read.
    """
    from .models import UserChannelState
    
    # Get the most recent message in the channel
    last_message = ChatMessage.objects.filter(
        channel_id=channel_id
    ).order_by('-created_at').first()
    
    if not last_message:
        return 0
    
    # Hardcoded tenant IDs as fallback
    company_id = 1
    client_id = 1
    
    # Get or create UserChannelState for this user and channel
    user_channel_state, created = UserChannelState.objects.get_or_create(
        user=user,
        channel_id=channel_id,
        defaults={
            'created_by': user.id,
            'updated_by': user.id,
            'company_id': company_id,
            'client_id': client_id,
        }
    )
    
    # Ensure required fields are set
    if not user_channel_state.company_id:
        user_channel_state.company_id = company_id
    if not user_channel_state.client_id:
        user_channel_state.client_id = client_id
    
    # Update the last read message ID
    user_channel_state.last_read_message_id = last_message.id
    user_channel_state.updated_by = user.id
    user_channel_state.save(update_fields=[
        'last_read_message_id', 
        'updated_at', 
        'updated_by',
        'company_id',
        'client_id'
    ])
    
    # Get unread messages (messages after the last read message)
    unread_messages = ChatMessage.objects.filter(
        channel_id=channel_id,
        created_at__gt=user_channel_state.updated_at if not created else timezone.now()
    )
    
    # Create read statuses for unread messages
    read_statuses = []
    for msg in unread_messages:
        read_statuses.append(
            MessageReadStatus(
                message=msg,
                user=user,
                created_by=user.id,
                updated_by=user.id,
                company_id=company_id,
                client_id=client_id
            )
        )
    
    # Bulk create read statuses
    if read_statuses:
        MessageReadStatus.objects.bulk_create(read_statuses)
    
    return len(read_statuses)