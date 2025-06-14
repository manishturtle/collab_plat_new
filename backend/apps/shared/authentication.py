from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import exceptions
from django.utils.translation import gettext_lazy as _
from django_tenants.utils import schema_context

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
            user_id = validated_token[settings.USER_ID_CLAIM]
            tenant_id = validated_token.get('tenant_id')
            schema_name = validated_token.get('schema_name')
            
            if not tenant_id or not schema_name:
                raise exceptions.AuthenticationFailed(
                    _('Invalid token: Missing tenant information'),
                    code='invalid_token'
                )
            
            # Get the user model
            user_model = self.user_model
            
            # Get user from the tenant's schema
            with schema_context(schema_name):
                try:
                    user = user_model.objects.get(**{settings.USER_ID_FIELD: user_id})
                    
                    # Check if user is active
                    if not user.is_active:
                        raise exceptions.AuthenticationFailed(
                            _('User is inactive'),
                            code='user_inactive'
                        )
                    
                    return user
                    
                except user_model.DoesNotExist:
                    raise exceptions.AuthenticationFailed(
                        _('User not found'),
                        code='user_not_found'
                    )
                    
        except KeyError:
            raise exceptions.AuthenticationFailed(
                _('Invalid token: Missing required claims'),
                code='invalid_token'
            )
