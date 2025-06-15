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
    def messages(self, request, pk=None, tenant_slug=None):
        """
        Get messages for a specific channel.
        """
        try:
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
            
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.exception("Error fetching messages")
            return Response(
                {'detail': 'Failed to fetch messages'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'])
    def send_message(self, request, pk=None, tenant_slug=None):
        """
        Send a message to a channel.
        """
        # The tenant_slug parameter is automatically passed from the URL
        # but we don't need to use it here as the tenant context is already set
        # by the TenantAwareAPIView
        
        channel = self.get_object()

        # Validate input
        content = request.data.get('content')
        if not content:
            return Response(
                {'detail': 'Message content is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
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
            
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.exception("Error sending message")
            return Response(
                {'detail': 'Failed to send message'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None, tenant_slug=None):
        """
        Mark all messages in a channel as read.
        """
        try:
            channel = self.get_object()
            count = mark_messages_as_read(channel.id, request.user)
            return Response({
                'status': 'success',
                'message': f'Marked {count} messages as read',
                'channel_id': str(channel.id)
            })
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.exception("Error marking messages as read")
            return Response(
                {'detail': 'Failed to mark messages as read'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'])
    def centralized(self, request, pk=None, tenant_slug=None):
        """
        Centralized chat view that combines all channels for the user.
        Returns a structured response with:
        - Direct messages
        - Group channels
        - Contextual chats
        - Unread counts
        """
        from ..models import ChatChannel, UserChannelState
        from ..selectors import get_unread_message_count
        
        try:
            # Get all channels where user is a participant
            channels = ChatChannel.objects.filter(
                participations__user=request.user
            ).prefetch_related('participants', 'participations')
            
            # Get all user channel states for unread counts
            channel_states = {
                state.channel_id: state 
                for state in UserChannelState.objects.filter(
                    user=request.user,
                    channel__in=channels
                )
            }
            
            # Categorize channels
            direct_messages = []
            group_channels = []
            contextual_chats = []
            
            for channel in channels:
                # Get unread count
                unread_count = get_unread_message_count(channel.id, request.user)
                
                # Get last message preview
                last_message = channel.messages.order_by('-created_at').first()
                last_message_preview = None
                if last_message:
                    last_message_preview = {
                        'id': str(last_message.id),
                        'content': last_message.content[:100],
                        'sender_id': last_message.user_id,
                        'created_at': last_message.created_at,
                        'is_own': last_message.user_id == request.user.id
                    }
                
                # Get other participants for direct messages
                other_participants = []
                if channel.channel_type == 'direct':
                    other_participants = [
                        {
                            'id': p.user.id,
                            'username': p.user.username,
                            'email': p.user.email,
                            'avatar': p.user.avatar_url if hasattr(p.user, 'avatar_url') else None
                        }
                        for p in channel.participations.all() 
                        if p.user_id != request.user.id
                    ]
                
                channel_data = {
                    'id': str(channel.id),
                    'name': channel.name,
                    'channel_type': channel.channel_type,
                    'unread_count': unread_count,
                    'last_message': last_message_preview,
                    'created_at': channel.created_at,
                    'updated_at': channel.updated_at,
                    'participants': [
                        {
                            'id': p.user.id,
                            'username': p.user.username,
                            'email': p.user.email,
                            'role': p.role,
                            'is_online': False  # Will be implemented with presence
                        }
                        for p in channel.participations.all()
                    ],
                    'other_participants': other_participants,
                    'context': {
                        'host_application_id': channel.host_application_id,
                        'object_type': channel.context_object_type,
                        'object_id': channel.context_object_id
                    } if channel.channel_type == 'contextual_object' else None
                }
                
                # Categorize
                if channel.channel_type == 'direct':
                    direct_messages.append(channel_data)
                elif channel.channel_type == 'group':
                    group_channels.append(channel_data)
                elif channel.channel_type == 'contextual_object':
                    contextual_chats.append(channel_data)
            
            # Sort channels by last activity (most recent first)
            def sort_key(c):
                return c['last_message']['created_at'] if c['last_message'] else c['created_at']
                
            direct_messages.sort(key=sort_key, reverse=True)
            group_channels.sort(key=sort_key, reverse=True)
            contextual_chats.sort(key=sort_key, reverse=True)
            
            return Response({
                'direct_messages': direct_messages,
                'group_channels': group_channels,
                'contextual_chats': contextual_chats,
                'unread_counts': {
                    'direct': sum(c['unread_count'] for c in direct_messages),
                    'groups': sum(c['unread_count'] for c in group_channels),
                    'contextual': sum(c['unread_count'] for c in contextual_chats),
                    'total': sum(c['unread_count'] for c in direct_messages + group_channels + contextual_chats)
                }
            })
            
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.exception("Error in centralized chat view")
            return Response(
                {'detail': 'Failed to load chat data'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )