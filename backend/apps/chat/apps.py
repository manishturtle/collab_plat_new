"""
App configuration for the chat application.
"""
import logging
import os
from django.apps import AppConfig
from django.conf import settings

logger = logging.getLogger(__name__)


class ChatConfig(AppConfig):
    """Configuration for the chat application."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.chat'
    
    def ready(self):
        """Initialize the chat application."""
        # Skip if we're running management commands that don't need the full app stack
        is_running_migrations = 'makemigrations' in os.sys.argv or 'migrate' in os.sys.argv
        is_running_tests = 'test' in os.sys.argv
        
        if is_running_migrations or is_running_tests:
            return
            
        # Only import and initialize channels layer when running the server
        if 'runserver' in os.sys.argv or 'daphne' in os.sys.argv or 'uvicorn' in os.sys.argv:
            self._initialize_channels()
    
    def _initialize_channels(self):
        """Initialize Django Channels components."""
        try:
            # Import signals
            import apps.chat.signals  # noqa
            logger.info('Chat signals imported successfully')
            
            # Initialize channel layer
            from channels.layers import get_channel_layer
            get_channel_layer()
            logger.info('Channel layer initialized successfully')
            
        except ImportError as e:
            logger.error(f'Failed to initialize chat components: {e}')
        except Exception as e:
            logger.error(f'Error initializing chat components: {e}')
