# Multi-Tenant Authentication System for Django

A beginner-friendly guide to implementing schema-based multi-tenancy with JWT authentication in Django.

## 👋 Before You Start

This guide assumes you have:
- Basic Python and Django knowledge
- Django project set up
- PostgreSQL database (required for schema support)
- Basic understanding of REST APIs

## 🎯 What You'll Build

By following this guide, you'll create a system that:
1. Supports multiple tenants with separate database schemas
2. Provides JWT-based authentication
3. Automatically routes requests to the correct tenant schema
4. Securely manages user access

## 📦 Prerequisites

1. Python 3.8+
2. Django 4.2+
3. PostgreSQL 10+
4. Required packages (we'll install these later)

## 📚 Table of Contents
1. [🚀 Quick Start](#-quick-start)
2. [🧩 Core Components](#-core-components)
3. [⚙️ Setup Instructions](#️-setup-instructions)
4. [🔄 Authentication Flow](#-authentication-flow)
5. [🔌 API Endpoints](#-api-endpoints)
6. [💻 Using the System](#-using-the-system)
7. [🔧 Integration Guide](#-integration-guide)
8. [⚠️ Common Issues](#️-common-issues)
9. [🔒 Security Considerations](#-security-considerations)

## 🚀 Quick Start

Follow these steps to get started quickly:

1. **Install required packages**
   ```bash
   pip install djangorestframework djangorestframework-simplejwt django-tenants psycopg2-binary
   ```

2. **Add to INSTALLED_APPS** (`settings.py`)
   ```python
   INSTALLED_APPS = [
       # ...
       'rest_framework',
       'rest_framework_simplejwt',
       'django_tenants',
       'your_app_name',
   ]
   ```

3. **Copy these files** to your project:
   - `authentication.py`
   - `base_views.py`
   - `models.py` (update your models accordingly)
   - `views.py` (update your views accordingly)

4. **Run migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate_schemas --shared
   ```

5. **Create your first tenant**
   ```python
   from your_app.models import Tenant, Domain
   
   # Create public tenant
   tenant = Tenant(
       schema_name='public',
       name='Public Tenant',
   )
   tenant.save()
   
   # Add domain
   domain = Domain()
   domain.domain = 'localhost'  # Your domain
   domain.tenant = tenant
   domain.is_primary = True
   domain.save()
   ```

Now you're ready to use the multi-tenant system! Continue reading for detailed explanations.

## 🧩 Core Components

### 1. Database Structure

#### 📊 Tenant Model (`models.py`)
```python
class Tenant(TenantMixin):
    # Required field for django-tenants
    schema_name = models.CharField(max_length=63, unique=True)
    
    # Your custom fields
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'ecomm_superadmin_tenants'
```

#### 🌐 Domain Model (`models.py`)
```python
class Domain(DomainMixin):
    # Required fields
    domain = models.CharField(max_length=253, unique=True)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    is_primary = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'ecomm_superadmin_domain'
```

#### 👥 User Model (`models.py`)
```python
class TenantUserModel(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    
    # Required for custom user model
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    class Meta:
        db_table = 'ecomm_tenant_admins_tenantuser'
```

### 2. Authentication Flow

```mermaid
sequenceDiagram
    participant Client
    participant View
    participant Auth
    participant DB
    
    Client->>View: POST /api/tenant1/auth/login/
    View->>Auth: Validate credentials
    Auth->>DB: Check user in tenant1 schema
    DB-->>Auth: User data
    Auth-->>View: JWT tokens
    View-->>Client: Return tokens + user data
    
    Note over Client: Use token in Authorization header
    
    Client->>View: GET /api/tenant1/protected/
    View->>Auth: Verify token
    Auth->>DB: Check user in tenant1 schema
    DB-->>Auth: User exists & active
    Auth-->>View: Valid token
    View->>DB: Get protected data
    DB-->>View: Return data
    View-->>Client: Return response
```

### 3. File Structure

```
your_project/
├── your_app/
│   ├── __init__.py
│   ├── authentication.py    # Custom auth classes
│   ├── base_views.py       # TenantAwareAPIView
│   ├── models.py          # Tenant, Domain, User models
│   ├── views.py           # Your API views
│   └── urls.py            # URL routing
├── config/
│   └── settings.py       # Django settings
└── manage.py
```

### 2. Authentication Classes

#### TenantJWTAuthentication
- Extends `JWTAuthentication` from `rest_framework_simplejwt`
- Verifies user existence and active status on every request
- Validates tenant information from JWT token

### 3. Base Views

#### TenantAwareAPIView
- Base class for all tenant-aware API views
- Automatically sets schema context based on JWT token
- Handles authentication and permission checks
- Manages tenant schema switching

## Setup Instructions

1. **Install Dependencies**
   ```bash
   pip install djangorestframework-simplejwt django-tenants
   ```

2. **Update Settings**
   Add to your `settings.py`:
   ```python
   INSTALLED_APPS = [
       # ...
       'rest_framework',
       'rest_framework_simplejwt',
       'django_tenants',
   ]
   
   # JWT Configuration
   SIMPLE_JWT = {
       'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
       'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
       'ROTATE_REFRESH_TOKENS': False,
       'ALGORITHM': 'HS256',
       'SIGNING_KEY': "your-secret-key-here",
       'AUTH_HEADER_TYPES': ('Bearer',),
       'USER_ID_FIELD': 'id',
       'USER_ID_CLAIM': 'user_id',
   }
   
   # Multi-tenant settings
   TENANT_MODEL = 'shared.Tenant'
   TENANT_DOMAIN_MODEL = 'shared.Domain'
   ```

## Authentication Flow

1. **Login**
   - Client sends credentials to `/api/<tenant_slug>/auth/login/`
   - System verifies tenant and user credentials
   - Returns JWT tokens with tenant context

2. **API Requests**
   - Client includes JWT token in `Authorization: Bearer <token>` header
   - System validates token and sets tenant context
   - Request is processed in the correct tenant schema

## API Endpoints

### 1. User Login
```
POST /api/<tenant_slug>/auth/login/
```
**Request Body:**
```json
{
    "email": "user@example.com",
    "password": "password123"
}
```

**Success Response (200 OK):**
```json
{
    "message": "Login successful",
    "user": {
        "id": 1,
        "email": "user@example.com",
        "tenant_id": 1,
        "first_name": "John",
        "last_name": "Doe",
        "is_staff": false,
        "is_superuser": false
    },
    "tokens": {
        "refresh": "xxx.yyy.zzz",
        "access": "aaa.bbb.ccc"
    },
    "tenant": {
        "id": 1,
        "name": "Tenant Name",
        "schema_name": "tenant_slug"
    }
}
```

## Using the System

### 1. Creating Protected Views
```python
from shared.base_views import TenantAwareAPIView
from rest_framework.response import Response

class ProtectedView(TenantAwareAPIView):
    def get(self, request):
        # This will automatically have the correct tenant context
        return Response({"message": "Accessing tenant data"})
```

### 2. Making Authenticated Requests
```python
import requests

url = "http://your-api.com/api/tenant-slug/protected-route/"
headers = {
    "Authorization": "Bearer your.access.token.here",
    "Content-Type": "application/json"
}

response = requests.get(url, headers=headers)
```

## Integration Guide

1. **Add to Existing Project**
   - Copy `shared` app to your project
   - Update database settings
   - Run migrations
   - Configure URLs

2. **Customization**
   - Extend `TenantAwareAPIView` for tenant-specific views
   - Override authentication settings as needed
   - Add custom user fields to `TenantUserModel`

## Security Considerations

1. Always use HTTPS in production
2. Set appropriate token expiration times
3. Implement rate limiting on authentication endpoints
4. Regularly rotate signing keys
5. Monitor and log authentication attempts

## Troubleshooting

1. **Token Validation Errors**
   - Verify token expiration
   - Check signing key matches
   - Ensure tenant exists and is active

2. **Schema Issues**
   - Verify tenant schema exists
   - Check database permissions
   - Confirm schema name matches exactly

## Support

For issues and feature requests, please open an issue in the project repository.
