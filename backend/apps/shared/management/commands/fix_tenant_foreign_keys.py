from django.core.management.base import BaseCommand
from django.db import connection
from django.conf import settings
from django_tenants.utils import get_public_schema_name

class Command(BaseCommand):
    help = 'Fix foreign key constraints to use the correct user model'

    def handle(self, *args, **options):
        # Get the correct user model table
        user_model = settings.AUTH_USER_MODEL.lower().replace('.', '_')
        
        # SQL to fix the foreign key constraints
        sql_commands = [
            # Fix chat_channelparticipant
            f"""
            DO $$
            BEGIN
                -- Drop the existing foreign key constraint if it exists
                IF EXISTS (
                    SELECT 1 
                    FROM information_schema.table_constraints 
                    WHERE table_name = 'chat_channelparticipant' 
                    AND constraint_name = 'chat_channelparticipant_user_id_beeb51d8_fk_auth_user_id'
                ) THEN
                    EXECUTE 'ALTER TABLE chat_channelparticipant DROP CONSTRAINT chat_channelparticipant_user_id_beeb51d8_fk_auth_user_id';
                END IF;
                
                -- Add the new foreign key constraint
                EXECUTE format('
                    ALTER TABLE chat_channelparticipant 
                    ADD CONSTRAINT chat_channelparticipant_user_id_fk_%s_id 
                    FOREIGN KEY (user_id) REFERENCES %s (id) 
                    DEFERRABLE INITIALLY DEFERRED',
                    user_model, user_model
                );
            END $$;
            """,
            
            # Fix any other tables with similar issues
            # Add more ALTER TABLE statements for other tables if needed
        ]
        
        with connection.cursor() as cursor:
            for sql in sql_commands:
                try:
                    cursor.execute(sql)
                    self.stdout.write(self.style.SUCCESS('Successfully executed SQL command'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error executing SQL: {str(e)}'))
                    raise
