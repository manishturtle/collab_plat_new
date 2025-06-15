from django.core.management.base import BaseCommand
from django.db import connection
from django.conf import settings
from django_tenants.utils import schema_context
import logging
import re

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Fix foreign key constraints for a specific tenant'

    def add_arguments(self, parser):
        parser.add_argument('--schema', type=str, required=True, help='Tenant schema name')

    def get_foreign_keys(self, cursor, table_name):
        """Get all foreign key constraints for a table."""
        cursor.execute("""
            SELECT
                tc.constraint_name,
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
                AND tc.table_name = %s
        """, [table_name])
        return cursor.fetchall()

    def get_constraint_name(self, cursor, table_name, column_name):
        """Get the exact constraint name for a column."""
        cursor.execute("""
            SELECT conname 
            FROM pg_constraint 
            WHERE conrelid = %s::regclass
            AND conname LIKE %s
        """, [table_name, f'%{column_name}%'])
        result = cursor.fetchone()
        return result[0] if result else None

    def handle(self, *args, **options):
        schema_name = options['schema']
        
        with schema_context(schema_name):
            self.stdout.write(self.style.SUCCESS(f'Fixing foreign keys in schema: {schema_name}'))
            
            # Get the correct user model table
            user_table = 'ecomm_tenant_admins_tenantuser'  # From the actual table name in the database
            constraint_name = 'chat_channelparticipant_user_id_fk'  # The correct constraint name
            
            with connection.cursor() as cursor:
                try:
                    # First, check if the correct constraint already exists
                    cursor.execute("""
                        SELECT 1 
                        FROM information_schema.table_constraints 
                        WHERE table_name = 'chat_channelparticipant' 
                        AND constraint_name = %s
                    """, [constraint_name])
                    
                    if cursor.fetchone():
                        self.stdout.write(self.style.SUCCESS('Correct foreign key constraint already exists'))
                        return
                    
                    # Get all foreign key constraints on the table
                    fks = self.get_foreign_keys(cursor, 'chat_channelparticipant')
                    self.stdout.write(self.style.SUCCESS('Current foreign keys on chat_channelparticipant:'))
                    for fk in fks:
                        self.stdout.write(f"- {fk[0]}: {fk[1]} -> {fk[2]}.{fk[3]}")
                    
                    # Find any existing constraint on user_id
                    existing_constraint = next((fk for fk in fks if fk[1] == 'user_id'), None)
                    
                    # If there's an existing constraint, drop it
                    if existing_constraint:
                        drop_sql = f"""
                            ALTER TABLE chat_channelparticipant 
                            DROP CONSTRAINT IF EXISTS {existing_constraint[0]} CASCADE
                        """
                        self.stdout.write(self.style.WARNING(f'Dropping constraint: {existing_constraint[0]}'))
                        cursor.execute(drop_sql)
                    
                    # Add the new constraint
                    add_sql = f"""
                        ALTER TABLE chat_channelparticipant 
                        ADD CONSTRAINT {constraint_name}
                        FOREIGN KEY (user_id) REFERENCES {user_table} (id)
                        DEFERRABLE INITIALLY DEFERRED
                    """
                    self.stdout.write(self.style.SUCCESS(f'Adding constraint: {constraint_name}'))
                    cursor.execute(add_sql)
                    
                    self.stdout.write(self.style.SUCCESS('Successfully fixed foreign key constraints'))
                    
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error fixing foreign keys: {str(e)}'))
                    raise
