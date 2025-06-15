from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from django_tenants.utils import schema_context
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
    
    def initial(self, request, *args, **kwargs):
        """
        Run before anything else in the view.
        Sets the schema context based on the JWT token.
        """
        super().initial(request, *args, **kwargs)
        
        # Get schema_name from token
        auth_header = request.META.get('HTTP_AUTHORIZATION', '').split()
        
        if len(auth_header) == 2 and auth_header[0].lower() == 'bearer':
            try:
                # Get the validated token
                validated_token = TenantJWTAuthentication().get_validated_token(auth_header[1])
                schema_name = validated_token.get('schema_name')
                
                if schema_name:
                    # Set the schema for this request
                    print("schema_name::", schema_name)
                    request.tenant_schema = schema_name
                    
            except (InvalidToken, TokenError) as e:
                # Token is invalid, permission classes will handle this
                pass
    
    def dispatch(self, request, *args, **kwargs):
        """
        Override dispatch to set the schema context.
        """
        # Call the parent's dispatch to run authentication/permission checks
        response = super().dispatch(request, *args, **kwargs)
        
        # Set schema context if we have a schema
        if hasattr(request, 'tenant_schema'):
            with schema_context(request.tenant_schema):
                return self.finalize_response(request, response, *args, **kwargs)
        
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
