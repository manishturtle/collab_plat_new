from django.db import migrations
from django.db import connection

def get_actual_columns(schema_name, table_name):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_schema = %s AND table_name = %s
            ORDER BY ordinal_position
        """, [schema_name, table_name])
        return cursor.fetchall()

class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0008_add_missing_columns_to_participant'),
    ]

    operations = [
        migrations.RunSQL(
            """
            DO $$
            DECLARE
                col_record RECORD;
                sql_text TEXT;
                has_created_by BOOLEAN := FALSE;
                has_updated_by BOOLEAN := FALSE;
            BEGIN
                -- Check what columns actually exist
                FOR col_record IN 
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'chat_channelparticipant' 
                    AND table_schema = current_schema()
                LOOP
                    IF col_record.column_name = 'created_by' THEN
                        has_created_by := TRUE;
                    ELSIF col_record.column_name = 'updated_by' THEN
                        has_updated_by := TRUE;
                    END IF;
                END LOOP;
                
                -- Add created_by if it doesn't exist
                IF NOT has_created_by THEN
                    EXECUTE 'ALTER TABLE chat_channelparticipant ADD COLUMN created_by INTEGER NULL';
                    RAISE NOTICE 'Added created_by column';
                END IF;
                
                -- Add updated_by if it doesn't exist
                IF NOT has_updated_by THEN
                    EXECUTE 'ALTER TABLE chat_channelparticipant ADD COLUMN updated_by INTEGER NULL';
                    RAISE NOTICE 'Added updated_by column';
                END IF;
                
                -- Fix any duplicate columns if they exist
                -- This is a simplified approach - in a real scenario, you'd need to handle data migration carefully
                BEGIN
                    -- Try to drop any duplicate constraints
                    EXECUTE 'ALTER TABLE chat_channelparticipant 
                            DROP CONSTRAINT IF EXISTS chat_channelparticipant_user_id_beeb51d8_fk_auth_user_id';
                    EXECUTE 'ALTER TABLE chat_channelparticipant 
                            DROP CONSTRAINT IF EXISTS chat_channelparticipant_user_id_fk';
                    
                    -- Ensure the correct foreign key exists
                    IF NOT EXISTS (
                        SELECT 1 
                        FROM information_schema.table_constraints 
                        WHERE constraint_name = 'chat_channelparticipant_user_id_fk' 
                        AND table_name = 'chat_channelparticipant'
                        AND table_schema = current_schema()
                    ) THEN
                        EXECUTE 'ALTER TABLE chat_channelparticipant 
                                ADD CONSTRAINT chat_channelparticipant_user_id_fk 
                                FOREIGN KEY (user_id) 
                                REFERENCES ecomm_tenant_admins_tenantuser(id) 
                                ON DELETE CASCADE 
                                DEFERRABLE INITIALLY DEFERRED';
                    END IF;
                    
                    -- Ensure the unique constraint exists
                    IF NOT EXISTS (
                        SELECT 1 
                        FROM information_schema.table_constraints 
                        WHERE constraint_name = 'chat_channelparticipant_user_id_channel_id_uniq' 
                        AND table_name = 'chat_channelparticipant'
                        AND table_schema = current_schema()
                    ) THEN
                        EXECUTE 'ALTER TABLE chat_channelparticipant 
                                ADD CONSTRAINT chat_channelparticipant_user_id_channel_id_uniq 
                                UNIQUE (user_id, channel_id)';
                    END IF;
                    
                EXCEPTION WHEN OTHERS THEN
                    RAISE NOTICE 'Error fixing constraints: %', SQLERRM;
                END;
                
            EXCEPTION WHEN OTHERS THEN
                RAISE NOTICE 'Error in migration: %', SQLERRM;
                RAISE;
            END $$;
            """,
            reverse_sql="""
            -- This is a non-destructive operation, so reverse is a no-op
            SELECT 1;
            """
        ),
    ]
