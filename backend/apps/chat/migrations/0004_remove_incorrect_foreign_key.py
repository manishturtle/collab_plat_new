from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0003_fix_user_foreign_key'),
    ]

    def drop_constraint_if_exists(cursor, table_name, constraint_name):
        cursor.execute("""
            SELECT 1 
            FROM information_schema.table_constraints 
            WHERE table_name = %s 
            AND constraint_name = %s
        """, [table_name, constraint_name])
        if cursor.fetchone():
            cursor.execute(f'ALTER TABLE {table_name} DROP CONSTRAINT {constraint_name}')
            return True
        return False

    operations = [
        migrations.RunSQL(
            """
            DO $$
            DECLARE
                constraint_record RECORD;
            BEGIN
                -- Find and drop all foreign key constraints on user_id
                FOR constraint_record IN 
                    SELECT conname
                    FROM pg_constraint 
                    WHERE conrelid = 'chat_channelparticipant'::regclass
                    AND confrelid = 'ecomm_tenant_admins_tenantuser'::regclass
                    AND conname LIKE '%user_id%'
                LOOP
                    EXECUTE format('ALTER TABLE chat_channelparticipant DROP CONSTRAINT IF EXISTS %I', 
                                 constraint_record.conname);
                END LOOP;
                
                -- Ensure we have the correct foreign key
                IF NOT EXISTS (
                    SELECT 1 
                    FROM information_schema.table_constraints 
                    WHERE table_name = 'chat_channelparticipant' 
                    AND constraint_name = 'chat_channelparticipant_user_id_fk'
                ) THEN
                    EXECUTE '
                        ALTER TABLE chat_channelparticipant 
                        ADD CONSTRAINT chat_channelparticipant_user_id_fk
                        FOREIGN KEY (user_id) 
                        REFERENCES ecomm_tenant_admins_tenantuser(id)
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
