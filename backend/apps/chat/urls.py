from django.urls import path
from django.views.generic import TemplateView

urlpatterns = [
    # Add other URL patterns here
    
    # Serve the WebSocket test page
    path('test-websocket/', TemplateView.as_view(template_name='websocket_test.html'), name='test_websocket'),
]
