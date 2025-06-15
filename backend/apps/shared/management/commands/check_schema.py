from django.core.management.base import BaseCommand
from django.db import connection
from django_tenants.utils import get_public_schema_name

class Command(BaseCommand):
    help = 'Check and fix the public schema'

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            # Check if public schema exists
            cursor.execute("""
                SELECT schema_name 
                FROM information_schema.schemata 
                WHERE schema_name = 'public';
            """)
            
            if not cursor.fetchone():
                self.stdout.write(self.style.WARNING('Public schema does not exist. Creating...'))
                cursor.execute('CREATE SCHEMA public;')
                self.stdout.write(self.style.SUCCESS('Created public schema'))
            else:
                self.stdout.write(self.style.SUCCESS('Public schema exists'))
            
            # Make sure the search path includes public
            cursor.execute('SHOW search_path;')
            search_path = cursor.fetchone()[0]
            self.stdout.write(f'Current search_path: {search_path}')
            
            if 'public' not in search_path:
                self.stdout.write(self.style.WARNING('public not in search_path. Updating...'))
                cursor.execute('SET search_path TO public;')
                self.stdout.write(self.style.SUCCESS('Updated search_path to include public'))
