"""
Management command to start a Redis server for local development.
"""
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

from django.core.management.base import BaseCommand
from django.conf import settings
import django


class Command(BaseCommand):
    """Start a Redis server for local development."""
    
    help = 'Start a Redis server for local development'
    
    def add_arguments(self, parser):
        """Add command line arguments."""
        parser.add_argument(
            '--port',
            type=int,
            default=6380,  # Changed default port to 6380
            help='Port to run Redis on (default: 6380)'
        )
        parser.add_argument(
            '--bind',
            default='127.0.0.1',
            help='Bind address (default: 127.0.0.1)'
        )
        parser.add_argument(
            '--dir',
            default=os.path.join(Path(__file__).resolve().parent.parent.parent.parent.parent, 'redis_data'),
            help='Directory to store Redis data (default: <project_root>/redis_data)'
        )
    
    def handle(self, *args, **options):
        """Handle the command."""
        # Configure Django settings
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
        
        # Initialize Django without importing models
        django.setup(set_prefix=False)
        
        port = options['port']
        bind = options['bind']
        data_dir = options['dir']
        
        # Create data directory if it doesn't exist
        os.makedirs(data_dir, exist_ok=True)
        
        # Build the Redis server command
        cmd = [
            'redis-server',
            '--port', str(port),
            '--bind', bind,
            '--dir', data_dir,
            '--save', '""',  # Disable persistence for development
            '--appendonly', 'no',
        ]
        
        self.stdout.write(self.style.SUCCESS(f'Starting Redis server on {bind}:{port}...'))
        self.stdout.write(self.style.SUCCESS(f'Data directory: {data_dir}'))
        self.stdout.write('Press Ctrl+C to stop the server')
        
        try:
            # Start the Redis server
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            
            # Stream the output
            for line in process.stdout:
                self.stdout.write(line.strip())
            
            # Wait for the process to complete
            process.wait()
            
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING('Stopping Redis server...'))
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
            self.stdout.write(self.style.SUCCESS('Redis server stopped'))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Error: {str(e)}'))
            sys.exit(1)
        
        sys.exit(process.returncode)