# from .base_views import TenantAwareAPIView

# class ProtectedView(TenantAwareAPIView):
#     def get(self, request):
#         # This will only be accessible with a valid JWT token
#         # The schema is automatically set based on the token
#         return Response({"message": "This is a protected endpoint"})
		
		
# 		#For public views (no authentication):
# from rest_framework.views import APIView

# class PublicView(APIView):
#     authentication_classes = []  # No authentication required
#     permission_classes = []      # No permissions required
    
#     def get(self, request):
#         return Response({"message": "This is a public endpoint"})