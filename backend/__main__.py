#!/usr/bin/env python
"""
Entry point for running the Django development server with WebSocket support.
"""
import os
import sys

def main():
    """Run the Django development server with WebSocket support."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    
    # Check if the runserver command is being used
    if len(sys.argv) >= 2 and sys.argv[1] == 'runserver':
        # Add channels development server if not already present
        if '--noasgi' not in sys.argv and '--asgi' not in sys.argv:
            sys.argv.append('--asgi')
    
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
