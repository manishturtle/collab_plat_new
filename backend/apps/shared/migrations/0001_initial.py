# Generated by Django 5.1.11 on 2025-06-15 07:02

import apps.shared.models
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Domain',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('domain', models.CharField(db_index=True, max_length=253, unique=True)),
                ('is_primary', models.BooleanField(db_index=True, default=True)),
            ],
            options={
                'db_table': 'ecomm_superadmin_domain',
                'ordering': ['-is_primary', 'domain'],
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Tenant',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('schema_name', models.CharField(max_length=63, unique=True)),
                ('name', models.CharField(blank=True, max_length=255, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
            ],
            options={
                'db_table': 'ecomm_superadmin_tenants',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='TenantUserModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('company_id', models.IntegerField(default=1, editable=False)),
                ('client_id', models.IntegerField(default=1, editable=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.IntegerField(blank=True, db_column='created_by', null=True)),
                ('updated_by', models.IntegerField(blank=True, db_column='updated_by', null=True)),
                ('email', models.EmailField(db_index=True, max_length=254, unique=True)),
                ('username', models.CharField(blank=True, db_index=True, max_length=150)),
                ('first_name', models.CharField(blank=True, max_length=150)),
                ('last_name', models.CharField(blank=True, max_length=150)),
                ('is_active', models.BooleanField(default=True)),
                ('is_staff', models.BooleanField(default=False)),
                ('is_superuser', models.BooleanField(default=False)),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now)),
                ('last_login', models.DateTimeField(blank=True, null=True)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'Tenant User',
                'verbose_name_plural': 'Tenant Users',
                'db_table': 'ecomm_tenant_admins_tenantuser',
                'ordering': ['email'],
            },
            managers=[
                ('objects', apps.shared.models.TenantUserManager()),
            ],
        ),
    ]
