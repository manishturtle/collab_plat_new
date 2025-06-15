from django.core.management.base import BaseCommand
from django.db import connection
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Fix foreign key constraints for TenantUserModel'

    def add_arguments(self, parser):
        parser.add_argument('--schema', type=str, help='Schema name to apply fix to')

    def handle(self, *args, **options):
        schema = options.get('schema')
        if not schema:
            self.stderr.write(self.style.ERROR('Schema name is required'))
            return

        self.stdout.write(f"Fixing foreign key constraints in schema: {schema}")
        
        with connection.cursor() as cursor:
            # Set the search path to the tenant schema
            cursor.execute(f'SET search_path TO {schema}')
            
            # List of tables with user_id foreign keys
            tables = [
                'chat_channelparticipant',
                'chat_chatmessage',
                'chat_messagereadstatus',
                'chat_userchannelstate',
                'chat_device'
            ]
            
            for table in tables:
                # Check if table exists
                cursor.execute(f"""SELECT to_regclass('{table}')""")
                if cursor.fetchone()[0] is None:
                    self.stdout.write(f"Table '{table}' does not exist, skipping")
                    continue
                
                self.stdout.write(f"Processing table: {table}")
                
                # Find all constraints referencing auth_user
                cursor.execute(f"""
                    SELECT con.conname
                    FROM pg_constraint con 
                    JOIN pg_class rel ON rel.oid = con.conrelid
                    JOIN pg_namespace nsp ON nsp.oid = rel.relnamespace
                    JOIN pg_attribute att ON att.attrelid = rel.oid AND att.attnum = ANY(con.conkey)
                    JOIN pg_class rel_ref ON rel_ref.oid = con.confrelid
                    WHERE con.contype = 'f'
                    AND rel.relname = '{table}'
                    AND att.attname = 'user_id'
                    AND rel_ref.relname = 'auth_user'
                """)
                constraints = cursor.fetchall()
                
                if constraints:
                    for constraint in constraints:
                        constraint_name = constraint[0]
                        self.stdout.write(f"Found constraint on {table}: {constraint_name} referencing auth_user")
                        
                        # Drop the existing constraint
                        try:
                            cursor.execute(f"ALTER TABLE {table} DROP CONSTRAINT IF EXISTS {constraint_name}")
                            self.stdout.write(self.style.SUCCESS(f"Dropped constraint: {constraint_name}"))
                        except Exception as e:
                            self.stderr.write(self.style.ERROR(f"Error dropping constraint {constraint_name}: {e}"))
                else:
                    self.stdout.write(f"No auth_user constraints found for {table}")
                
                # Check if the table has a user_id column
                cursor.execute(f"""SELECT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = '{table}' AND column_name = 'user_id')""")
                has_user_id = cursor.fetchone()[0]
                
                if not has_user_id:
                    self.stdout.write(f"Table {table} does not have user_id column, skipping")
                    continue
                    
                # Check if the table already has a foreign key to ecomm_tenant_admins_tenantuser
                cursor.execute(f"""
                    SELECT COUNT(*)
                    FROM pg_constraint con 
                    JOIN pg_class rel ON rel.oid = con.conrelid
                    JOIN pg_class rel_ref ON rel_ref.oid = con.confrelid
                    WHERE con.contype = 'f'
                    AND rel.relname = '{table}'
                    AND rel_ref.relname = 'ecomm_tenant_admins_tenantuser'
                """)
                has_tenantusermodel_fk = cursor.fetchone()[0] > 0
                
                if not has_tenantusermodel_fk:
                    # Add new constraint to ecomm_tenant_admins_tenantuser
                    try:
                        new_constraint_name = f"{table}_user_id_tenantusermodel_fk"
                        cursor.execute(f"""
                            ALTER TABLE {table}
                            ADD CONSTRAINT {new_constraint_name}
                            FOREIGN KEY (user_id) REFERENCES ecomm_tenant_admins_tenantuser(id)
                            ON DELETE CASCADE
                        """)
                        self.stdout.write(self.style.SUCCESS(f"Added constraint {new_constraint_name} to {table}"))
                    except Exception as e:
                        self.stderr.write(self.style.ERROR(f"Error adding constraint to {table}: {e}"))
                else:
                    self.stdout.write(f"Table {table} already has foreign key to ecomm_tenant_admins_tenantuser")
            
            self.stdout.write(self.style.SUCCESS('Foreign key constraint update process completed'))
