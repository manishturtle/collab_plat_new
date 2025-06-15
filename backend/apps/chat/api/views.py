import uuid
from rest_framework import viewsets, mixins, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.db import connection
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

    def create(self, request, *args, **kwargs):
        """
        Create a new chat channel.
        The serializer handles the logic for different channel types:
        1. direct: One-to-one private conversations
        2. group: Multi-participant conversations
        3. contextual_object: Conversations tied to a specific context/object
        """
        # All validation and default-setting logic is handled by the serializer
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            with transaction.atomic():
                # The serializer's .save() method will call our custom .create() within the serializer
                channel = serializer.save()
                
                # Re-serialize the instance to include all fields populated on creation
                response_serializer = self.get_serializer(channel)
                return Response(response_serializer.data, status=status.HTTP_201_CREATED)
                
        except Exception as e:
            # Log the error and return a proper error response
            import logging
            logger = logging.getLogger(__name__)
            logger.exception("Error creating channel")
            
            # Check for specific error types and return appropriate responses
            if 'unique_constraint' in str(e).lower() or 'duplicate' in str(e).lower():
                return Response(
                    {'detail': 'A channel with these parameters already exists'},
                    status=status.HTTP_409_CONFLICT
                )
                
            return Response(
                {'detail': 'An error occurred while creating the channel'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
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