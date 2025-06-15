from django.core.management.base import BaseCommand
from django_tenants.utils import schema_context
from django.db import connection

class Command(BaseCommand):
    help = 'Check foreign key constraints in chat_channelparticipant table'

    def handle(self, *args, **options):
        with schema_context('bingo_travels'):
            with connection.cursor() as cursor:
                # Query to check foreign key constraints
                cursor.execute("""
                SELECT
                    tc.constraint_name,
                    tc.table_schema,
                    tc.table_name,
                    kcu.column_name,
                    ccu.table_schema AS foreign_table_schema,
                    ccu.table_name AS foreign_table_name,
                    ccu.column_name AS foreign_column_name
                FROM
                    information_schema.table_constraints tc
                    JOIN information_schema.key_column_usage kcu ON tc.constraint_name = kcu.constraint_name
                    JOIN information_schema.constraint_column_usage ccu ON ccu.constraint_name = tc.constraint_name
                WHERE
                    tc.constraint_type = 'FOREIGN KEY'
                    AND tc.table_name = 'chat_channelparticipant'
                    AND tc.table_schema = 'bingo_travels'
                ORDER BY tc.constraint_name;
                """)
                
                constraints = cursor.fetchall()
                
                self.stdout.write(self.style.SUCCESS(f'Found {len(constraints)} constraints:'))
                for constraint in constraints:
                    self.stdout.write(str(constraint))
                
                # Also check if the required auth_user table exists
                cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'bingo_travels' 
                    AND table_name = 'auth_user'
                );
                """)
                auth_user_exists = cursor.fetchone()[0]
                self.stdout.write(self.style.SUCCESS(f'auth_user table exists: {auth_user_exists}'))
                
                # Check what user table exists
                cursor.execute("""
                SELECT table_name FROM information_schema.tables 
                WHERE table_schema = 'bingo_travels' 
                AND table_name LIKE '%user%';
                """)
                user_tables = cursor.fetchall()
                self.stdout.write(self.style.SUCCESS(f'User-related tables:'))
                for table in user_tables:
                    self.stdout.write(str(table))
