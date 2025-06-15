from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Fix all foreign key constraints referencing auth_user in chat-related tables'

    def add_arguments(self, parser):
        parser.add_argument('--schema', type=str, required=True, help='Schema name to apply fix to')

    def handle(self, *args, **options):
        schema = options.get('schema')
        
        # Direct SQL approach
        with connection.cursor() as cursor:
            # Set the search path to the tenant schema
            cursor.execute(f'SET search_path TO {schema}')
            
            # First check what constraints actually exist
            cursor.execute("""
                SELECT conname, conrelid::regclass as table_name, confrelid::regclass as referenced_table, pg_get_constraintdef(oid) as constraint_def
                FROM pg_constraint
                WHERE contype = 'f' 
                AND conrelid::regclass::text LIKE 'chat%'
                AND confrelid::regclass::text = 'auth_user'
            """)
            constraints = cursor.fetchall()
            
            if not constraints:
                self.stdout.write(self.style.SUCCESS('No auth_user constraints found'))
                return
                
            self.stdout.write(f"Found {len(constraints)} constraints referencing auth_user:")
            for constraint in constraints:
                self.stdout.write(f"Found constraint '{constraint[0]}' on table '{constraint[1]}' referencing '{constraint[2]}'")
            
            # Process each constraint
            for constraint in constraints:
                constraint_name = constraint[0]
                table_name = constraint[1]
                
                # Extract column name from constraint definition
                constraint_def = constraint[3]
                
                # Parse the column name from the constraint definition
                import re
                match = re.search(r'FOREIGN KEY \(([^)]+)\)', constraint_def)
                if match:
                    column_name = match.group(1)
                    self.stdout.write(f"Processing constraint {constraint_name} on table {table_name}, column {column_name}")
                    
                    try:
                        # Drop the constraint
                        cursor.execute(f"""
                            ALTER TABLE {table_name} 
                            DROP CONSTRAINT IF EXISTS {constraint_name}
                        """)
                        self.stdout.write(self.style.SUCCESS(f"Dropped constraint: {constraint_name}"))
                        
                        # Add the new constraint
                        new_constraint_name = f"{table_name}_{column_name}_fk_tenant_user"
                        cursor.execute(f"""
                            ALTER TABLE {schema}.{table_name} 
                            ADD CONSTRAINT {new_constraint_name} 
                            FOREIGN KEY ({column_name}) REFERENCES {schema}.ecomm_tenant_admins_tenantuser(id) 
                            ON DELETE CASCADE
                        """)
                        self.stdout.write(self.style.SUCCESS(f"Added new constraint {new_constraint_name} on {table_name}.{column_name}"))
                        
                    except Exception as e:
                        self.stderr.write(self.style.ERROR(f"Error processing {constraint_name}: {e}"))
                else:
                    self.stderr.write(self.style.ERROR(f"Could not extract column name from constraint {constraint_name}: {constraint_def}"))
            
            # Force analyze to update statistics
            cursor.execute(f"ANALYZE {schema}.ecomm_tenant_admins_tenantuser")
            for constraint in constraints:
                table_name = constraint[1]
                try:
                    cursor.execute(f"ANALYZE {schema}.{table_name}")
                except Exception as e:
                    self.stderr.write(self.style.ERROR(f"Error analyzing {table_name}: {e}"))
            
            # Verify all chat tables using auth_user now point to tenant user model
            cursor.execute("""
                SELECT conname, conrelid::regclass as table_name, confrelid::regclass as referenced_table
                FROM pg_constraint
                WHERE contype = 'f' 
                AND conrelid::regclass::text LIKE 'chat%'
                ORDER BY conrelid::regclass::text, conname
            """)
            after_constraints = cursor.fetchall()
            
            self.stdout.write(self.style.SUCCESS(f"\nAfter fixes - Constraints on chat tables:"))
            for constraint in after_constraints:
                self.stdout.write(f"{constraint[1]}.{constraint[0]} -> {constraint[2]}")
            
            # Final check for any remaining auth_user references
            cursor.execute("""
                SELECT COUNT(*)
                FROM pg_constraint
                WHERE contype = 'f' 
                AND conrelid::regclass::text LIKE 'chat%'
                AND confrelid::regclass::text = 'auth_user'
            """)
            remaining = cursor.fetchone()[0]
            
            if remaining > 0:
                self.stderr.write(self.style.WARNING(f"There are still {remaining} constraints referencing auth_user!"))
            else:
                self.stdout.write(self.style.SUCCESS("All auth_user constraints have been successfully replaced!"))
