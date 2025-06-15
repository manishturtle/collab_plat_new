# from rest_framework_simplejwt.authentication import JWTAuthentication
# from rest_framework import exceptions
# from django.utils.translation import gettext_lazy as _
# from django_tenants.utils import schema_context
# from django.conf import settings

# class TenantJWTAuthentication(JWTAuthentication):
#     """
#     Custom JWT authentication that also verifies the user exists and is active
#     in the tenant's schema on every request.
#     """
#     def get_user(self, validated_token):
#         """
#         Find and return a user using the given validated token.
#         """
#         try:
#             user_id = validated_token[settings.USER_ID_CLAIM]
#             tenant_id = validated_token.get('tenant_id')
#             schema_name = validated_token.get('schema_name')
            
#             if not tenant_id or not schema_name:
#                 raise exceptions.AuthenticationFailed(
#                     _('Invalid token: Missing tenant information'),
#                     code='invalid_token'
#                 )
            
#             # Get the user model
#             user_model = self.user_model
            
#             # Get user from the tenant's schema
#             with schema_context(schema_name):
#                 try:
#                     user = user_model.objects.get(**{settings.USER_ID_FIELD: user_id})
                    
#                     # Check if user is active
#                     if not user.is_active:
#                         raise exceptions.AuthenticationFailed(
#                             _('User is inactive'),
#                             code='user_inactive'
#                         )
                    
#                     return user
                    
#                 except user_model.DoesNotExist:
#                     raise exceptions.AuthenticationFailed(
#                         _('User not found'),
#                         code='user_not_found'
#                     )
                    
#         except KeyError:
#             raise exceptions.AuthenticationFailed(
#                 _('Invalid token: Missing required claims'),
#                 code='invalid_token'
#             )


# apps/shared/authentication.py
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import exceptions
from django.utils.translation import gettext_lazy as _
from django_tenants.utils import schema_context, get_tenant_model
import logging

logger = logging.getLogger(__name__)

class TenantJWTAuthentication(JWTAuthentication):
    """
    Custom JWT authentication that also verifies the user exists and is active
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
            if not all([user_id, tenant_id, schema_name]):
                missing = [k for k, v in {
                    'user_id': user_id,
                    'tenant_id': tenant_id,
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
                # Switch to the tenant's schema using schema_name (string) instead of tenant object
                logger.debug(f"Attempting to switch to tenant schema: {schema_name}")
                
                with schema_context(schema_name):  # Pass schema_name directly
                    logger.debug(f"Successfully switched to tenant: {schema_name}")
                    
                    # Get the user model
                    user_model = self.user_model
                    logger.debug(f"Using user model: {user_model.__name__}")
                    
                    try:
                        user = user_model.objects.get(
                            id=user_id,
                            is_active=True
                        )
                        logger.debug(f"Successfully authenticated user: {user}")
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
            raise exceptions.AuthenticationFailed(
                f"Authentication failed: {str(e)}",
                code='authentication_error'
            )