import requests
import json
import sys
import logging
from typing import Dict, Any, Tuple, Optional, List

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Suppress SSL warnings
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_auth_token() -> Optional[str]:
    """Authenticate and get JWT token"""
    auth_url = 'http://localhost:8014/api/bingo_travels/auth/login/'
    
    try:
        logger.info("Authenticating with email: yash@turtlesoftware.co")
        response = requests.post(
            auth_url,
            json={"email": "yash@turtlesoftware.co", "password": "India@123"},
            timeout=10,
            verify=False
        )
        
        if response.status_code == 200:
            data = response.json()
            logger.info("Authentication successful")
            access_token = data.get('tokens', {}).get('access')
            if access_token:
                return access_token
            else:
                logger.error("No access token in response")
                return None
        else:
            logger.error(f"Authentication failed: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        logger.exception("Error during authentication:")
        return None

def test_create_channel(base_url: str, headers: Dict[str, str], channel_data: Dict[str, Any]) -> Tuple[bool, Any]:
    """Helper function to test channel creation with given data"""
    create_url = f"{base_url}/channels/"
    
    logger.info("\n=== Testing Channel Creation ===")
    logger.info(f"URL: {create_url}")
    logger.debug("Headers: %s", json.dumps(headers, indent=2))
    logger.debug("Request data: %s", json.dumps(channel_data, indent=2))
    
    try:
        response = requests.post(
            create_url,
            headers=headers,
            json=channel_data,
            timeout=30,
            verify=False
        )
        
        logger.info("=== Response ===")
        logger.info(f"Status Code: {response.status_code}")
        
        try:
            response_data = response.json()
            logger.info("Response Body: %s", json.dumps(response_data, indent=2))
        except json.JSONDecodeError:
            logger.info("Response Body (raw): %s", response.text)
            response_data = response.text
        
        if response.status_code == 201:
            logger.info("=== [SUCCESS] Channel created successfully! ===")
            logger.info("Channel ID: %s", response_data.get('id', 'Unknown'))
            return True, response_data
        else:
            logger.error(f"=== [ERROR] Failed to create channel. Status code: {response.status_code} ===")
            logger.debug("Response headers: %s", response.headers)
            return False, response_data
            
    except requests.exceptions.RequestException as e:
        logger.exception("[ERROR] Request failed")
        if hasattr(e, 'response') and e.response is not None:
            logger.error("Response status: %s", e.response.status_code)
            try:
                logger.error("Error response: %s", e.response.json())
            except:
                logger.error("Error response (raw): %s", e.response.text)
        return False, str(e)
    except Exception as e:
        logger.exception("[ERROR] Unexpected error")
        return False, str(e)

def list_channels(base_url: str, headers: Dict[str, str]) -> Tuple[bool, Any]:
    """List all channels"""
    list_url = f"{base_url}/channels/"
    
    try:
        logger.info("\n=== Listing Channels ===")
        logger.info(f"URL: {list_url}")
        logger.debug(f"Using headers: {headers}")
        
        response = requests.get(
            list_url,
            headers=headers,
            timeout=10,
            verify=False
        )
        
        logger.info("=== Response ===")
        logger.info(f"Status Code: {response.status_code}")
        logger.debug(f"Response Headers: {response.headers}")
        
        try:
            response_data = response.json()
            logger.info("Channels: %s", json.dumps(response_data, indent=2))
        except json.JSONDecodeError:
            logger.info("Response Body (raw): %s", response.text)
            response_data = response.text
        
        if response.status_code == 200:
            logger.info("=== [SUCCESS] Retrieved channel list successfully! ===")
            return True, response_data
        else:
            logger.error(f"=== [ERROR] Failed to retrieve channels. Status code: {response.status_code} ===")
            logger.error(f"Response: {response.text}")
            return False, response_data
            
    except requests.exceptions.RequestException as e:
        logger.exception("[ERROR] Request failed")
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"Response status: {e.response.status_code}")
            logger.error(f"Response text: {e.response.text}")
        return False, str(e)
    except Exception as e:
        logger.exception("[ERROR] Unexpected error")
        return False, str(e)

def run_tests():
    """Run all test cases"""
    # Configuration
    tenant_slug = "bingo_travels"
    base_url = f'http://localhost:8014/api/chat/{tenant_slug}'
    
    logger.info(f"\n{'='*50}")
    logger.info("Starting Chat API Tests")
    logger.info(f"Base URL: {base_url}")
    
    # Step 1: Authenticate and get token
    logger.info("\n=== Step 1: Authenticating... ===")
    token = get_auth_token()
    
    if not token:
        logger.error("Authentication failed. Exiting...")
        return False
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    
    # Step 2: List existing channels
    logger.info("\n=== Step 2: Listing existing channels... ===")
    success, channels = list_channels(base_url, headers)
    
    if not success:
        logger.error("Failed to list channels. Exiting...")
        return False
    
    # Get the list of user IDs from the tenant
    # For now, we'll use the two users you mentioned
    user_ids = [1, 2]  # Replace with actual user IDs if different
    
    # Step 3: Test channel creation with different scenarios
    test_cases = [
        {
            "name": "Direct channel between two users",
            "data": {
                "channel_type": "direct",
                "participants": user_ids,  # Both users in the direct chat
                "name": f"Direct Chat {user_ids[0]}-{user_ids[1]}",
                "host_application_id": 1,
                "context_object_type": "test",
                "context_object_id": 1,
                "is_private": True
            }
        },
        {
            "name": "Group channel with all users",
            "data": {
                "channel_type": "group",
                "participants": user_ids,  # Both users in the group
                "name": "Team Group Chat",
                "description": "A group for team collaboration",
                "host_application_id": 1,
                "context_object_type": "test",
                "context_object_id": 1,
                "is_private": False
            }
        },
        {
            "name": "Private group channel",
            "data": {
                "channel_type": "group",
                "participants": user_ids,
                "name": "Private Team Chat",
                "description": "Private channel for team discussions",
                "host_application_id": 1,
                "context_object_type": "test",
                "context_object_id": 1,
                "is_private": True
            }
        }
    ]
    
    logger.info("\n=== Step 3: Testing channel creation ===")
    for test_case in test_cases:
        logger.info(f"\n{'='*50}")
        logger.info(f"Test Case: {test_case['name']}")
        success, result = test_create_channel(base_url, headers, test_case['data'])
        
        if success:
            logger.info("✅ Test case PASSED")
        else:
            logger.error(f"❌ Test case FAILED: {result}")
    
    return True

if __name__ == "__main__":
    run_tests()
