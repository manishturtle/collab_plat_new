"""
Models for the shared app.
"""
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, UserManager
from django.utils import timezone
from django.core.validators import RegexValidator
from django_tenants.models import TenantMixin, DomainMixin
from django_tenants.utils import schema_context


# This abstract model is good practice and can be kept.
class BaseTenantModel(models.Model):
    """
    Base model for all tenant-specific models.
    """
    company_id = models.IntegerField(default=1, editable=False)
    client_id = models.IntegerField(default=1, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)
    created_by = models.IntegerField(null=True, blank=True, db_column='created_by')
    updated_by = models.IntegerField(null=True, blank=True, db_column='updated_by')

    class Meta:
        abstract = True

class Tenant(TenantMixin):
    """
    Model that maps to the existing ecomm_superadmin_tenants table
    and integrates with django-tenants.
    """
    # These are the minimal required fields for django-tenants
    schema_name = models.CharField(max_length=63, unique=True)
    
    # Add only the fields that exist in your actual database table
    name = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    
    # Disable schema creation/deletion since tables already exist
    auto_create_schema = False
    auto_drop_schema = False
    
    # Add any other fields that exist in your actual table
    # Make sure to set null=True for fields that might be nullable
    
    class Meta:
        db_table = 'ecomm_superadmin_tenants'
        managed = False  # Important: Don't let Django manage the table

    def __str__(self):
        return self.name

class Domain(DomainMixin):
    """
    Model that maps to the existing ecomm_superadmin_domain table
    and integrates with django-tenants.
    """
    # Required fields for DomainMixin
    domain = models.CharField(max_length=253, unique=True, db_index=True)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='domains')
    is_primary = models.BooleanField(default=True, db_index=True)
    
    # Add any other fields that exist in your actual domain table
    # Make sure to set null=True for fields that might be nullable
    
    class Meta:
        db_table = 'ecomm_superadmin_domain'
        managed = False  # Important: Don't let Django manage the table
        
        # Add this if you have a specific ordering for domains
        ordering = ['-is_primary', 'domain']

    def __str__(self):
        return self.domain

class TenantUserManager(UserManager):
    """Custom user manager for TenantUserModel."""
    def _create_user(self, email, password=None, **extra_fields):
        """Create and save a user with the given email and password."""
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)

class TenantUserModel(BaseTenantModel, AbstractBaseUser, PermissionsMixin):
    """
    Model for tenant users.
    This is a concrete model that will be used across all tenants.
    """
    email = models.EmailField(unique=True, db_index=True)
    username = models.CharField(max_length=150, blank=True, db_index=True)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(null=True, blank=True)

    objects = TenantUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        db_table = 'ecomm_tenant_admins_tenantuser'
        verbose_name = 'Tenant User'
        verbose_name_plural = 'Tenant Users'
        ordering = ['email']


    def get_full_name(self):
        """Return the first_name plus the last_name, with a space in between."""
        full_name = f"{self.first_name or ''} {self.last_name or ''}"
        return full_name.strip() or self.email

    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name or self.email.split('@')[0]