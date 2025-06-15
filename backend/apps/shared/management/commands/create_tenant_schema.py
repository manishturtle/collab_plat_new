from django.core.management.base import BaseCommand
from django_tenants.utils import get_tenant_model, tenant_context
from django_tenants.postgresql_backend.base import _check_schema_name
from django.db import connection

class Command(BaseCommand):
    help = 'Create a new tenant schema'

    def add_arguments(self, parser):
        parser.add_argument('schema_name', type=str, help='The schema name to create')
        parser.add_argument('--domain', type=str, help='The domain for the tenant', default=None)

    def handle(self, *args, **options):
        schema_name = options['schema_name']
        domain = options['domain'] or f"{schema_name}.localhost"
        
        # Validate schema name
        _check_schema_name(schema_name)
        
        tenant_model = get_tenant_model()
        
        try:
            # Check if schema already exists
            with connection.cursor() as cursor:
                cursor.execute("SELECT schema_name FROM information_schema.schemata WHERE schema_name = %s", [schema_name])
                if cursor.fetchone():
                    self.stdout.write(self.style.SUCCESS(f'Schema {schema_name} already exists'))
                    return
            
            # Create the schema
            with connection.cursor() as cursor:
                cursor.execute(f'CREATE SCHEMA "{schema_name}"')
            
            self.stdout.write(self.style.SUCCESS(f'Successfully created schema: {schema_name}'))
            
            # Create tenant record if it doesn't exist
            tenant, created = tenant_model.objects.get_or_create(
                schema_name=schema_name,
                defaults={
                    'name': schema_name.replace('_', ' ').title(),
                }
            )
            
            # Create domain record
            from django_tenants.models import Domain
            Domain.objects.get_or_create(
                domain=domain,
                tenant=tenant,
                is_primary=True
            )
            
            self.stdout.write(self.style.SUCCESS(f'Successfully created/updated tenant: {schema_name}'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error creating schema {schema_name}: {str(e)}'))
            # Clean up schema if it was created but tenant creation failed
            with connection.cursor() as cursor:
                cursor.execute(f'DROP SCHEMA IF EXISTS "{schema_name}" CASCADE')
            raise
