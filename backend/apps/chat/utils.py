"""
Utilities for WebSocket communication in the chat application.
"""
import asyncio
import json
import logging
from typing import Dict, Any, Optional, List, Set, Union
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db.models import Q, Prefetch
from .models import ChatMessage, MessageReadStatus, ChatChannel

User = get_user_model()
logger = logging.getLogger(__name__)


def get_channel_group_name(channel_id: str, group_type: str = 'chat') -> str:
    """
    Get the channel group name for a given channel ID and group type.
    
    Args:
        channel_id: The ID of the channel
        group_type: Type of group ('chat', 'typing', 'presence', etc.)
        
    Returns:
        str: The channel group name
    """
    return f'{group_type}_{channel_id}'


def get_user_presence_group_name(user_id: str) -> str:
    """
    Get the presence group name for a user.
    
    Args:
        user_id: The ID of the user
        
    Returns:
        str: The user's presence group name
    """
    return f'user_{user_id}'


async def notify_new_message(channel_id: str, message_data: Dict[str, Any]) -> None:
    """
    Notify channel participants about a new message.
    
    Args:
        channel_id: The ID of the channel
        message_data: The message data to send
    """
    channel_layer = get_channel_layer()
    group_name = get_channel_group_name(channel_id, 'chat')
    
    try:
        await channel_layer.group_send(
            group_name,
            {
                'type': 'chat.message',
                'message': message_data
            }
        )
    except Exception as e:
        logger.error(f'Error sending new message notification: {str(e)}')


async def notify_message_read(channel_id: str, user_id: str, message_id: str) -> None:
    """
    Notify clients that a message has been read.
    
    Args:
        channel_id: The ID of the channel containing the message
        user_id: The ID of the user who read the message
        message_id: The ID of the message that was read
    """
    channel_layer = get_channel_layer()
    group_name = get_channel_group_name(channel_id, 'chat')
    
    try:
        await channel_layer.group_send(
            group_name,
            {
                'type': 'message.read',
                'message_id': message_id,
                'user_id': user_id,
                'timestamp': timezone.now().isoformat()
            }
        )
    except Exception as e:
        logger.error(f'Error sending message read notification: {str(e)}')


async def notify_typing(channel_id: str, user_id: str, is_typing: bool) -> None:
    """
    Notify clients in a channel that a user is typing.
    
    Args:
        channel_id: The ID of the channel
        user_id: The ID of the user who is typing
        is_typing: Whether the user started or stopped typing
    """
    channel_layer = get_channel_layer()
    group_name = get_channel_group_name(channel_id, 'typing')
    
    try:
        await channel_layer.group_send(
            group_name,
            {
                'type': 'typing.update',
                'user_id': user_id,
                'is_typing': is_typing,
                'timestamp': timezone.now().isoformat()
            }
        )
    except Exception as e:
        logger.error(f'Error sending typing notification: {str(e)}')


async def notify_presence_update(user_id: str, is_online: bool, status: str = None, 
                               status_emoji: str = None) -> None:
    """
    Notify about a user's presence status change.
    
    Args:
        user_id: The ID of the user
        is_online: Whether the user is now online
        status: Optional status text
        status_emoji: Optional emoji for status
    """
    channel_layer = get_channel_layer()
    
    try:
        # Notify all presence subscribers
        await channel_layer.group_send(
            'presence',
            {
                'type': 'presence.update',
                'user_id': user_id,
                'is_online': is_online,
                'status': status,
                'status_emoji': status_emoji,
                'last_seen': timezone.now().isoformat() if not is_online else None
            }
        )
    except Exception as e:
        logger.error(f'Error sending presence update: {str(e)}')


async def notify_channel_update(channel_id: str, event_type: str, data: Dict[str, Any]) -> None:
    """
    Notify clients about channel updates (e.g., new member, name change).
    
    Args:
        channel_id: The ID of the channel that was updated
        event_type: Type of the event (e.g., 'channel.updated', 'member.added')
        data: Additional data related to the event
    """
    channel_layer = get_channel_layer()
    group_name = get_channel_group_name(channel_id, 'chat')
    
    try:
        await channel_layer.group_send(
            group_name,
            {
                'type': 'channel.event',
                'event': event_type,
                'data': data,
                'timestamp': timezone.now().isoformat()
            }
        )
    except Exception as e:
        logger.error(f'Error sending channel update: {str(e)}')


async def get_online_users(channel_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Get a list of online users, optionally filtered by channel.
    
    Args:
        channel_id: Optional channel ID to filter users by
        
    Returns:
        List of user dictionaries with online status
    """
    from django.db.models import Q, Prefetch
    
    # Get users who were active in the last 5 minutes
    active_threshold = timezone.now() - timezone.timedelta(minutes=5)
    online_users = User.objects.filter(
        Q(is_online=True) | Q(last_seen__gte=active_threshold)
    ).order_by('username')
    
    # Filter by channel if specified
    if channel_id:
        try:
            channel = await ChatChannel.objects.prefetch_related(
                Prefetch('participants', queryset=User.objects.all())
            ).aget(id=channel_id)
            
            # Filter users to only those in the channel
            channel_user_ids = set(str(user.id) for user in channel.participants.all())
            online_users = [
                user for user in online_users 
                if str(user.id) in channel_user_ids
            ]
        except ChatChannel.DoesNotExist:
            logger.warning(f'Channel {channel_id} not found')
            return []
    
    # Serialize user data
    return [
        {
            'id': str(user.id),
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'is_online': user.is_online,
            'last_seen': user.last_seen.isoformat() if user.last_seen else None,
            'status': user.status,
            'status_emoji': user.status_emoji,
            'avatar_url': user.avatar.url if user.avatar else None
        }
        for user in online_users
    ]


def mark_messages_as_read(user_id: str, message_ids: List[str]) -> int:
    """
    Mark multiple messages as read by a user.
    
    Args:
        user_id: The ID of the user who read the messages
        message_ids: List of message IDs to mark as read
        
    Returns:
        int: Number of messages marked as read
    """
    from django.db import transaction
    
    with transaction.atomic():
        # Get unread messages
        messages = ChatMessage.objects.filter(
            id__in=message_ids
        ).exclude(
            read_by=user_id
        ).select_related('channel')
        
        # Create read status for each message
        read_statuses = [
            MessageReadStatus(
                message=message,
                user_id=user_id,
                is_read=True,
                read_at=timezone.now()
            )
            for message in messages
        ]
        
        # Bulk create read statuses
        if read_statuses:
            MessageReadStatus.objects.bulk_create(
                read_statuses,
                ignore_conflicts=True
            )
        
        # Update channel unread counts if needed
        channel_ids = {str(msg.channel_id) for msg in messages}
        for channel_id in channel_ids:
            # Trigger notification for each channel
            async_to_sync(notify_message_read)(
                channel_id=channel_id,
                user_id=user_id,
                message_id=None  # Indicates batch update
            )
    
    return len(read_statuses)
