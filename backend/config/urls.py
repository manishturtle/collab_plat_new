"""
URL configuration for config project.
"""

from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

# API URL patterns
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('apps.shared.urls')),
    path('api/chat/', include(('apps.chat.api.urls', 'chat'), namespace='chat-api')),
    
    # WebSocket test page
    path('test-websocket/', TemplateView.as_view(template_name='chat/websocket_test.html'), name='test_websocket'),
]

# Serve static and media files in development
if settings.DEBUG:
    from django.contrib.staticfiles.views import serve
    from django.views.decorators.cache import never_cache
    
    # Serve static files in development
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
    # Serve index.html for all other URLs in development
    urlpatterns += [
        re_path(r'^.*$', never_cache(serve), {
            'path': 'index.html',
            'document_root': settings.STATIC_ROOT,
        }),
    ]

# Add debug toolbar in development
if settings.DEBUG and 'debug_toolbar' in settings.INSTALLED_APPS:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
