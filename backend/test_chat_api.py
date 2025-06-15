import os
import sys
import json
import requests
from django.core.management import execute_from_command_line

# Add the project to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

# Import Django models after setup
from django.contrib.auth import get_user_model
from apps.chat.models import ChatChannel, ChannelParticipant

def get_auth_token():
    """Get authentication token for API requests"""
    url = "http://localhost:8000/api/turtlesoftware/auth/login/"  # Using the tenant slug 'turtlesoftware'
    data = {
        "email": "ankit@turtlesoftware.co",  # Use the test user's email
        "password": "India@123"  # Use the test user's password
    }
    
    try:
        response = requests.post(url, json=data)
        response.raise_for_status()
        response_data = response.json()
        print("Login response:", json.dumps(response_data, indent=2))
        
        # Extract the access token from the nested tokens object
        if 'tokens' in response_data and 'access' in response_data['tokens']:
            return response_data['tokens']['access']
        elif 'access' in response_data:
            return response_data["access"]
        elif 'token' in response_data:
            return response_data["token"]
        else:
            print("Unexpected response format. Could not find access token.")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"Error getting auth token: {e}")
        if hasattr(e, 'response') and e.response is not None:
            if e.response.status_code == 401:
                print("Invalid credentials. Please check the email and password.")
            elif e.response.status_code == 400:
                print("Bad request. Response:", e.response.text)
            else:
                print(f"Unexpected error: {e.response.status_code} - {e.response.text}")
        return None

def test_chat_api():
    # Get auth token
    token = get_auth_token()
    if not token:
        print("Failed to get auth token. Exiting.")
        return
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    base_url = "http://localhost:8000/api/chat/turtlesoftware"  # Replace with your tenant slug
    
    print("=== Testing Chat API ===\n")
    
    # 1. List channels
    print("1. Listing channels...")
    try:
        response = requests.get(f"{base_url}/channels/", headers=headers)
        response.raise_for_status()
        channels = response.json()
        print(f"Found {len(channels)} channels")
        if channels:
            print("First channel:", json.dumps(channels[0], indent=2))
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error listing channels: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response status: {e.response.status_code}")
            print("Response content:", e.response.text)
    except Exception as e:
        print(f"Unexpected error listing channels: {e}")
    
    # 2. Create a new channel
    print("\n2. Creating a new channel...")
    try:
        channel_data = {
            "channel_type": "group",
            "name": "Test Channel",
            "participants": [1]  # User IDs to add to the channel
        }
        print("Sending request to:", f"{base_url}/channels/")
        print("Request data:", json.dumps(channel_data, indent=2))
        
        response = requests.post(
            f"{base_url}/channels/", 
            json=channel_data, 
            headers=headers
        )
        response.raise_for_status()
        channel = response.json()
        print(f"Created channel: {channel['id']}")
        print("Channel details:", json.dumps(channel, indent=2))
        channel_id = channel["id"]
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error creating channel: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response status: {e.response.status_code}")
            print("Response content:", e.response.text)
        channel_id = None
    except Exception as e:
        print(f"Unexpected error creating channel: {e}")
        channel_id = None
    
    if not channel_id:
        print("No channel ID available for further tests. Exiting.")
        return
    
    # 3. Get channel details
    print(f"\n3. Getting details for channel {channel_id}...")
    try:
        response = requests.get(
            f"{base_url}/channels/{channel_id}/", 
            headers=headers
        )
        response.raise_for_status()
        print("Channel details:", json.dumps(response.json(), indent=2))
    except Exception as e:
        print(f"Error getting channel details: {e}")
    
    # 4. Send a message
    print(f"\n4. Sending a message to channel {channel_id}...")
    try:
        message_data = {
            "content": "Hello, this is a test message!",
            "message_type": "text"
        }
        response = requests.post(
            f"{base_url}/channels/{channel_id}/send_message/", 
            json=message_data, 
            headers=headers
        )
        response.raise_for_status()
        message = response.json()
        print(f"Sent message: {message['id']}")
        message_id = message["id"]
    except Exception as e:
        print(f"Error sending message: {e}")
        message_id = None
    
    # 5. Get messages in the channel
    print(f"\n5. Getting messages in channel {channel_id}...")
    try:
        response = requests.get(
            f"{base_url}/channels/{channel_id}/messages/", 
            headers=headers
        )
        response.raise_for_status()
        messages = response.json()
        print(f"Found {len(messages)} messages")
        if messages:
            print("First message:", json.dumps(messages[0], indent=2))
    except Exception as e:
        print(f"Error getting messages: {e}")
    
    # 6. Mark messages as read
    if message_id:
        print(f"\n6. Marking message {message_id} as read...")
        try:
            response = requests.post(
                f"{base_url}/channels/{channel_id}/mark_read/", 
                json={"message_ids": [message_id]}, 
                headers=headers
            )
            response.raise_for_status()
            print("Marked messages as read")
        except Exception as e:
            print(f"Error marking messages as read: {e}")
    
    print("\n=== Chat API Tests Complete ===")

if __name__ == "__main__":
    test_chat_api()
