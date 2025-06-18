"""
URLs for the shared app.
"""
from django.urls import path, include
from . import views

app_name = 'shared'

urlpatterns = [
    # Authentication
    path('<str:tenant_slug>/auth/login/', views.TenantLoginView.as_view(), name='tenant-login'),
    
    # Chat endpoints
    path('<str:tenant_slug>/chat/users/', views.TenantUsersForChatView.as_view(), name='chat-users-list'),
]
