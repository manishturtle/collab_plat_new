
# apps/shared/authentication.py
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import exceptions
from django.utils.translation import gettext_lazy as _
from django_tenants.utils import schema_context, get_tenant_model
from django.db import connection
import logging

logger = logging.getLogger(__name__)

class TenantJWTAuthentication(JWTAuthentication):
    """
    Custom JWT authentication that verifies the user exists and is active
    in the tenant's schema on every request.
    """
    def get_user(self, validated_token):
        """
        Find and return a user using the given validated token.
        """
        try:
            # Debug: Log the incoming token
            logger.debug(f"Validated token: {validated_token}")
            
            # Extract token claims
            user_id = validated_token.get('user_id')
            tenant_id = validated_token.get('tenant_id')
            schema_name = validated_token.get('schema_name')
            
            # Debug: Log extracted values
            logger.debug(f"Extracted - user_id: {user_id}, tenant_id: {tenant_id}, schema_name: {schema_name}")
            
            # Validate required claims
            if not all([user_id, schema_name]):
                missing = [k for k, v in {
                    'user_id': user_id,
                    'schema_name': schema_name
                } if not v]
                
                error_msg = f'Missing required token claims: {", ".join(missing)}'
                logger.error(error_msg)
                raise exceptions.AuthenticationFailed(
                    error_msg,
                    code='missing_claims'
                )

            # Get the tenant model
            tenant_model = get_tenant_model()
            
            try:
                # Get the tenant
                tenant = tenant_model.objects.get(schema_name=schema_name)
                logger.debug(f"Found tenant: {tenant.schema_name}")
                
                # Set the tenant on the connection
                connection.set_tenant(tenant)
                
                # Get the user model
                user_model = self.user_model
                logger.debug(f"Using user model: {user_model.__name__}")
                
                try:
                    # Get the user from the tenant's schema
                    user = user_model.objects.get(
                        id=user_id,
                        is_active=True
                    )
                    
                    # Add the tenant to the user object for later use
                    user.tenant = tenant
                    
                    logger.debug(f"Successfully authenticated user: {user.email} in tenant: {tenant.schema_name}")
                    return user
                    
                except user_model.DoesNotExist:
                    error_msg = f"User not found or inactive (ID: {user_id})"
                    logger.error(error_msg)
                    raise exceptions.AuthenticationFailed(
                        error_msg,
                        code='user_not_found'
                    )
                
            except tenant_model.DoesNotExist:
                error_msg = f"Tenant not found (schema: {schema_name})"
                logger.error(error_msg)
                raise exceptions.AuthenticationFailed(
                    error_msg,
                    code='tenant_not_found'
                )
                
        except Exception as e:
            # Log the full exception with traceback
            logger.exception("Authentication error")
            # Make sure to reset the connection to public schema on error
            connection.set_schema_to_public()
            raise exceptions.AuthenticationFailed(
                f"Authentication failed: {str(e)}",
                code='authentication_error'
            )
    
    def authenticate(self, request):
        """
        Override the authenticate method to ensure proper tenant context.
        """
        # Let the parent class handle the token validation
        result = super().authenticate(request)
        
        if result is not None:
            user, token = result
            # Set the tenant on the user object if it's not already set
            if hasattr(token, 'payload') and 'schema_name' in token.payload:
                schema_name = token.payload['schema_name']
                tenant_model = get_tenant_model()
                try:
                    tenant = tenant_model.objects.get(schema_name=schema_name)
                    user.tenant = tenant
                except tenant_model.DoesNotExist:
                    logger.error(f"Tenant not found during authentication: {schema_name}")
        
        return result