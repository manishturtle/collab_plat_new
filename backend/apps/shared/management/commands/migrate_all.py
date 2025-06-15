# scripts/migrate_all.py
import os
import django
from django.conf import settings
from django.core.management import call_command

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

def run_migrations():
    # Migrate public schema
    print("=== Migrating public schema ===")
    call_command('migrate_schemas', '--schema=public')
    
    # Migrate all tenant schemas
    from django_tenants.utils import get_tenant_model
    TenantModel = get_tenant_model()
    
    for tenant in TenantModel.objects.exclude(schema_name='public'):
        print(f"\n=== Migrating tenant: {tenant.schema_name} ===")
        call_command('migrate_schemas', f'--schema={tenant.schema_name}')

if __name__ == '__main__':
    run_migrations()