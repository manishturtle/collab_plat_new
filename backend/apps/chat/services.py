from typing import List, Optional, Dict, Any
from django.db import transaction
from django.utils import timezone
from django.conf import settings
from apps.shared.models import TenantUserModel as User
from .models import ChatChannel, ChannelParticipant, ChatMessage, MessageReadStatus
from .selectors import get_channel_by_id

@transaction.atomic
def create_channel(
    *, 
    user: User, 
    name: str = None, 
    participants: List[User] = None,
    channel_type: str = ChatChannel.ChannelType.GROUP,
    context_data: Optional[Dict[str, Any]] = None
) -> ChatChannel:
    """
    Creates a new chat channel and adds participants.
    The creator is automatically made an admin.
    
    Args:
        user: The user creating the channel
        name: Optional name for the channel (auto-generated for direct messages)
        participants: List of users to add to the channel (can be User objects or user IDs)
        channel_type: Type of channel (direct, group, or contextual)
        context_data: Optional context data for contextual channels
    """
    # Convert participant IDs to User objects if needed
    participant_users = []
    participants = participants or []
    
    # If participants are passed as integers (IDs), fetch the user objects
    for p in participants:
        if isinstance(p, int) or isinstance(p, str) and p.isdigit():
            try:
                p_id = int(p)
                p_user = User.objects.get(id=p_id)
                participant_users.append(p_user)
            except User.DoesNotExist:
                # Skip invalid user IDs
                continue
        else:
            # It's already a user object
            participant_users.append(p)
            
    # Ensure unique participants
    all_participants = set(participant_users)
    all_participants.add(user)  # Always include the creator

    # For direct messages, ensure only 2 participants
    if channel_type == ChatChannel.ChannelType.DIRECT:
        if len(all_participants) != 2:
            raise ValueError("Direct messages must have exactly 2 participants")
        # Generate a consistent name for direct messages
        name = " & ".join(sorted([p.get_full_name() or p.email for p in all_participants]))
    
    # Create the channel
    channel = ChatChannel.objects.create(
        name=name,
        channel_type=channel_type,
        created_by=user.id,
        updated_by=user.id,
        **context_data or {}
    )
    
    # Add participants
    participant_objects = []
    for participant in all_participants:
        role = ChannelParticipant.Role.ADMIN if participant == user else ChannelParticipant.Role.MEMBER
        participant_objects.append(
            ChannelParticipant(
                channel=channel,
                user=participant,
                role=role,
                created_by=user.id,
                updated_by=user.id
            )
        )
    
    ChannelParticipant.objects.bulk_create(participant_objects)
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