import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.conf import settings
from .models import ChatMessage, UserChannelState, ChatChannel, MessageReadStatus
from .utils import (
    get_channel_group_name,
    notify_message_read,
    notify_typing,
    notify_new_message
)

User = get_user_model()
logger = logging.getLogger(__name__)

class ChatConsumer(AsyncWebsocketConsumer):
    """Handle WebSocket connections for chat messages."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._is_connected = False
        self._is_closing = False
    
    async def connect(self):
        """Handle WebSocket connection."""
        if self._is_closing:
            return
            
        try:
            # Get user from scope (set by middleware)
            self.user = self.scope.get('user')
            
            # Check if user is authenticated
            if not self.user or not self.user.is_authenticated:
                logger.warning('Unauthenticated WebSocket connection attempt')
                self._is_closing = True
                await self.close(code=4000)  # Using 4000 for both auth and bad request for simplicity
                return
                
            self._is_connected = True
                
            # Get channel ID from URL route
            self.channel_id = self.scope['url_route']['kwargs'].get('channel_id')
            if not self.channel_id:
                logger.error('No channel_id in URL route')
                await self.close(code=4000)  # Bad request
                return
                
            # Set up group names
            self.room_group_name = get_channel_group_name(self.channel_id, 'chat')
            self.typing_group_name = get_channel_group_name(self.channel_id, 'typing')
            
            # Check if user has access to this channel
            has_access = await self.check_channel_access()
            if not has_access:
                logger.warning(f'User {self.user.id} denied access to channel {self.channel_id}')
                await self.close(code=4000)  # Using 4000 for Forbidden
                return

            # Join chat group
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            
            # Join typing group
            await self.channel_layer.group_add(
                self.typing_group_name,
                self.channel_name
            )
            
            # Mark user as online
            await self.set_user_online(True)
            
            # Accept the connection
            await self.accept()
            
            # Notify others in the channel that user has joined
            try:
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'user.join',
                        'user_id': str(self.user.id),
                        'username': self.user.username,
                        'timestamp': timezone.now().isoformat()
                    }
                )
                
                # Send channel info and recent messages
                await self.send_channel_info()
                await self.send_recent_messages()
                
                logger.info(f'WebSocket connection established for user {self.user.id} on channel {self.channel_id}')
                
            except Exception as e:
                logger.error(f'Error during WebSocket connection setup: {str(e)}', exc_info=True)
                await self.close(code=3000)  # Using 3000 for internal errors
                
        except Exception as e:
            logger.error(f'Unexpected error in WebSocket connect: {str(e)}', exc_info=True)
            await self.close(code=3000)  # Using 3000 for internal errors
    
    async def safe_send(self, message):
        """Safely send a message to the WebSocket, handling closed connections."""
        if not self._is_connected or self._is_closing:
            return False
            
        try:
            await self.send(text_data=json.dumps(message))
            return True
        except Exception as e:
            if "closed" not in str(e).lower():
                logger.warning(f"Failed to send message to WebSocket: {str(e)}")
            return False
            
    async def safe_group_send(self, group_name, message_type, message_data):
        """Safely send a message to a channel group."""
        if not self._is_connected or self._is_closing:
            return False
            
        try:
            await self.channel_layer.group_send(
                group_name,
                {
                    'type': message_type,
                    **message_data
                }
            )
            return True
        except Exception as e:
            if "closed" not in str(e).lower():
                logger.error(f"Failed to send message to group {group_name}: {str(e)}")
            return False
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection.
        
        Args:
            close_code: The close code or message from the WebSocket
        """
        if self._is_closing:
            return
            
        self._is_closing = True
        close_code_value = 1000  # Default normal closure
        
        try:
            # If we're being called with a message dict, extract the close code
            if isinstance(close_code, dict):
                close_code_value = close_code.get('code', 1000)
            elif isinstance(close_code, int):
                close_code_value = close_code
                
            # Only proceed with cleanup if we have the necessary attributes
            if not hasattr(self, 'room_group_name') or not hasattr(self, 'channel_name'):
                logger.warning("Disconnecting without room_group_name or channel_name")
                self._is_connected = False
                return await super().disconnect(close_code_value)
                
            # Only notify others if we have a user and they're authenticated
            if hasattr(self, 'user') and self.user and hasattr(self.user, 'is_authenticated') and self.user.is_authenticated:
                try:
                    # Notify others that user has left
                    await self.safe_group_send(
                        self.room_group_name,
                        'user.leave',
                        {
                            'user_id': str(self.user.id),
                            'username': self.user.username,
                            'timestamp': timezone.now().isoformat()
                        }
                    )
                    
                    # Mark user as offline
                    try:
                        await self.set_user_online(False)
                    except Exception as e:
                        logger.error(f"Error updating user online status: {str(e)}")
                        
                except Exception as e:
                    logger.error(f"Error notifying channel of user leave: {str(e)}", exc_info=True)
            
            # Always try to leave the groups if they exist
            group_leave_errors = False
            
            try:
                await self.channel_layer.group_discard(
                    self.room_group_name,
                    self.channel_name
                )
            except Exception as e:
                logger.error(f"Error leaving room group {self.room_group_name}: {str(e)}")
                group_leave_errors = True
                
            if hasattr(self, 'typing_group_name'):
                try:
                    await self.channel_layer.group_discard(
                        self.typing_group_name,
                        self.channel_name
                    )
                except Exception as e:
                    logger.error(f"Error leaving typing group {self.typing_group_name}: {str(e)}")
                    group_leave_errors = True
                    
            if group_leave_errors:
                logger.warning("Some group leave operations failed during disconnect")
                
        except Exception as e:
            if "closed" not in str(e).lower():
                logger.error(f"Unexpected error during WebSocket disconnect: {str(e)}", exc_info=True)
        finally:
            # Always ensure the connection is closed
            self._is_connected = False
            try:
                await super().disconnect(close_code_value)
            except Exception as e:
                if "closed" not in str(e).lower():
                    logger.error(f"Error during final WebSocket disconnect: {str(e)}")
                # Force close the connection
                try:
                    await self.close()
                except Exception:
                    pass  # Ignore any errors during forced close

    async def receive(self, text_data):
        """Handle incoming WebSocket messages."""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'chat.message':
                await self.handle_chat_message(data)
            elif message_type == 'typing':
                await self.handle_typing(data.get('is_typing', False))
            elif message_type == 'message.read':
                await self.handle_message_read(data.get('message_id'))
            elif message_type == 'heartbeat':
                # Simply respond with a heartbeat acknowledgement
                await self.safe_send({
                    'type': 'heartbeat.ack',
                    'timestamp': timezone.now().isoformat()
                })
            else:
                logger.warning(f'Unknown message type: {message_type}')
                
        except json.JSONDecodeError:
            await self.send_error('Invalid JSON format')
        except Exception as e:
            logger.error(f'Error processing message: {str(e)}')
            await self.send_error('An error occurred while processing your message')
    
    async def handle_chat_message(self, data):
        """Handle a new chat message."""
        content = data.get('content', '').strip()
        if not content:
            return
            
        # Save message to database
        message = await self.save_message(content, self.user)
        
        # Get user data for including in the message
        user_data = await self.get_user_data(self.user)
        
        # Prepare message data with explicitly included user information
        message_data = {
            'id': str(message.id),
            'content': message.content,
            'content_type': message.content_type,
            'sender_id': str(self.user.id),
            'user_id': str(self.user.id),
            'username': self.user.username,
            'first_name': self.user.first_name,  # Include first name directly
            'last_name': self.user.last_name,    # Include last name directly
            'full_name': f"{self.user.first_name} {self.user.last_name}".strip(),  # Include full name
            'timestamp': message.created_at.isoformat(),
            'is_read': False,
            'read_by': [],
            'attachments': [],
            # Include full user data object in standard format
            'user': {
                'id': self.user.id,
                'email': self.user.email,
                'first_name': self.user.first_name,
                'last_name': self.user.last_name,
                'full_name': f"{self.user.first_name} {self.user.last_name}".strip(),
                'username': self.user.username,
                'is_online': getattr(self.user, 'is_online', False)
            }
        }
        
        # Log the message data to confirm structure
        logger.info(f"Sending message with user data: {user_data}")
        
        # Notify all channel participants
        await notify_new_message(
            channel_id=self.channel_id,
            message_data=message_data
        )
        
        # Mark message as read by sender
        await self.mark_message_as_read(message.id)
    
    async def handle_typing(self, is_typing):
        """Handle typing indicator."""
        await notify_typing(
            channel_id=self.channel_id,
            user_id=self.user.id,
            is_typing=is_typing
        )
    
    async def handle_message_read(self, message_id):
        """Handle message read receipt."""
        if not message_id:
            return
            
        updated = await self.mark_message_as_read(message_id)
        if updated:
            await notify_message_read(
                channel_id=self.channel_id,
                user_id=self.user.id,
                message_id=message_id
            )
    
    # Message handlers for group events
    async def chat_message(self, event):
        """Handle chat message from group."""
        # Extract message and any additional data from the event
        message = event['message']
        
        # Log the incoming event structure for debugging
        logger.info(f"Received event to broadcast: {event}")
        
        # Get sender information from the message or event
        sender_id = message.get('sender_id') or message.get('user_id') or event.get('sender_id') or event.get('user_id')
        first_name = event.get('first_name') or message.get('first_name', '')
        last_name = event.get('last_name') or message.get('last_name', '')
        full_name = event.get('sender_name') or message.get('full_name', '')
        
        # CRITICAL: Check if this message was sent by the current user
        # If so, don't send it back to avoid duplication
        if sender_id and str(sender_id) == str(self.user.id):
            logger.info(f"Skipping echo of own message to avoid duplicate: {sender_id} == {self.user.id}")
            return
        
        # Make sure the message includes sender information
        if first_name and 'first_name' not in message:
            message['first_name'] = first_name
            
        if last_name and 'last_name' not in message:
            message['last_name'] = last_name
            
        if full_name and 'full_name' not in message:
            message['full_name'] = full_name
        
        # If not populated yet, try to get the full user data
        if 'user' not in message and sender_id:
            try:
                # Get user from database
                user_obj = await self.get_user_by_id(sender_id)
                if user_obj:
                    # Create complete user data
                    user_data = await self.get_user_data(user_obj)
                    message['user'] = user_data
                    logger.info(f"Added user data to message: {user_data}")
                    
                    # Also add basic fields at top level for compatibility
                    if not message.get('first_name'):
                        message['first_name'] = user_obj.first_name
                    if not message.get('last_name'):
                        message['last_name'] = user_obj.last_name
                    if not message.get('full_name'):
                        message['full_name'] = f"{user_obj.first_name} {user_obj.last_name}".strip()
                    if not message.get('username'):
                        message['username'] = user_obj.username
            except Exception as e:
                logger.error(f"Error adding user data to message: {str(e)}")
        
        # Set is_own flag for the receiver
        message['is_own'] = False  # Since we're skipping echo, this is always false
        
        # Create complete message with proper format
        websocket_message = {
            'type': 'chat.message',
            'message': message
        }
        
        # Log what we're sending to client
        logger.info(f"Sending to client: {websocket_message}")
        
        # Send the enhanced message
        await self.safe_send(websocket_message)
    
    async def typing_update(self, event):
        """Handle typing update from group."""
        await self.safe_send({
            'type': 'typing',
            'user_id': event['user_id'],
            'is_typing': event['is_typing']
        })
    
    async def message_read(self, event):
        """Handle message read receipt from group."""
        await self.safe_send({
            'type': 'message.read',
            'message_id': event['message_id'],
            'user_id': event['user_id']
        })
    
    async def user_join(self, event):
        """Handle user join notification."""
        await self.safe_send({
            'type': 'user.join',
            'user_id': event['user_id'],
            'username': event['username'],
            'timestamp': event['timestamp']
        })
    
    async def user_leave(self, event):
        """Handle user leave notification."""
        await self.safe_send({
            'type': 'user.leave',
            'user_id': event['user_id'],
            'username': event['username'],
            'timestamp': event['timestamp']
        })
    
    # Helper methods
    @database_sync_to_async
    def check_channel_access(self):
        """Check if user has access to this channel."""
        return ChatChannel.objects.filter(
            id=self.channel_id,
            participants=self.user
        ).exists()
    
    @database_sync_to_async
    def save_message(self, content, user):
        """Save message to database."""
        channel = ChatChannel.objects.get(id=self.channel_id)
        return ChatMessage.objects.create(
            channel=channel,
            user=user,
            content=content,
            content_type='text/plain'
        )
    
    @database_sync_to_async
    def mark_message_as_read(self, message_id):
        """Mark a message as read by the current user."""
        try:
            message = ChatMessage.objects.get(
                id=message_id,
                channel_id=self.channel_id
            )
            
            # Create or update read status
            # Note: MessageReadStatus doesn't have an is_read field, so we only set read_at
            _, created = MessageReadStatus.objects.update_or_create(
                message=message,
                user=self.user,
                defaults={
                    'read_at': timezone.now()
                }
            )
            return created
        except (ChatMessage.DoesNotExist, ValueError):
            return False
    
    @database_sync_to_async
    def set_user_online(self, is_online):
        """Update user's online status."""
        self.user.is_online = is_online
        if not is_online:
            self.user.last_seen = timezone.now()
        self.user.save(update_fields=['is_online', 'last_seen'])
        
    @database_sync_to_async
    def get_user_by_id(self, user_id):
        """Get a user by their ID.
        
        Args:
            user_id: The user ID to lookup
            
        Returns:
            User object if found, None otherwise
        """
        User = get_user_model()
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None
    
    @database_sync_to_async
    def get_user_data(self, user):
        """Get full user data for inclusion in message payload.
        
        This matches the structure returned by the REST API.
        
        Args:
            user: The user object to serialize
            
        Returns:
            dict: Dictionary with user information
        """
        return {
            'id': user.id,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'full_name': f"{user.first_name} {user.last_name}".strip(),
            'is_online': getattr(user, 'is_online', False),
        }
    
    async def send_channel_info(self):
        """Send channel information to the client."""
        try:
            channel = await self.get_channel_info()
            if channel:
                await self.safe_send({
                    'type': 'channel.info',
                    'channel': channel
                })
            else:
                logger.error(f"Failed to get channel info for channel {self.channel_id}")
        except Exception as e:
            logger.error(f"Error sending channel info: {str(e)}", exc_info=True)
    
    @database_sync_to_async
    def get_channel_info(self):
        """Get channel information."""
        try:
            from .serializers import ChatChannelSerializer
            from django.http import HttpRequest
            channel = ChatChannel.objects.get(id=self.channel_id)
            
            # Create a mock request object with the user
            mock_request = HttpRequest()
            mock_request.user = self.user
            
            return ChatChannelSerializer(channel, context={'request': mock_request}).data
        except Exception as e:
            logger.error(f"Error getting channel info: {str(e)}", exc_info=True)
            return None
        
    async def send_recent_messages(self, limit=50):
        """Send recent messages to the client."""
        try:
            messages = await self.get_recent_messages(limit)
            if messages is not None:
                await self.safe_send({
                    'type': 'messages.history',
                    'messages': messages
                })
        except Exception as e:
            logger.error(f"Error sending recent messages: {str(e)}", exc_info=True)
        
    @database_sync_to_async
    def get_recent_messages(self, limit):
        """Get recent messages for the channel."""
        from .serializers import ChatMessageSerializer
        messages = ChatMessage.objects.filter(
            channel_id=self.channel_id
        ).select_related('user').order_by('-created_at')[:limit]
        
        # Mark as read if requested
        read_messages = []
        for message in messages:
            if message.user_id != self.user.id:
                # Note: MessageReadStatus doesn't have an is_read field
                MessageReadStatus.objects.get_or_create(
                    message=message,
                    user=self.user,
                    defaults={'read_at': timezone.now()}
                )
            read_messages.append(message)
        
        from django.http import HttpRequest
        
        # Create a mock request object with the user
        mock_request = HttpRequest()
        mock_request.user = self.user
        
        return ChatMessageSerializer(
            read_messages,
            many=True,
            context={'request': mock_request}
        ).data
    
    async def send_error(self, message):
        """Send an error message to the client."""
        await self.send(text_data=json.dumps({
            'type': 'error',
            'message': message
        }))


