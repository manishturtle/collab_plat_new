from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0005_cleanup_foreign_keys'),
    ]

    operations = [
        migrations.RunSQL(
            """
            DO $$
            DECLARE
                r RECORD;
            BEGIN
                -- First, drop all foreign key constraints on chat_channelparticipant
                FOR r IN (
                    SELECT conname, conrelid::regclass as table_name, conrelid::regclass as table_name2
                    FROM pg_constraint 
                    WHERE conrelid = 'chat_channelparticipant'::regclass
                    AND contype = 'f'
                ) LOOP
                    BEGIN
                        EXECUTE format('ALTER TABLE %I DROP CONSTRAINT IF EXISTS %I CASCADE', 
                                     r.table_name, r.conname);
                        RAISE NOTICE 'Dropped constraint: % on table %', r.conname, r.table_name;
                    EXCEPTION WHEN OTHERS THEN
                        RAISE NOTICE 'Error dropping constraint %: %', r.conname, SQLERRM;
                    END;
                END LOOP;
                
                -- Add back the correct user foreign key
                BEGIN
                    EXECUTE '
                        ALTER TABLE chat_channelparticipant 
                        ADD CONSTRAINT chat_channelparticipant_user_id_fk
                        FOREIGN KEY (user_id) 
                        REFERENCES ecomm_tenant_admins_tenantuser(id)
                        ON DELETE CASCADE
                        DEFERRABLE INITIALLY DEFERRED';
                    RAISE NOTICE 'Added user foreign key constraint';
                EXCEPTION WHEN OTHERS THEN
                    RAISE NOTICE 'Error adding user foreign key: %', SQLERRM;
                END;
                
                -- Add back the correct channel foreign key
                BEGIN
                    EXECUTE '
                        ALTER TABLE chat_channelparticipant 
                        ADD CONSTRAINT chat_channelparticipant_channel_id_fk
                        FOREIGN KEY (channel_id) 
                        REFERENCES chat_chatchannel(id)
                        ON DELETE CASCADE
                        DEFERRABLE INITIALLY DEFERRED';
                    RAISE NOTICE 'Added channel foreign key constraint';
                EXCEPTION WHEN OTHERS THEN
                    RAISE NOTICE 'Error adding channel foreign key: %', SQLERRM;
                END;
            END $$;
            """,
            reverse_sql="""
            -- No reverse SQL needed as we're just cleaning up invalid constraints
            SELECT 1;
            """
        ),
    ]
