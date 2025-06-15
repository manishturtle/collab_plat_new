from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0007_add_missing_columns'),
    ]

    operations = [
        migrations.RunSQL(
            """
            DO $$
            BEGIN
                -- Add created_by if it doesn't exist
                IF NOT EXISTS (
                    SELECT 1 
                    FROM information_schema.columns 
                    WHERE table_name = 'chat_channelparticipant' 
                    AND column_name = 'created_by'
                ) THEN
                    ALTER TABLE chat_channelparticipant 
                    ADD COLUMN created_by INTEGER NULL;
                END IF;
                
                -- Add updated_by if it doesn't exist
                IF NOT EXISTS (
                    SELECT 1 
                    FROM information_schema.columns 
                    WHERE table_name = 'chat_channelparticipant' 
                    AND column_name = 'updated_by'
                ) THEN
                    ALTER TABLE chat_channelparticipant 
                    ADD COLUMN updated_by INTEGER NULL;
                END IF;
            END $$;
            """,
            reverse_sql="""
            -- No reverse SQL needed as we're just adding columns
            SELECT 1;
            """
        ),
    ]
