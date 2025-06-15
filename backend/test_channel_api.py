import os
import sys
import json
import requests

# Add the project to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

# Import Django modules after setup
from django.contrib.auth import get_user_model
from django_tenants.utils import schema_context

def test_channel_api_direct():
    """Test creating a direct channel via the API endpoint"""
    print("=== Testing Channel API (Direct) ===")
    
    # Setup test parameters
    schema_name = 'bingo_travels'
    user_id = 1  # This would be the authenticated user
    participant_id = 2  # The user to create a direct channel with
    
    # Get user info for both users
    with schema_context(schema_name):
        User = get_user_model()
        
        try:
            user = User.objects.get(id=user_id)
            participant = User.objects.get(id=participant_id)
            print(f"Found user: {user.email} (ID: {user.id})")
            print(f"Found participant: {participant.email} (ID: {participant.id})")
        except User.DoesNotExist as e:
            print(f"Error: User not found - {e}")
            return
    
    # Create a test management command to get an auth token (simplified for this test)
    auth_token = None
    try:
        url = "http://localhost:8000/api/bingo_travels/auth/login/"
        data = {
            "email": "yash@turtlesoftware.co",  # Should match user_id=1
            "password": "password123"
        }
        print(f"\nTrying to authenticate as: {data['email']}")
        response = requests.post(url, json=data)
        
        if response.status_code == 200:
            response_data = response.json()
            
            # Extract token from the response
            if 'tokens' in response_data and 'access' in response_data['tokens']:
                auth_token = response_data['tokens']['access']
                print("Authentication successful")
            else:
                print(f"Unexpected response format: {response_data}")
        else:
            print(f"Authentication failed: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"Authentication error: {e}")
    
    if not auth_token:
        print("Could not obtain auth token. Exiting.")
        return
    
    # Test the channel creation endpoint
    try:
        url = f"http://localhost:8000/api/chat/{schema_name}/channels/"
        headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }
        
        # Create a direct channel with just the participant ID
        data = {
            "channel_type": "direct",
            "participants": [participant_id]
        }
        
        print(f"\nCreating channel with data: {json.dumps(data, indent=2)}")
        response = requests.post(url, json=data, headers=headers)
        
        print(f"Response status: {response.status_code}")
        if response.status_code in (200, 201):
            response_data = response.json()
            print(f"Channel created successfully: {json.dumps(response_data, indent=2)}")
            return True
        else:
            print(f"Failed to create channel: {response.text}")
            return False
    except Exception as e:
        print(f"Error creating channel: {e}")
        return False

if __name__ == "__main__":
    success = test_channel_api_direct()
    if success:
        print("\n=== Test completed successfully ===")
    else:
        print("\n=== Test failed ===")
