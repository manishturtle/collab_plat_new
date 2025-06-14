"""
Views for shared functionality including authentication.
"""
import importlib.metadata
import logging
from django.db import connection
from django.http import JsonResponse

logger = logging.getLogger(__name__)
from rest_framework.views import APIView
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django_tenants.utils import schema_context, get_tenant_model, get_tenant_domain_model
from django.apps import apps
from .models import Tenant, Domain, TenantUserModel as UserModel

# Get the tenant model from settings
def get_tenant_model():
    return Tenant

# Get the domain model from settings
def get_domain_model():
    return Domain

class TenantLoginView(APIView):
    """
    API endpoint that allows users to log in with their email and password.
    URL: /api/<tenant_slug>/auth/login/
    """
    authentication_classes = []  # No authentication needed for login
    permission_classes = []

    def post(self, request, tenant_slug):
        """
        Handle POST request for user login.
        """
        email = request.data.get('email')
        password = request.data.get('password')

        # Validate required fields
        if not email or not password:
            return JsonResponse(
                {'error': 'Email and password are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Get the tenant model
            TenantModel = get_tenant_model()
            DomainModel = get_domain_model()
            
            try:
                logger.info(f"Looking up domain with domain: {tenant_slug}")
                # Look up tenant by schema_name (which should match the tenant_slug in the URL)
                tenant = TenantModel.objects.get(schema_name=tenant_slug)
                logger.info(f"Found tenant: {getattr(tenant, 'name', 'N/A')} (ID: {tenant.id}, Schema: {tenant.schema_name})")
            except TenantModel.DoesNotExist:
                logger.error(f"Tenant not found: {tenant_slug}")
                return JsonResponse(
                    {'error': 'Tenant not found'},
                    status=status.HTTP_404_NOT_FOUND
                )

            # Switch to the tenant's schema
            connection.set_schema(tenant.schema_name)

            # Try to authenticate the user using our custom user model
            try:
                logger.info(f"Looking up user with email: {email} in tenant: {tenant.schema_name}")
                # Get the user from the tenant's schema
                with schema_context(tenant.schema_name):
                    user = UserModel.objects.get(email=email, is_active=True)
                    logger.info(f"Found user: {user.email} (ID: {user.id})")
                    
                    # Verify password
                    if not user.check_password(password):
                        logger.warning(f"Invalid password for user: {email}")
                        return JsonResponse(
                            {'error': 'Invalid email or password'},
                            status=status.HTTP_401_UNAUTHORIZED
                        )

                    # Generate JWT tokens
                    try:
                        logger.info(f"Generating tokens for user: {user.email}")
                        # Create token with custom claims
                        refresh = RefreshToken.for_user(user)
                        # Add tenant_id to the token payload
                        refresh['tenant_id'] = str(tenant.id)
                        refresh['schema_name'] = tenant.schema_name
                        
                        # Get user data
                        user_data = {
                            'id': user.id,
                            'email': user.email,
                            'tenant_id': tenant.id,
                            'first_name': getattr(user, 'first_name', ''),
                            'last_name': getattr(user, 'last_name', ''),
                            'is_staff': user.is_staff,
                            'is_superuser': user.is_superuser,
                        }

                        # Get tenant data
                        tenant_data = {
                            'id': tenant.id,
                            'name': getattr(tenant, 'name', ''),
                            'schema_name': tenant.schema_name,
                        }

                        response_data = {
                            'message': 'Login successful',
                            'user': user_data,
                            'tokens': {
                                'refresh': str(refresh),
                                'access': str(refresh.access_token),
                            },
                            'tenant': tenant_data,
                        }

                        logger.info(f"Login successful for user: {user.email}")
                        return JsonResponse(response_data, status=status.HTTP_200_OK)

                    except Exception as e:
                        logger.error(f"Error generating tokens: {str(e)}")
                        return JsonResponse(
                            {'error': 'Error generating authentication tokens'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR
                        )

            except UserModel.DoesNotExist:
                logger.warning(f"User not found for email: {email}")
                return JsonResponse(
                    {'error': 'Invalid email or password'},
                    status=status.HTTP_401_UNAUTHORIZED
                )

        except Exception as e:
            logger.error(f"Unexpected error during login: {str(e)}", exc_info=True)
            return JsonResponse(
                {'error': 'An unexpected error occurred'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        finally:
            # Make sure to switch back to the public schema
            connection.set_schema_to_public()
