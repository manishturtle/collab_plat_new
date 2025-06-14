"""
URLs for the shared app.
"""
from django.urls import path
from . import views

app_name = 'shared'

urlpatterns = [
    # Authentication
    path('<str:tenant_slug>/auth/login/', views.TenantLoginView.as_view(), name='tenant-login'),
]
