import unittest
import json
import requests
from django.test import TestCase
from rest_framework import status

class ChatAPITestCase(TestCase):
    """Test cases for Chat API endpoints"""

    def setUp(self):
        """Set up test data and client"""
        self.base_url = 'http://localhost:8014/api/chat/bingo_travels'
        self.token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzQ5OTgwMjM0LCJpYXQiOjE3NDk5NzY2MzQsImp0aSI6ImUxNjRlMDhhYjUwYTRkOTRhZTJjYWRlMjgzNDc3Mzg3IiwidXNlcl9pZCI6MSwidGVuYW50X2lkIjoiNTIxIiwic2NoZW1hX25hbWUiOiJiaW5nb190cmF2ZWxzIn0.m7Gr2uHdd2v0IIzZsWLa5hIABdR0fowBpZo4GPNoXKA'
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.token}'
        }

    def test_create_channel(self):
        """Test creating a new chat channel"""
        url = f"{self.base_url}/channels/"
        data = {
            "channel_type": "direct",
            "participants": [2],
            "host_application_id": 1,
            "context_object_type": "wfwef",
            "context_object_id": 12
        }

        try:
            response = requests.post(
                url,
                headers=self.headers,
                json=data
            )
            
            print(f"\n=== Test Create Channel ===")
            print(f"Status Code: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2) if response.text else 'No content'}")
            
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            response_data = response.json()
            self.assertIn('id', response_data)
            self.assertEqual(response_data['channel_type'], 'direct')
            
        except requests.exceptions.RequestException as e:
            self.fail(f"API request failed: {str(e)}")

    def test_list_channels(self):
        """Test listing all channels"""
        url = f"{self.base_url}/channels/"
        
        try:
            response = requests.get(
                url,
                headers=self.headers
            )
            
            print(f"\n=== Test List Channels ===")
            print(f"Status Code: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2) if response.text else 'No content'}")
            
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertIsInstance(response.json(), list)
            
        except requests.exceptions.RequestException as e:
            self.fail(f"API request failed: {str(e)}")


if __name__ == '__main__':
    unittest.main()
