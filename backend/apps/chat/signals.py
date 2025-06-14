"""
Signals for the chat application.
"""
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from .models import ChatMessage as Message, ChatChannel as ChatRoom
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


@receiver(post_save, sender=Message)
def notify_chat_room(sender, instance, created, **kwargs):
    """
    Notify all participants in a chat room when a new message is created.
    """
    if created:
        # Update the channel's updated_at timestamp
        ChatRoom.objects.filter(id=instance.channel.id).update(updated_at=timezone.now())
        
        # Notify all participants in the chat room via WebSocket
        channel_layer = get_channel_layer()
        room_group_name = f'chat_{instance.room.id}'
        
        # Send message to room group
        async_to_sync(channel_layer.group_send)(
            room_group_name,
            {
                'type': 'chat_message',
                'message': {
                    'id': instance.id,
                    'room_id': instance.room.id,
                    'room_name': instance.room.name,
                    'sender': {
                        'id': instance.sender.id,
                        'username': instance.sender.username,
                        'email': instance.sender.email,
                    },
                    'content': instance.content,
                    'timestamp': instance.timestamp.isoformat(),
                    'is_read': instance.is_read,
                },
                'event_type': 'new_message'
            }
        )


@receiver(pre_save, sender=Message)
def update_message_timestamp(sender, instance, **kwargs):
    """
    Update the timestamp when a message is modified.
    """
    if not instance.pk:  # New message
        instance.timestamp = timezone.now()
