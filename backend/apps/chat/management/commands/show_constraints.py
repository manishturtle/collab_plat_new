from django.core.management.base import BaseCommand
from django.db import connection
from django_tenants.utils import schema_context

class Command(BaseCommand):
    help = 'Show all constraints in the database'

    def handle(self, *args, **options):
        with schema_context('turtlesoftware'):
            with connection.cursor() as cursor:
                # Get all foreign key constraints on chat_channelparticipant
                cursor.execute("""
                    SELECT 
                        tc.constraint_name,
                        tc.table_name,
                        kcu.column_name,
                        ccu.table_name AS foreign_table_name,
                        ccu.column_name AS foreign_column_name
                    FROM 
                        information_schema.table_constraints AS tc 
                        JOIN information_schema.key_column_usage AS kcu
                            ON tc.constraint_name = kcu.constraint_name
                            AND tc.table_schema = kcu.table_schema
                        JOIN information_schema.constraint_column_usage AS ccu
                            ON ccu.constraint_name = tc.constraint_name
                            AND ccu.table_schema = tc.table_schema
                    WHERE 
                        tc.constraint_type = 'FOREIGN KEY'
                        AND tc.table_name = 'chat_channelparticipant'
                    ORDER BY 
                        tc.table_name, 
                        kcu.column_name
                """)
                
                self.stdout.write(self.style.SUCCESS('Foreign key constraints for chat_channelparticipant:'))
                for row in cursor.fetchall():
                    self.stdout.write(f"- {row[0]}: {row[1]}.{row[2]} -> {row[3]}.{row[4]}")
                
                # Also check from pg_constraint
                self.stdout.write(self.style.SUCCESS('\nForeign keys from pg_constraint:'))
                cursor.execute("""
                    SELECT 
                        conname,
                        conrelid::regclass,
                        pg_get_constraintdef(oid)
                    FROM 
                        pg_constraint 
                    WHERE 
                        conrelid = 'chat_channelparticipant'::regclass
                        AND contype = 'f'
                """)
                for row in cursor.fetchall():
                    self.stdout.write(f"- {row[0]}: {row[1]} {row[2]}")
