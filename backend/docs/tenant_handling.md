# Multi-Tenant Architecture Implementation Guide

## Table of Contents
1. [Introduction](#introduction)
2. [Core Concepts](#core-concepts)
3. [Setup Instructions](#setup-instructions)
4. [Tenant Middleware](#tenant-middleware)
5. [Database Routing](#database-routing)
6. [Tenant Context](#tenant-context)
7. [Best Practices](#best-practices)
8. [Common Pitfalls](#common-pitfalls)
9. [Testing](#testing)
10. [Deployment](#deployment)

## Introduction
This document outlines the implementation of a multi-tenant architecture using Django's schema-based approach. The system is designed to support multiple tenants in a single application instance while keeping their data isolated.

## Core Concepts

### Tenant Model
```python
class Tenant(models.Model):
    name = models.CharField(max_length=100)
    schema_name = models.CharField(max_length=63, unique=True, validators=[
        RegexValidator(
            regex='^[a-z][a-z0-9_]*$',
            message='Schema name must start with a letter and only contain lowercase letters, numbers, or underscores.'
        )
    ])
    domain_url = models.CharField(max_length=100, unique=True)
    created_on = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
```

### Tenant-Aware Models
All tenant-specific models should inherit from:
```python
class TenantAwareModel(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    
    class Meta:
        abstract = True
```

## Setup Instructions

### 1. Dependencies
Add these to your `requirements.txt`:
```
django-tenant-schemas==1.10.0
psycopg2-binary>=2.8.6
```

### 2. Settings Configuration
Update `settings.py`:
```python
INSTALLED_APPS = [
    'tenant_schemas',
    'your_tenant_app',
    'django.contrib.contenttypes',
    'django.contrib.auth',
    # ... other apps
]

DATABASE_ROUTERS = ('tenant_schemas.routers.TenantSyncRouter',)
MIDDLEWARE = [
    'your_app.middleware.TenantMiddleware',
    # ... other middleware
]

TENANT_MODEL = "your_tenant_app.Tenant"
TENANT_DOMAIN_MODEL = "your_tenant_app.Domain"
```

## Tenant Middleware

Create `middleware.py` in your app:
```python
from django_tenants.middleware.main import TenantMainMiddleware
from django.conf import settings

class TenantMiddleware(TenantMainMiddleware):
    def get_tenant(self, model, hostname, *args, **kwargs):
        tenant = super().get_tenant(model, hostname, *args, **kwargs)
        # Add custom tenant validation logic here
        return tenant
```

## Database Routing

Create `routers.py`:
```python
class TenantSyncRouter:
    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if db == 'default':
            return None
        return False
```

## Tenant Context

For accessing tenant information in views/templates:
```python
from django_tenants.utils import tenant_context

def some_view(request):
    with tenant_context(request.tenant):
        # Your tenant-specific code here
        pass
```

## Best Practices

1. **Schema Prefixing**
   - Always prefix tenant-specific tables with the schema name
   - Use `connection.schema_name` to get current schema

2. **Migrations**
   - Run migrations for shared apps on public schema
   - Run migrations for tenant apps on all tenant schemas

3. **Caching**
   - Use tenant-aware cache keys
   - Example: `f"{schema_name}:{cache_key}"`

## Common Pitfalls

1. **Schema Leaks**
   - Always use `tenant_context` when making requests
   - Be cautious with raw SQL queries

2. **Performance**
   - Monitor connection pooling
   - Consider read replicas for heavy read operations

## Testing

Use the `@modify_settings` decorator for tenant-specific tests:

```python
from django_tenants.test.cases import TenantTestCase

class TenantTestCase(TenantTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Setup test tenant data
```

## Deployment

1. **Migrations**
   ```bash
   python manage.py migrate_schemas --shared
   python manage.py migrate_schemas --tenant
   ```

2. **Static Files**
   - Use separate storage backends per tenant
   - Configure `STATICFILES_STORAGE` with tenant awareness

3. **Monitoring**
   - Track tenant-specific metrics
   - Set up alerts for tenant-specific issues

## Troubleshooting

Common issues and solutions:

1. **Database Connection Issues**
   - Verify database user has proper schema permissions
   - Check connection pooling settings

2. **Migration Problems**
   - Ensure proper migration dependencies
   - Test migrations in staging first

## Additional Resources

- [Django Tenants Documentation](https://django-tenants.readthedocs.io/)
- [Multi-tenant Django Applications](https://books.agiliq.com/projects/django-multi-tenant/en/latest/)

---
*Last Updated: June 2025*
