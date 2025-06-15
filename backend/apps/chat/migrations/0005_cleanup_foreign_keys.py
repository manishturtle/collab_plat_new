from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0004_remove_incorrect_foreign_key'),
    ]

    operations = [
        migrations.RunSQL(
            """
            DO $$
            DECLARE
                constraint_record RECORD;
                constraint_name TEXT;
            BEGIN
                -- First, drop all foreign key constraints on user_id
                FOR constraint_record IN 
                    SELECT conname, conrelid::regclass as table_name
                    FROM pg_constraint 
                    WHERE conrelid = 'chat_channelparticipant'::regclass
                    AND confrelid IS NOT NULL
                    AND conname LIKE '%user_id%'
                LOOP
                    EXECUTE format('ALTER TABLE %I DROP CONSTRAINT IF EXISTS %I CASCADE', 
                                 constraint_record.table_name, 
                                 constraint_record.conname);
                END LOOP;
                
                -- Then, add back the correct foreign key
                EXECUTE '
                    ALTER TABLE chat_channelparticipant 
                    ADD CONSTRAINT chat_channelparticipant_user_id_fk
                    FOREIGN KEY (user_id) 
                    REFERENCES ecomm_tenant_admins_tenantuser(id)
                    DEFERRABLE INITIALLY DEFERRED';
                    
                -- Also clean up any duplicate channel_id constraints
                SELECT conname INTO constraint_name
                FROM pg_constraint 
                WHERE conrelid = 'chat_channelparticipant'::regclass
                AND conname LIKE '%channel_id%'
                LIMIT 1;
                
                IF FOUND THEN
                    EXECUTE format('ALTER TABLE chat_channelparticipant DROP CONSTRAINT IF EXISTS %I CASCADE', 
                                 constraint_name);
                    
                    EXECUTE '
                        ALTER TABLE chat_channelparticipant 
                        ADD CONSTRAINT chat_channelparticipant_channel_id_fk
                        FOREIGN KEY (channel_id) 
                        REFERENCES chat_chatchannel(id)
                        ON DELETE CASCADE
                        DEFERRABLE INITIALLY DEFERRED';
                END IF;
            END $$;
            """,
            reverse_sql="""
            -- No reverse SQL needed as we're just cleaning up invalid constraints
            SELECT 1;
            """
        ),
    ]
