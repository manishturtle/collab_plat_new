import os
import django

def check_migrations():
    # Set the Django settings module
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    
    # Setup Django
    django.setup()
    
    from django.db import connection
    
    try:
        # Connect to the bingo_travels schema
        with connection.cursor() as cursor:
            cursor.execute('SET search_path TO bingo_travels')
            
            # Check if django_migrations table exists
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'bingo_travels' 
                    AND table_name = 'django_migrations'
                )
            """)
            
            if cursor.fetchone()[0]:
                print("django_migrations table exists in bingo_travels schema")
                
                # Get applied migrations
                cursor.execute('SELECT app, name FROM django_migrations ORDER BY id')
                print("\nApplied migrations in bingo_travels schema:")
                for app, name in cursor.fetchall():
                    print(f"- {app}: {name}")
            else:
                print("django_migrations table does not exist in bingo_travels schema")
            
            # Check if the tenant user table exists
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'bingo_travels' 
                    AND table_name = 'ecomm_tenant_admins_tenantuser'
                )
            """)
            
            if cursor.fetchone()[0]:
                print("\necomm_tenant_admins_tenantuser table exists in bingo_travels schema")
            else:
                print("\necomm_tenant_admins_tenantuser table does not exist in bingo_travels schema")
            
            # Reset search path
            cursor.execute('SET search_path TO public')
    
    except Exception as e:
        print(f"Error checking migrations: {e}")

if __name__ == "__main__":
    check_migrations()
