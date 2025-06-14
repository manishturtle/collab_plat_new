"""
App configuration for the shared app.
"""
from django.apps import AppConfig


class SharedConfig(AppConfig):
    """Configuration for the shared app."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.shared'
    label = 'shared'
