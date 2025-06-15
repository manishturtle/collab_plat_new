"""
Management command to check Django Channels and Redis connection.
"""
import json
import logging
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.core.management.base import BaseCommand

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Check Django Channels and Redis connection'

    def handle(self, *args, **options):
        try:
            self.stdout.write("Testing Redis and Channels connection...")
            channel_layer = get_channel_layer()
            
            # Test sending a message to a test channel
            test_channel = 'test_channel'
            test_message = {'type': 'test.message', 'data': 'Test connection'}
            
            self.stdout.write("Sending test message...")
            # Send message
            async_to_sync(channel_layer.send)(test_channel, test_message)
            
            self.stdout.write("Attempting to receive message...")
            # Try to receive the message
            message = async_to_sync(channel_layer.receive)(test_channel)
            
            self.stdout.write(self.style.SUCCESS('[SUCCESS] Successfully connected to Redis and sent/received message:'))
            self.stdout.write(json.dumps(message, indent=2))
            return True
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'[ERROR] Error connecting to Redis/Channels: {str(e)}'))
            logger.exception('Error in check_channels command:')
            return False
