from django.db import connection
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from django_tenants.utils import schema_context, get_tenant_model
from rest_framework import status
from rest_framework.response import Response

from .authentication import TenantJWTAuthentication

class TenantAwareAPIView(APIView):
    """
    Base view that handles tenant-aware requests with JWT authentication.
    Automatically sets the schema context for the request.
    """
    authentication_classes = [TenantJWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def setup_tenant_context(self, request):
        """
        Set up tenant context based on the JWT token.
        """
        # Get schema_name from token
        auth_header = request.META.get('HTTP_AUTHORIZATION', '').split()
        
        if len(auth_header) == 2 and auth_header[0].lower() == 'bearer':
            try:
                # Get the validated token
                validated_token = TenantJWTAuthentication().get_validated_token(auth_header[1])
                schema_name = validated_token.get('schema_name')
                
                if schema_name:
                    # Get the tenant model
                    TenantModel = get_tenant_model()
                    try:
                        # Get the tenant and set it on the connection
                        tenant = TenantModel.objects.get(schema_name=schema_name)
                        connection.set_tenant(tenant)
                        request.tenant = tenant
                        return True
                    except TenantModel.DoesNotExist:
                        return False
                        
            except (InvalidToken, TokenError) as e:
                # Token is invalid, permission classes will handle this
                pass
        return False
    
    def initial(self, request, *args, **kwargs):
        """
        Run before anything else in the view.
        Sets up the tenant context.
        """
        super().initial(request, *args, **kwargs)
        
        # Set up tenant context
        if not hasattr(request, 'tenant'):
            if not self.setup_tenant_context(request):
                return Response(
                    {'detail': 'Unable to determine tenant context'},
                    status=status.HTTP_400_BAD_REQUEST
                )
    
    def dispatch(self, request, *args, **kwargs):
        """
        Override dispatch to handle tenant context and transactions.
        """
        # Ensure tenant is set up
        if not hasattr(request, 'tenant'):
            return Response(
                {'detail': 'Unable to determine tenant context'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Process the request within the tenant's schema context
        with schema_context(request.tenant.schema_name):
            try:
                # Call the parent's dispatch to handle the request
                response = super().dispatch(request, *args, **kwargs)
                return response
                
            except Exception as e:
                # Log the error and re-raise
                import logging
                logger = logging.getLogger(__name__)
                logger.exception("Error processing request")
                raise
        
        return self.finalize_response(request, response, *args, **kwargs)
    
    def handle_exception(self, exc):
        """
        Handle any exception that occurs, by returning an appropriate response.
        """
        if isinstance(exc, InvalidToken):
            return Response(
                {'error': 'Invalid or expired token'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        return super().handle_exception(exc)
