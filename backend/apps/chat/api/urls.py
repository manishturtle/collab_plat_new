# from django.urls import path, include
# from rest_framework.routers import DefaultRouter

# from . import views

# # Create a router for our API endpoints
# router = DefaultRouter(trailing_slash=False)

# # Register viewsets with the router
# router.register(r'channels', views.ChannelViewSet, basename='channel')

# # The API URLs are now determined automatically by the router
# urlpatterns = [
#     # Include the router's URL patterns
#     path('', include(router.urls)),
    
#     # Additional API endpoints
#     path('channels/<uuid:pk>/messages/', views.ChannelViewSet.as_view({'get': 'messages'}), name='channel-messages'),
#     path('channels/<uuid:pk>/send_message/', views.ChannelViewSet.as_view({'post': 'send_message'}), name='send-message'),
#     path('channels/<uuid:pk>/mark_read/', views.ChannelViewSet.as_view({'post': 'mark_read'}), name='mark-read'),
# ]

# # Include authentication URLs for browsable API
# urlpatterns += [
#     path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
# ]


# apps/chat/api/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create a router for our API endpoints
router = DefaultRouter()
router.register(r'channels', views.ChannelViewSet, basename='channel')

# The API URLs are now determined automatically by the router
urlpatterns = [ 
    path('<slug:tenant_slug>/', include(router.urls)),
    path(
        '<slug:tenant_slug>/channels/<uuid:pk>/messages/',
        views.ChannelViewSet.as_view({'get': 'messages'}),
        name='channel-messages'
    ),
    path(
        '<slug:tenant_slug>/channels/<uuid:pk>/send_message/',
        views.ChannelViewSet.as_view({'post': 'send_message'}),
        name='send-message'
    ),
    path(
        '<slug:tenant_slug>/channels/<uuid:pk>/mark_read/',
        views.ChannelViewSet.as_view({'post': 'mark_read'}),
        name='mark-read'
    ),
]