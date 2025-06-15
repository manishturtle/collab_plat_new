from django.core.management.base import BaseCommand
from django_tenants.utils import get_tenant_model, tenant_context

class Command(BaseCommand):
    help = 'Run migrations for a specific tenant'

    def add_arguments(self, parser):
        parser.add_argument('schema_name', type=str, help='The schema name of the tenant')

    def handle(self, *args, **options):
        schema_name = options['schema_name']
        tenant_model = get_tenant_model()
        
        try:
            tenant = tenant_model.objects.get(schema_name=schema_name)
            self.stdout.write(self.style.SUCCESS(f'Running migrations for tenant: {schema_name}'))
            
            with tenant_context(tenant):
                from django.core.management import call_command
                call_command('migrate', interactive=False)
                self.stdout.write(self.style.SUCCESS(f'Successfully migrated tenant: {schema_name}'))
                
        except tenant_model.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Tenant with schema name {schema_name} does not exist'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error migrating tenant {schema_name}: {str(e)}'))
