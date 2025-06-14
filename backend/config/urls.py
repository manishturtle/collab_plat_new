"""
URL configuration for config project.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Shared app (authentication, etc.)
    path('api/', include('apps.shared.urls')),
]
