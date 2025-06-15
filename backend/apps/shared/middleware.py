from django_tenants.middleware.main import TenantMainMiddleware
from django_tenants.utils import get_tenant_model, schema_context
from django.db import connection
import logging
import jwt
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework_simplejwt.settings import api_settings as jwt_settings

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
            # Set the tenant on the connection and request
            connection.set_tenant(tenant)
            request.tenant = tenant
            logger.debug(f"Set tenant from JWT token: {tenant.schema_name}")
        else:
            # Fall back to parent class (hostname-based) tenant resolution
            super().process_request(request)
            logger.debug(f"Set tenant from hostname: {getattr(request, 'tenant', None)}")
            
        # Ensure the tenant is set on the connection
        if hasattr(request, 'tenant') and request.tenant:
            connection.set_tenant(request.tenant)
