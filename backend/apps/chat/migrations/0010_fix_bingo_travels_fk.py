from django.db import migrations

class Migration(migrations.Migration):
    """
    Fix foreign key constraints in the bingo_travels tenant schema 
    that are incorrectly referencing auth_user instead of the custom user model.
    """
    
    def fix_constraints(apps, schema_editor):
        """
        Drop the incorrect foreign key constraint and add the correct one.
        """
        # Only apply to bingo_travels schema
        if schema_editor.connection.schema_name != 'bingo_travels':
            return
            
        # Execute raw SQL to drop the constraint
        schema_editor.execute(
            """
            DO $$
            BEGIN
                -- Check if constraint exists
                IF EXISTS (
                    SELECT 1 FROM pg_constraint 
                    WHERE conname = 'chat_channelparticipant_user_id_beeb51d8_fk_auth_user_id' 
                    AND connamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'bingo_travels')
                ) THEN
                    -- Drop the constraint
                    ALTER TABLE bingo_travels.chat_channelparticipant 
                    DROP CONSTRAINT chat_channelparticipant_user_id_beeb51d8_fk_auth_user_id;
                    
                    -- Add the correct constraint
                    ALTER TABLE bingo_travels.chat_channelparticipant
                    ADD CONSTRAINT chat_channelparticipant_user_id_custom_fk
                    FOREIGN KEY (user_id)
                    REFERENCES bingo_travels.ecomm_tenant_admins_tenantuser(id)
                    ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;
                END IF;
            END $$;
            """
        )

    operations = [
        migrations.RunPython(fix_constraints, reverse_code=migrations.RunPython.noop),
    ]
