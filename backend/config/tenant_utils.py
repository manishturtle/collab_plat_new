"""
Tenant utilities including the tenant limit callback function.
"""

def tenant_limit_callback(tenant):
    """
    Callback function to limit the number of tenants that can be created.
    
    Args:
        tenant: The tenant instance being created.
        
    Returns:
        bool: True if the tenant can be created, False otherwise.
    """
    # You can implement your tenant limit logic here
    # For example, check if the current number of tenants is below a certain limit
    # from .models import TenantModel
    # return TenantModel.objects.count() < 100  # Example: limit to 100 tenants
    return True  # For now, allow unlimited tenants
