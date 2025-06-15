from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Mark migrations as applied for a specific tenant'

    def handle(self, *args, **options):
        # Get the tenant's schema name
        schema_name = 'bingo_travels'
        
        # Set the search path to the tenant's schema
        with connection.cursor() as cursor:
            # Switch to the tenant's schema
            cursor.execute(f'SET search_path TO {schema_name}')
            
            # Check if django_migrations table exists
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = %s 
                    AND table_name = 'django_migrations'
                )
            """, [schema_name])
            
            if not cursor.fetchone()[0]:
                # Create django_migrations table if it doesn't exist
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS django_migrations (
                        id SERIAL PRIMARY KEY,
                        app VARCHAR(255) NOT NULL,
                        name VARCHAR(255) NOT NULL,
                        applied TIMESTAMP WITH TIME ZONE NOT NULL
                    )
                """)
                self.stdout.write(self.style.SUCCESS(f'Created django_migrations table in schema {schema_name}'))
            
            # Mark shared.0001_initial as applied
            cursor.execute("""
                INSERT INTO django_migrations (app, name, applied)
                SELECT 'shared', '0001_initial', NOW()
                WHERE NOT EXISTS (
                    SELECT 1 FROM django_migrations 
                    WHERE app = 'shared' AND name = '0001_initial'
                )
            """)
            
            # Mark shared.0002_... as applied
            cursor.execute("""
                INSERT INTO django_migrations (app, name, applied)
                SELECT 'shared', '0002_tenantusermodel_avatar_url_tenantusermodel_is_online_and_more', NOW()
                WHERE NOT EXISTS (
                    SELECT 1 FROM django_migrations 
                    WHERE app = 'shared' AND name = '0002_tenantusermodel_avatar_url_tenantusermodel_is_online_and_more'
                )
            """)
            
            # Mark shared.0003_... as applied
            cursor.execute("""
                INSERT INTO django_migrations (app, name, applied)
                SELECT 'shared', '0003_fix_tenant_user_table', NOW()
                WHERE NOT EXISTS (
                    SELECT 1 FROM django_migrations 
                    WHERE app = 'shared' AND name = '0003_fix_tenant_user_table'
                )
            """)
            
            self.stdout.write(self.style.SUCCESS(f'Successfully marked migrations as applied for schema {schema_name}'))
            
            # Reset search path
            cursor.execute('SET search_path TO public')
