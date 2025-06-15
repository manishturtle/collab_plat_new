from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'List all schemas in the database'

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT schema_name 
                FROM information_schema.schemata 
                WHERE schema_name NOT IN ('pg_catalog', 'information_schema', 'pg_toast')
                ORDER BY schema_name;
            """)
            schemas = cursor.fetchall()
            
            self.stdout.write(self.style.SUCCESS('Available schemas:'))
            for schema in schemas:
                self.stdout.write(f'- {schema[0]}')
