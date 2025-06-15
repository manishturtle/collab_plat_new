from typing import List, Optional, Dict, Any
from django.db import transaction
from django.utils import timezone
from django.conf import settings
from apps.shared.models import TenantUserModel as User
from .models import ChatChannel, ChannelParticipant, ChatMessage, MessageReadStatus
from .selectors import get_channel_by_id

@transaction.atomic
# apps/chat/services.py

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
        ChatChannel: The created channel
    """
    from .models import ChatChannel, ChannelParticipant
    # Validate input
    if not created_by:
        raise ValueError("created_by user is required")
    
    if channel_type not in [t[0] for t in ChatChannel.ChannelType.choices]:
        raise ValueError(f"Invalid channel_type. Must be one of: {[t[0] for t in ChatChannel.ChannelType.choices]}")
    
    if channel_type in ['group', 'contextual_object'] and not name:
        raise ValueError("Name is required for group and contextual channels")
    
    if channel_type == 'direct' and len(participants) != 1:
        raise ValueError("Direct messages must have exactly one participant")
    
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
    
    # Add participants
    for user_id in participants:
        try:
            user = User.objects.get(id=user_id)
            print("kkk:", user)
            ChannelParticipant.objects.create(
                channel=channel,
                user=user,
                role=ChannelParticipant.Role.ADMIN if user == created_by else ChannelParticipant.Role.MEMBER,
                created_by=created_by.id,
                updated_by=created_by.id
            )
        except User.DoesNotExist:
            continue
    
    return channel
    
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
    Returns the number of messages marked as read.
    """
    # Get unread messages
    unread_messages = ChatMessage.objects.filter(
        channel_id=channel_id
    ).exclude(
        read_statuses__user=user
    )
    
    # Create read statuses
    read_statuses = [
        MessageReadStatus(
            message=msg,
            user=user,
            created_by=user.id,
            updated_by=user.id,
            company_id=getattr(user, 'company_id', 1),  # Add company_id
            client_id=getattr(user, 'client_id', 1)     # Add client_id
        ) 
        for msg in unread_messages
    ]
    
    # Bulk create read statuses
    if read_statuses:
        MessageReadStatus.objects.bulk_create(read_statuses)
    
    return len(read_statuses)