from django_tenants.middleware.main import TenantMainMiddleware
from django_tenants.utils import get_tenant_model, schema_context
from django.db import connection
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.settings import api_settings as jwt_settings
import jwt
import logging

User = get_user_model()
logger = logging.getLogger(__name__)


class CustomTenantMiddleware(TenantMainMiddleware):
    """
    Custom tenant middleware that ensures the tenant is set from the JWT token.
    """
    def get_tenant_from_token(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '').split()
        
        if not auth_header or len(auth_header) != 2 or auth_header[0].lower() != 'bearer':
            return None
            
        token = auth_header[1]
        try:
            # Decode the token without verification first to get the schema_name
            token_data = jwt.decode(
                token,
                options={"verify_signature": False},
                algorithms=[jwt_settings.ALGORITHM]
            )
            
            schema_name = token_data.get('schema_name')
            if not schema_name:
                logger.warning("No schema_name found in JWT token")
                return None
                
            tenant_model = get_tenant_model()
            try:
                tenant = tenant_model.objects.get(schema_name=schema_name)
                logger.debug(f"Found tenant from JWT token: {schema_name}")
                return tenant
            except tenant_model.DoesNotExist:
                logger.error(f"Tenant not found for schema: {schema_name}")
                return None
                
        except jwt.PyJWTError as e:
            logger.warning(f"JWT decode error: {str(e)}")
            return None

    def process_request(self, request):
        # First, try to get tenant from JWT token
        tenant = self.get_tenant_from_token(request)
        
        if tenant:
            request.tenant = tenant
            connection.set_tenant(request.tenant)
            logger.debug(f"Set tenant from JWT token: {tenant.schema_name}")
        else:
            # Fall back to parent class (hostname-based) tenant resolution
            super().process_request(request)


class WebSocketJWTAuthMiddleware(BaseMiddleware):
    """
    Custom WebSocket middleware that authenticates users using JWT tokens.
    """
    async def __call__(self, scope, receive, send):
        # Get the token from the query string
        query_params = dict(
            (x.split('=') if '=' in x else (x, ''))
            for x in scope.get('query_string', b'').decode().split('&')
        )
        token = query_params.get('token')
        
        if not token:
            # Try to get token from headers (for wss:// connections)
            headers = dict(scope.get('headers', []))
            auth_header = headers.get(b'authorization', b'').decode()
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
        
        if not token:
            scope['user'] = AnonymousUser()
            return await super().__call__(scope, receive, send)
        
        try:
            # Validate token and get user
            user = await self.get_user_from_token(token)
            if user:
                scope['user'] = user
                # Set tenant schema if available in the token
                await self.set_tenant_schema(scope, token)
            else:
                scope['user'] = AnonymousUser()
        except Exception as e:
            logger.error(f"WebSocket authentication error: {str(e)}")
            scope['user'] = AnonymousUser()
        
        return await super().__call__(scope, receive, send)
    
    @database_sync_to_async
    def get_user_from_token(self, token):
        """Get user from JWT token."""
        try:
            # Decode token to get user ID
            decoded_token = AccessToken(token)
            user_id = decoded_token.get('user_id')
            
            if not user_id:
                return None
                
            # Get user from database
            try:
                user = User.objects.get(id=user_id, is_active=True)
                return user
            except User.DoesNotExist:
                return None
                
        except (InvalidToken, TokenError) as e:
            logger.warning(f"Invalid token: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error getting user from token: {str(e)}")
            return None
    
    @database_sync_to_async
    def set_tenant_schema(self, scope, token):
        """Set tenant schema from JWT token if available."""
        try:
            # Decode token without verification to get schema_name
            decoded = jwt.decode(
                token,
                options={"verify_signature": False},
                algorithms=[jwt_settings.ALGORITHM]
            )
            
            schema_name = decoded.get('schema_name')
            if schema_name:
                # Set the schema name in the connection
                connection.set_schema(schema_name)
                scope['schema_name'] = schema_name
                
        except Exception as e:
            logger.warning(f"Error setting tenant schema: {str(e)}")