class PresenceConsumer(AsyncWebsocketConsumer):
    """Handle user presence (online/offline status)."""
    
    async def connect(self):
        """Handle WebSocket connection for presence."""
        self.user = self.scope.get('user')
        if not self.user or not self.user.is_authenticated:
            await self.close(code=4003)  # Forbidden
            return
            
        self.user_id = str(self.user.id)
        self.presence_group = 'presence'
        self.user_presence_group = f'user_{self.user_id}'
        
        # Join presence groups
        await self.channel_layer.group_add(self.presence_group, self.channel_name)
        await self.channel_layer.group_add(self.user_presence_group, self.channel_name)
        
        # Mark user as online
        await self.set_user_online(True)
        
        # Get initial presence data
        await self.send_presence_update(is_online=True)
        
        # Send list of online users
        await self.send_online_users()
        
        await self.accept()
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection."""
        if hasattr(self, 'presence_group'):
            # Mark user as offline
            await self.set_user_online(False)
            
            # Notify others that user is offline
            await self.send_presence_update(is_online=False)
            
            # Leave groups
            await self.channel_layer.group_discard(
                self.presence_group,
                self.channel_name
            )
            await self.channel_layer.group_discard(
                self.user_presence_group,
                self.channel_name
            )
    
    async def receive(self, text_data):
        """Handle incoming WebSocket messages."""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'status.update':
                # Handle status update (e.g., away, busy, etc.)
                status = data.get('status')
                status_emoji = data.get('status_emoji')
                await self.update_user_status(status, status_emoji)
                
        except json.JSONDecodeError:
            logger.warning('Invalid JSON in presence message')
        except Exception as e:
            logger.error(f'Error processing presence message: {str(e)}')
    
    async def presence_update(self, event):
        """Handle presence update from group."""
        await self.send(text_data=json.dumps({
            'type': 'presence.update',
            'user_id': event['user_id'],
            'is_online': event['is_online'],
            'status': event.get('status'),
            'status_emoji': event.get('status_emoji'),
            'last_seen': event.get('last_seen')
        }))
    
    async def online_users(self, event):
        """Handle online users list update."""
        await self.send(text_data=json.dumps({
            'type': 'online.users',
            'users': event['users']
        }))
    
    async def send_presence_update(self, is_online):
        """Send presence update to all connected clients."""
        await self.channel_layer.group_send(
            self.presence_group,
            {
                'type': 'presence.update',
                'user_id': self.user_id,
                'is_online': is_online,
                'status': self.user.status,
                'status_emoji': self.user.status_emoji,
                'last_seen': self.user.last_seen.isoformat() if self.user.last_seen else None
            }
        )
    
    @database_sync_to_async
    def set_user_online(self, is_online):
        """Update user's online status in the database."""
        self.user.is_online = is_online
        if not is_online:
            self.user.last_seen = timezone.now()
        self.user.save(update_fields=['is_online', 'last_seen'])
    
    @database_sync_to_async
    def update_user_status(self, status=None, status_emoji=None):
        """Update user's status and notify others."""
        update_fields = []
        
        if status is not None and status != self.user.status:
            # Truncate status to match database field length constraint
            if status and len(status) > 10:
                status = status[:10]
                logger.warning(f"Status message truncated to 10 characters for user {self.user_id}")
            self.user.status = status
            update_fields.append('status')
            
        if status_emoji is not None and status_emoji != self.user.status_emoji:
            # Ensure emoji fits within the field limit
            if status_emoji and len(status_emoji) > 10:
                status_emoji = status_emoji[:10]
                logger.warning(f"Status emoji truncated to 10 characters for user {self.user_id}")
            self.user.status_emoji = status_emoji
            update_fields.append('status_emoji')
        
        if update_fields:
            self.user.save(update_fields=update_fields)
            
            # Notify others about the status change
            self.channel_layer.group_send(
                self.presence_group,
                {
                    'type': 'presence.update',
                    'user_id': self.user_id,
                    'is_online': self.user.is_online,
                    'status': self.user.status,
                    'status_emoji': self.user.status_emoji,
                    'last_seen': self.user.last_seen.isoformat() if self.user.last_seen else None
                }
            )
    
    @database_sync_to_async
    def get_online_users(self):
        """Get list of online users with their status."""
        from django.db.models import Q
        from ..serializers import UserStatusSerializer
        
        # Get users who were active in the last 5 minutes
        active_threshold = timezone.now() - timezone.timedelta(minutes=5)
        online_users = User.objects.filter(
            Q(is_online=True) | 
            Q(last_seen__gte=active_threshold)
        ).exclude(id=self.user.id).order_by('username')
        
        return UserStatusSerializer(online_users, many=True).data
    
    async def send_online_users(self):
        """Send list of online users to the client."""
        online_users = await self.get_online_users()
        await self.channel_layer.group_send(
            self.user_presence_group,
            {
                'type': 'online.users',
                'users': online_users
            }
        )


