# test_chat_api.py
import os
import sys
import json
import requests
from urllib.parse import urljoin

# Configuration
BASE_URL = "http://localhost:8030"
TENANT_SLUG = "turtlesoftware"  # Replace with your tenant slug
API_PREFIX = f"/api/chat/{TENANT_SLUG}"

# Test user credentials
TEST_USERS = [
    {"email": "ankit@turtlesoftware.com", "password": "Qu1ckAss1st@123"},
    {"email": "manish@gmail.com", "password": "Qu1ckAss1st@123"}
]

class TestChatAPI:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        self.channel_id = None
        self.access_tokens = []

    def _make_url(self, path):
        """Helper to build full URLs"""
        return urljoin(BASE_URL, path.lstrip('/'))

    def login_users(self):
        """Log in test users and store their tokens"""
        print("\n=== Logging in users ===")
        for i, user in enumerate(TEST_USERS):
            url = self._make_url(f"/api/{TENANT_SLUG}/auth/login/")
            try:
                response = self.session.post(url, json=user)
                response.raise_for_status()
                token = response.json().get('access')
                self.access_tokens.append(token)
                print(f"User {i+1} logged in successfully")
            except Exception as e:
                print(f"Failed to log in user {i+1}: {e}")
                sys.exit(1)

    def test_create_channel(self):
        """Test creating a new channel"""
        print("\n=== Testing channel creation ===")
        url = self._make_url(f"{API_PREFIX}/channels/")
        headers = {"Authorization": f"Bearer {self.access_tokens[0]}"}
        
        payload = {
            "channel_type": "direct",
            "participants": [2]  # Assuming user2 has ID 2
        }
        
        try:
            response = self.session.post(url, headers=headers, json=payload)
            response.raise_for_status()
            self.channel_id = response.json().get('id')
            print(f"Channel created successfully. ID: {self.channel_id}")
            print("Response:", json.dumps(response.json(), indent=2))
        except Exception as e:
            print(f"Failed to create channel: {e}")

    def test_send_message(self):
        """Test sending a message"""
        if not self.channel_id:
            print("No channel ID available. Skipping message test.")
            return
            
        print("\n=== Testing message sending ===")
        url = self._make_url(f"{API_PREFIX}/channels/{self.channel_id}/send_message/")
        headers = {"Authorization": f"Bearer {self.access_tokens[0]}"}
        
        payload = {
            "content": "Hello from the test script!",
            "content_type": "text/plain"
        }
        
        try:
            response = self.session.post(url, headers=headers, json=payload)
            response.raise_for_status()
            print("Message sent successfully")
            print("Response:", json.dumps(response.json(), indent=2))
        except Exception as e:
            print(f"Failed to send message: {e}")

    def test_list_messages(self):
        """Test listing messages in a channel"""
        if not self.channel_id:
            print("No channel ID available. Skipping message listing test.")
            return
            
        print("\n=== Testing message listing ===")
        url = self._make_url(f"{API_PREFIX}/channels/{self.channel_id}/messages/")
        headers = {"Authorization": f"Bearer {self.access_tokens[0]}"}
        
        try:
            response = self.session.get(url, headers=headers)
            response.raise_for_status()
            print("Messages retrieved successfully")
            print("Response:", json.dumps(response.json(), indent=2))
        except Exception as e:
            print(f"Failed to list messages: {e}")

    def run_all_tests(self):
        """Run all test methods"""
        self.login_users()
        self.test_create_channel()
        self.test_send_message()
        self.test_list_messages()

if __name__ == "__main__":
    tester = TestChatAPI()
    tester.run_all_tests()