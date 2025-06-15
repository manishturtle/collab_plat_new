import os
import sys

# Add the project to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

# Import the user model after setup
from django.contrib.auth import get_user_model
from django_tenants.utils import schema_context

# List users in the public schema (shared)
print("Users in public schema:")
User = get_user_model()
users = User.objects.all()
for user in users:
    print(f"ID: {user.id}, Email: {user.email}, Is Active: {user.is_active}, Is Staff: {user.is_staff}")

# List users in the tenant schema
try:
    with schema_context('turtlesoftware'):
        print("\nUsers in turtlesoftware tenant:")
        users = User.objects.all()
        for user in users:
            print(f"ID: {user.id}, Email: {user.email}, Is Active: {user.is_active}, Is Staff: {user.is_staff}")
except Exception as e:
    print(f"\nError accessing tenant schema: {e}")
