from django.core.management.base import BaseCommand
from django.db import connection
from django_tenants.utils import schema_context

class Command(BaseCommand):
    help = 'Check foreign key constraints for chat models'

    def handle(self, *args, **options):
        with schema_context('turtlesoftware'):
            with connection.cursor() as cursor:
                # Check foreign keys for chat_channelparticipant
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
                        AND tc.table_name IN ('chat_channelparticipant')
                """)
                
                self.stdout.write(self.style.SUCCESS('Foreign key constraints for chat_channelparticipant:'))
                for row in cursor.fetchall():
                    self.stdout.write(f"- {row[0]}: {row[1]}.{row[2]} -> {row[3]}.{row[4]}")
                
                # Check if the user exists in the tenant user table
                cursor.execute("SELECT id, email FROM ecomm_tenant_admins_tenantuser LIMIT 5")
                users = cursor.fetchall()
                self.stdout.write(self.style.SUCCESS('\nFirst 5 users in ecomm_tenant_admins_tenantuser:'))
                for user in users:
                    self.stdout.write(f"- ID: {user[0]}, Email: {user[1]}")
