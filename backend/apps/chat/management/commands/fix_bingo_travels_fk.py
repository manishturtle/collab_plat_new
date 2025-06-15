from django.core.management.base import BaseCommand
from django_tenants.utils import schema_context
from django.db import connection

class Command(BaseCommand):
    help = 'Fix foreign key constraint in bingo_travels schema'

    def handle(self, *args, **options):
        with schema_context('bingo_travels'):
            with connection.cursor() as cursor:
                self.stdout.write(self.style.SUCCESS('Fixing foreign key constraints in bingo_travels schema...'))
                
                # Check for existing constraints
                cursor.execute("""
                SELECT conname
                FROM pg_constraint
                JOIN pg_class ON pg_constraint.conrelid = pg_class.oid
                JOIN pg_namespace ON pg_class.relnamespace = pg_namespace.oid
                WHERE pg_namespace.nspname = 'bingo_travels'
                AND pg_class.relname = 'chat_channelparticipant'
                AND pg_constraint.conname LIKE '%user_id%'
                AND pg_constraint.contype = 'f';
                """)
                constraints = cursor.fetchall()
                self.stdout.write(f'Found {len(constraints)} user_id foreign key constraints:')
                for constraint in constraints:
                    self.stdout.write(str(constraint[0]))
                
                # Check if the problematic constraint exists
                cursor.execute("""
                SELECT EXISTS (
                    SELECT 1 FROM pg_constraint 
                    JOIN pg_class ON pg_constraint.conrelid = pg_class.oid
                    JOIN pg_namespace ON pg_class.relnamespace = pg_namespace.oid
                    WHERE pg_namespace.nspname = 'bingo_travels'
                    AND pg_class.relname = 'chat_channelparticipant'
                    AND conname = 'chat_channelparticipant_user_id_beeb51d8_fk_auth_user_id'
                );
                """)
                constraint_exists = cursor.fetchone()[0]
                
                if constraint_exists:
                    self.stdout.write(self.style.SUCCESS('Found problematic constraint, dropping it...'))
                    # Drop the problematic constraint
                    cursor.execute("""
                    ALTER TABLE bingo_travels.chat_channelparticipant 
                    DROP CONSTRAINT chat_channelparticipant_user_id_beeb51d8_fk_auth_user_id;
                    """)
                    self.stdout.write(self.style.SUCCESS('Constraint dropped successfully'))
                else:
                    self.stdout.write(self.style.WARNING('Problematic constraint not found, checking for similar constraints...'))
                    # Find any constraint referencing auth_user
                    cursor.execute("""
                    SELECT conname
                    FROM pg_constraint c
                    JOIN pg_class rel ON c.conrelid = rel.oid
                    JOIN pg_class referenced_rel ON c.confrelid = referenced_rel.oid
                    JOIN pg_namespace rel_ns ON rel.relnamespace = rel_ns.oid
                    JOIN pg_namespace referenced_rel_ns ON referenced_rel.relnamespace = referenced_rel_ns.oid
                    WHERE rel_ns.nspname = 'bingo_travels'
                    AND rel.relname = 'chat_channelparticipant'
                    AND c.contype = 'f'
                    AND referenced_rel.relname = 'auth_user';
                    """)
                    auth_user_constraints = cursor.fetchall()
                    
                    if auth_user_constraints:
                        for constraint in auth_user_constraints:
                            constraint_name = constraint[0]
                            self.stdout.write(f'Dropping constraint: {constraint_name}')
                            cursor.execute(f"""
                            ALTER TABLE bingo_travels.chat_channelparticipant 
                            DROP CONSTRAINT "{constraint_name}";
                            """)
                        self.stdout.write(self.style.SUCCESS('All auth_user constraints dropped'))
                    else:
                        self.stdout.write(self.style.WARNING('No auth_user constraints found'))
                
                # Check if the correct constraint already exists
                cursor.execute("""
                SELECT conname
                FROM pg_constraint c
                JOIN pg_class rel ON c.conrelid = rel.oid
                JOIN pg_class referenced_rel ON c.confrelid = referenced_rel.oid
                JOIN pg_namespace rel_ns ON rel.relnamespace = rel_ns.oid
                JOIN pg_namespace referenced_rel_ns ON referenced_rel.relnamespace = referenced_rel_ns.oid
                WHERE rel_ns.nspname = 'bingo_travels'
                AND rel.relname = 'chat_channelparticipant'
                AND c.contype = 'f'
                AND referenced_rel_ns.nspname = 'bingo_travels'
                AND referenced_rel.relname = 'ecomm_tenant_admins_tenantuser'
                AND c.confkey[1] = (
                    SELECT attnum
                    FROM pg_attribute
                    WHERE attrelid = referenced_rel.oid
                    AND attname = 'id'
                );
                """)
                correct_constraints = cursor.fetchall()
                
                if correct_constraints:
                    self.stdout.write(self.style.SUCCESS('Correct constraints already exist:'))
                    for constraint in correct_constraints:
                        self.stdout.write(str(constraint[0]))
                else:
                    self.stdout.write(self.style.WARNING('No correct constraints found, adding one...'))
                    # Add the correct constraint
                    try:
                        cursor.execute("""
                        ALTER TABLE bingo_travels.chat_channelparticipant
                        ADD CONSTRAINT chat_channelparticipant_user_id_custom_fk
                        FOREIGN KEY (user_id)
                        REFERENCES bingo_travels.ecomm_tenant_admins_tenantuser(id)
                        ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;
                        """)
                        self.stdout.write(self.style.SUCCESS('Added correct foreign key constraint'))
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f'Error adding constraint: {e}'))
                
                # Final check of constraints
                cursor.execute("""
                SELECT 
                    tc.constraint_name,
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
                    AND kcu.column_name = 'user_id'
                ORDER BY tc.constraint_name;
                """)
                final_constraints = cursor.fetchall()
                
                self.stdout.write(self.style.SUCCESS(f'Final user_id constraints ({len(final_constraints)}):'))
                for constraint in final_constraints:
                    self.stdout.write(f"{constraint[0]} -> {constraint[2]}.{constraint[3]}.{constraint[4]}")
                
                self.stdout.write(self.style.SUCCESS('Process completed'))
