from rest_framework import viewsets, mixins, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from django.db import transaction
from django.shortcuts import get_object_or_404

from ..models import ChatChannel, ChannelParticipant, ChatMessage, MessageReadStatus
from ..selectors import get_channels_for_user, get_channel_by_id, get_messages_for_channel
from ..services import create_channel, send_message, mark_messages_as_read
from .serializers import (
    ChatChannelSerializer, 
    ChannelParticipantSerializer,
    ChatMessageSerializer
)
from apps.shared.base_views import TenantAwareAPIView


class ChannelViewSet(TenantAwareAPIView,   
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet):
    """
    ViewSet for managing chat channels.
    Supports listing, retrieving, and creating channels.
    """
    serializer_class = ChatChannelSerializer
    lookup_field = 'pk'
    
    def get_queryset(self):
        """
        Returns channels where the current user is a participant.
        """
        return get_channels_for_user(user=self.request.user)
    
    def get_serializer_context(self):
        """
        Adds the request to the serializer context.
        """
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        """
        Create a new chat channel.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Create the channel using our service
        channel = create_channel(
            user=request.user,
            name=serializer.validated_data.get('name'),
            participants=serializer.validated_data.get('participants', []),
            channel_type=serializer.validated_data.get('channel_type', ChatChannel.ChannelType.GROUP),
            context_data={
                'host_application_id': serializer.validated_data.get('host_application_id'),
                'context_object_type': serializer.validated_data.get('context_object_type'),
                'context_object_id': serializer.validated_data.get('context_object_id'),
            }
        )
        
        # Return the created channel
        serializer = self.get_serializer(channel)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, 
            status=status.HTTP_201_CREATED, 
            headers=headers
        )
    
    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        """
        Get messages for a specific channel.
        """
        channel = self.get_object()
        messages = get_messages_for_channel(
            channel_id=channel.id,
            user=request.user
        )
        
        # Mark messages as read
        mark_messages_as_read(channel.id, request.user)
        
        page = self.paginate_queryset(messages)
        if page is not None:
            serializer = ChatMessageSerializer(
                page, 
                many=True,
                context={'request': request}
            )
            return self.get_paginated_response(serializer.data)
            
        serializer = ChatMessageSerializer(
            messages, 
            many=True,
            context={'request': request}
        )
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def send_message(self, request, pk=None):
        """
        Send a message to a channel.
        """
        channel = self.get_object()
        
        # Validate input
        content = request.data.get('content')
        if not content:
            return Response(
                {'detail': 'Message content is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Send message using our service
        message = send_message(
            channel_id=channel.id,
            user=request.user,
            content=content,
            content_type=request.data.get('content_type', 'text/plain'),
            file_url=request.data.get('file_url')
        )
        
        # Return the created message
        serializer = ChatMessageSerializer(
            message, 
            context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """
        Mark all messages in a channel as read.
        """
        channel = self.get_object()
        count = mark_messages_as_read(channel.id, request.user)
        return Response({
            'status': 'success',
            'message': f'Marked {count} messages as read',
            'channel_id': str(channel.id)
        })