from django.db import connection
from typing import List, Dict, Any, Optional


def fix_foreign_key_constraints() -> Dict[str, Any]:
    """
    Executes raw SQL to fix foreign key constraints directly in the database.
    Specifically addresses the issue with chat_channelparticipant referencing auth_user 
    instead of the custom tenant user model.
    
    Returns:
        Dict with status and message
    """
    with connection.cursor() as cursor:
        try:
            # Drop the existing constraint
            cursor.execute("""
                ALTER TABLE chat_channelparticipant 
                DROP CONSTRAINT IF EXISTS chat_channelparticipant_user_id_beeb51d8_fk_auth_user_id;
            """)
            
            # Add the new constraint
            cursor.execute("""
                ALTER TABLE chat_channelparticipant 
                ADD CONSTRAINT chat_channelparticipant_user_id_fk 
                FOREIGN KEY (user_id) REFERENCES ecomm_tenant_admins_tenantuser(id)
                ON DELETE CASCADE;
            """)
            
            return {
                "status": "success",
                "message": "Foreign key constraint successfully updated"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
