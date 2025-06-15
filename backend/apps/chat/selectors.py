from typing import List, Optional
from django.db.models import Q, QuerySet, Prefetch
from django.contrib.auth import get_user_model
from .models import ChatChannel, ChannelParticipant, ChatMessage, MessageReadStatus

User = get_user_model()

def get_channels_for_user(user: User) -> QuerySet[ChatChannel]:
    """
    Retrieves all chat channels a given user is a participant of.
    Orders them by the most recent activity (latest message).
    """
    return ChatChannel.objects.filter(
        participations__user=user
    ).prefetch_related(
        Prefetch('participants', queryset=User.objects.only('id', 'email', 'first_name', 'last_name')),
        'participations'
    ).order_by('-updated_at')

def get_channel_by_id(channel_id: str, user: User) -> Optional[ChatChannel]:
    """
    Get a specific channel if the user is a participant.
    """
    try:
        return ChatChannel.objects.get(
            id=channel_id,
            participations__user=user
        )
    except ChatChannel.DoesNotExist:
        return None

def get_messages_for_channel(channel_id: str, user: User, limit: int = 50) -> QuerySet[ChatMessage]:
    """
    Get messages for a channel that the user has access to.
    """
    return ChatMessage.objects.filter(
        channel_id=channel_id,
        channel__participations__user=user
    ).select_related('user').order_by('-created_at')[:limit]

def get_unread_message_count(channel_id: str, user: User) -> int:
    """
    Get the count of unread messages for a user in a channel.
    """
    # Get the timestamp of the last read message, if any
    last_read = MessageReadStatus.objects.filter(
        user=user,
        message__channel_id=channel_id
    ).order_by('-message__created_at').values_list('message__created_at', flat=True).first()
    
    # If there are no read messages, return count of all messages in the channel
    if not last_read:
        return ChatMessage.objects.filter(channel_id=channel_id).count()
    
    # Otherwise, return count of messages created after the last read message
    return ChatMessage.objects.filter(
        channel_id=channel_id,
        created_at__gt=last_read
    ).count()