"""
Signals for the chat application.
"""
import logging
from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db import transaction
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import ChatMessage, ChatChannel, MessageReadStatus
from .utils import notify_new_message, notify_message_read, notify_presence_update

User = get_user_model()
logger = logging.getLogger(__name__)

# Track user presence state
user_presence = {}

@receiver(post_save, sender=ChatMessage)
def handle_new_message(sender, instance, created, **kwargs):
    """
    Handle new chat messages and notify channel participants.
    """
    if created:
        # Update the channel's updated_at timestamp
        ChatChannel.objects.filter(id=instance.channel_id).update(updated_at=timezone.now())
        
        # Prepare message data for WebSocket
        message_data = {
            'id': str(instance.id),
            'channel_id': str(instance.channel_id),
            'sender_id': str(instance.user.id),  # Use 'user' instead of 'sender_id'
            'content': instance.content,
            'timestamp': instance.created_at.isoformat(),  # Use 'created_at' instead of 'timestamp'
            'is_read': False,
            'attachments': [{
                'file': instance.file_url,
                'file_name': instance.file_url.split('/')[-1] if instance.file_url else '',
                'mime_type': instance.content_type
            }] if instance.file_url else []
        }
        
        # Notify channel participants
        async_to_sync(notify_new_message)(
            channel_id=str(instance.channel_id),
            message_data=message_data
        )


@receiver(post_save, sender=MessageReadStatus)
def handle_message_read(sender, instance, created, **kwargs):
    """
    Handle message read receipts and notify other participants.
    """
    if created and instance.is_read:
        async_to_sync(notify_message_read)(
            channel_id=str(instance.message.channel_id),
            user_id=str(instance.user_id),
            message_id=str(instance.message_id)
        )


@receiver(post_save, sender=User)
def update_user_presence(sender, instance, **kwargs):
    """
    Update user's online status and notify others when user logs in/out.
    """
    if hasattr(instance, 'is_online'):
        previous_state = user_presence.get(instance.id, {})
        
        # Check if online status changed
        if previous_state.get('is_online', None) != instance.is_online:
            # Update presence state
            user_presence[instance.id] = {
                'is_online': instance.is_online,
                'last_seen': timezone.now()
            }
            
            # Notify about presence change
            async_to_sync(notify_presence_update)(
                user_id=str(instance.id),
                is_online=instance.is_online,
                status=instance.status,
                status_emoji=instance.status_emoji
            )


@receiver(post_delete, sender=MessageReadStatus)
def handle_message_unread(sender, instance, **kwargs):
    """
    Handle message unread status when read status is deleted.
    """
    if instance.is_read:
        # Notify that message was unread
        async_to_sync(notify_message_read)(
            channel_id=str(instance.message.channel_id),
            user_id=str(instance.user_id),
            message_id=str(instance.message_id),
            is_read=False
        )


def user_logged_in(sender, user, request, **kwargs):
    """
    Signal handler for user login.
    """
    # Update user's online status
    with transaction.atomic():
        User.objects.filter(pk=user.pk).update(
            is_online=True,
            last_seen=timezone.now()
        )
    
    # Update presence state
    user_presence[user.id] = {
        'is_online': True,
        'last_seen': timezone.now()
    }
    
    # Notify about presence change
    async_to_sync(notify_presence_update)(
        user_id=str(user.id),
        is_online=True,
        status=user.status,
        status_emoji=user.status_emoji
    )


def user_logged_out(sender, user, request, **kwargs):
    """
    Signal handler for user logout.
    """
    # Update user's online status
    with transaction.atomic():
        User.objects.filter(pk=user.pk).update(
            is_online=False,
            last_seen=timezone.now()
        )
    
    # Update presence state
    user_presence[user.id] = {
        'is_online': False,
        'last_seen': timezone.now()
    }
    
    # Notify about presence change
    async_to_sync(notify_presence_update)(
        user_id=str(user.id),
        is_online=False,
        status=user.status,
        status_emoji=user.status_emoji
    )


# Connect signals
from django.contrib.auth.signals import user_logged_in as auth_user_logged_in
from django.contrib.auth.signals import user_logged_out as auth_user_logged_out

auth_user_logged_in.connect(user_logged_in)
auth_user_logged_out.connect(user_logged_out)
