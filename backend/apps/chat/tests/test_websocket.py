"""
Tests for WebSocket functionality in the chat application.
"""
import json
import pytest
from channels.testing import WebsocketCommunicator
from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework_simplejwt.tokens import AccessToken

from config.asgi import application
from apps.chat.consumers import ChatConsumer, PresenceConsumer, TypingConsumer

User = get_user_model()

class TestChatWebSocket(TestCase):
    """Test WebSocket connections and message handling."""
    
    @classmethod
    def setUpTestData(cls):
        """Set up test data."""
        cls.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        cls.token = str(AccessToken.for_user(cls.user))
    
    async def test_connect_to_chat_consumer(self):
        """Test connecting to the chat consumer."""
        communicator = WebsocketCommunicator(
            application,
            f'/ws/chat/test-channel/?token={self.token}'
        )
        connected, _ = await communicator.connect()
        self.assertTrue(connected)
        
        # Test sending a message
        message = {
            'type': 'chat_message',
            'message': 'Hello, world!',
            'channel_id': 'test-channel'
        }
        await communicator.send_json_to(message)
        
        # Test receiving a message
        response = await communicator.receive_json_from()
        self.assertIn('message', response)
        
        # Clean up
        await communicator.disconnect()
    
    async def test_connect_to_presence_consumer(self):
        """Test connecting to the presence consumer."""
        communicator = WebsocketCommunicator(
            application,
            f'/ws/presence/?token={self.token}'
        )
        connected, _ = await communicator.connect()
        self.assertTrue(connected)
        
        # Test receiving presence update
        response = await communicator.receive_json_from()
        self.assertIn('type', response)
        self.assertEqual(response['type'], 'presence.update')
        
        # Clean up
        await communicator.disconnect()
    
    async def test_connect_to_typing_consumer(self):
        """Test connecting to the typing consumer."""
        communicator = WebsocketCommunicator(
            application,
            f'/ws/typing/test-channel/?token={self.token}'
        )
        connected, _ = await communicator.connect()
        self.assertTrue(connected)
        
        # Test sending a typing indicator
        typing_message = {
            'type': 'typing',
            'is_typing': True,
            'channel_id': 'test-channel'
        }
        await communicator.send_json_to(typing_message)
        
        # Clean up
        await communicator.disconnect()


@pytest.mark.asyncio
async def test_websocket_connection():
    """Test WebSocket connection with authentication."""
    # Create a test user
    user = await User.objects.acreate(
        username='testuser2',
        email='test2@example.com',
        password='testpass123'
    )
    
    # Generate JWT token
    token = str(AccessToken.for_user(user))
    
    # Connect to WebSocket
    communicator = WebsocketCommunicator(
        application,
        f'/ws/chat/test-channel/?token={token}'
    )
    connected, _ = await communicator.connect()
    assert connected
    
    # Send a test message
    await communicator.send_json_to({
        'type': 'chat_message',
        'message': 'Test message',
        'channel_id': 'test-channel'
    })
    
    # Receive the response
    response = await communicator.receive_json_from()
    assert 'message' in response
    
    # Clean up
    await communicator.disconnect()
