"""
WebSocket authentication and tenant middleware for the chat application.
"""
import logging
from urllib.parse import parse_qs
from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django_tenants.utils import get_tenant_model
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from django.db import close_old_connections, connection
from django.utils import timezone

# Get the user model
User = get_user_model()
logger = logging.getLogger(__name__)

class WebSocketJWTMiddleware:
    """
    Middleware that validates JWT tokens and sets up tenant context.
    This is a synchronous version that can be used with database_sync_to_async.
    """
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        # Only process WebSocket connections
        if scope.get('type') != 'websocket':
            return await self.app(scope, receive, send)
            
        logger.debug('WebSocket connection initiated')
            
        # Close any stale database connections
        close_old_connections()
        
        # Initialize scope with default values
        scope['user'] = AnonymousUser()
        scope['tenant'] = None
        
        try:
            # Get the token from the query string
            query_string = scope.get('query_string', b'').decode('utf-8')
            query_params = parse_qs(query_string)
            token = query_params.get('token', [''])[0]
            
            logger.debug(f'WebSocket connection attempt with token: {token[:10]}...' if token else 'No token provided')
            
            if not token:
                error_msg = 'No authentication token provided in WebSocket connection'
                logger.warning(error_msg)
                await self.send_error_and_close(send, error_msg)
                return
                
            try:
                # Validate the token and get user and tenant
                user, tenant = await self.authenticate_token(token)
                
                if not user:
                    error_msg = 'No user found for the provided token'
                    logger.warning(error_msg)
                    await self.send_error_and_close(send, error_msg)
                    return
                    
                if not user.is_active:
                    error_msg = f'User {user.id} is not active'
                    logger.warning(error_msg)
                    await self.send_error_and_close(send, error_msg)
                    return
                    
                if not tenant:
                    error_msg = 'No tenant found for the provided token'
                    logger.warning(error_msg)
                    await self.send_error_and_close(send, error_msg)
                    return
                    
                # Set the authenticated user and tenant
                scope['user'] = user
                scope['tenant'] = tenant
                connection.set_tenant(tenant)
                
                # Update user's last login and online status
                await self.update_user_status(user)
                
                logger.info(f'WebSocket connection authenticated for user {user.id} on tenant {tenant.schema_name}')
                
                # Proceed with the connection
                return await self.app(scope, receive, send)
                
            except Exception as auth_error:
                logger.error(f'Authentication error: {str(auth_error)}', exc_info=True)
                await self.send_error_and_close(send, 'Authentication failed')
                return
            
        except (InvalidToken, TokenError) as e:
            error_msg = f'Invalid token: {str(e)}'
            logger.warning(error_msg)
            await self.send_error_and_close(send, 'Invalid authentication token')
            return
            
        except Exception as e:
            error_msg = f'Unexpected error during WebSocket authentication: {str(e)}'
            logger.error(error_msg, exc_info=True)
            await self.send_error_and_close(send, 'Internal server error during authentication')
            return
    
    async def send_error_and_close(self, send, message):
        """Send an error message and close the WebSocket connection."""
        await send({
            'type': 'websocket.close',
            'code': 4000,  # Custom close code for authentication failure
            'reason': message
        })
    
    @database_sync_to_async
    def authenticate_token(self, token):
        """Validate JWT token and return user and tenant."""
        try:
            access_token = AccessToken(token)
            user_id = access_token.get('user_id')
            tenant_id = access_token.get('tenant_id')
            schema_name = access_token.get('schema_name')
            
            if not all([user_id, tenant_id, schema_name]):
                raise ValueError('Missing required token claims')
            
            # Get tenant
            tenant_model = get_tenant_model()
            tenant = tenant_model.objects.get(id=tenant_id, schema_name=schema_name)
            
            # Set tenant for this thread
            connection.set_tenant(tenant)
            
            # Get user
            user = User.objects.get(id=user_id)
                
            return user, tenant
            
        except (tenant_model.DoesNotExist, User.DoesNotExist) as e:
            logger.error(f'User or tenant not found: {str(e)}')
            return None, None
        except Exception as e:
            logger.error(f'Error in authenticate_token: {str(e)}', exc_info=True)
            return None, None
    
    @database_sync_to_async
    def update_user_status(self, user):
        """Update user's last login and online status."""
        try:
            update_fields = []
            
            if hasattr(user, 'last_login'):
                user.last_login = timezone.now()
                update_fields.append('last_login')
            
            if hasattr(user, 'is_online') and not user.is_online:
                user.is_online = True
                update_fields.append('is_online')
            
            if update_fields:
                User.objects.filter(pk=user.pk).update(
                    **{field: getattr(user, field) for field in update_fields}
                )
                
        except Exception as e:
            logger.error(f'Error updating user status: {str(e)}', exc_info=True)


# WebSocket middleware stack
def JWTAuthMiddlewareStack(inner):
    """
    Stack the JWT auth middleware with the default middleware.
    """
    from channels.auth import AuthMiddlewareStack
    return WebSocketJWTMiddleware(AuthMiddlewareStack(inner))