class TypingConsumer(AsyncWebsocketConsumer):
    """Handle typing indicators in chat."""
    
    async def connect(self):
        """Handle WebSocket connection for typing indicators."""
        self.user = self.scope.get('user')
        if not self.user or not self.user.is_authenticated:
            await self.close(code=4003)  # Forbidden
            return
            
        self.channel_id = self.scope['url_route']['kwargs']['channel_id']
        self.typing_group = f'typing_{self.channel_id}'
        self.user_typing_group = f'user_typing_{self.user.id}'
        
        # Check if user has access to this channel
        has_access = await self.check_channel_access()
        if not has_access:
            await self.close(code=4003)  # Forbidden
            return
        
        # Join typing groups
        await self.channel_layer.group_add(self.typing_group, self.channel_name)
        await self.channel_layer.group_add(self.user_typing_group, self.channel_name)
        
        await self.accept()
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection."""
        if hasattr(self, 'typing_group'):
            # Notify others that user stopped typing
            await self.channel_layer.group_send(
                self.typing_group,
                {
                    'type': 'typing.update',
                    'user_id': str(self.user.id),
                    'username': self.user.username,
                    'is_typing': False,
                    'is_disconnect': True
                }
            )
            
            # Leave groups
            await self.channel_layer.group_discard(self.typing_group, self.channel_name)
            await self.channel_layer.group_discard(self.user_typing_group, self.channel_name)
    
    async def receive(self, text_data):
        """Handle incoming typing indicators."""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'typing':
                is_typing = data.get('is_typing', False)
                await self.handle_typing_indicator(is_typing)
                
        except json.JSONDecodeError:
            logger.warning('Invalid JSON in typing message')
        except Exception as e:
            logger.error(f'Error processing typing message: {str(e)}')
    
    async def handle_typing_indicator(self, is_typing):
        """Handle typing indicator state change."""
        # Update typing status in the channel
        await self.channel_layer.group_send(
            self.typing_group,
            {
                'type': 'typing.update',
                'user_id': str(self.user.id),
                'username': self.user.username,
                'is_typing': is_typing,
                'timestamp': timezone.now().isoformat()
            }
        )
        
        # If user stopped typing, set a timeout to clear the typing state
        if not is_typing:
            await self.set_typing_timeout()
    
    async def typing_update(self, event):
        """Send typing update to WebSocket."""
        # Don't send the user's own typing status back to them
        if str(self.user.id) == event['user_id']:
            return
            
        await self.send(text_data=json.dumps({
            'type': 'typing',
            'user_id': event['user_id'],
            'username': event['username'],
            'is_typing': event['is_typing'],
            'timestamp': event.get('timestamp')
        }))
    
    async def set_typing_timeout(self):
        """Set a timeout to clear typing status if no further activity."""
        # This is a simplified example - in a real app, you'd use a proper task queue
        # or a more sophisticated approach with asyncio
        async def clear_typing():
            await asyncio.sleep(5)  # 5 seconds of inactivity
            await self.handle_typing_indicator(False)
        
        # Cancel any existing timeout task
        if hasattr(self, '_typing_timeout_task'):
            self._typing_timeout_task.cancel()
        
        # Create a new timeout task
        self._typing_timeout_task = asyncio.create_task(clear_typing())
    
    @database_sync_to_async
    def check_channel_access(self):
        """Check if user has access to this channel."""
        return ChatChannel.objects.filter(
            id=self.channel_id,
            participants=self.user
        ).exists()
