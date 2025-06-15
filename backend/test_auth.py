import requests
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def test_auth():
    """Test authentication and get JWT token"""
    auth_url = 'http://localhost:8014/api/bingo_travels/auth/login/'
    
    try:
        logger.info("Attempting to authenticate...")
        response = requests.post(
            auth_url,
            json={"email": "yash@turtlesoftware.co", "password": "India@123"},
            timeout=10,
            verify=False
        )
        
        logger.info(f"Status Code: {response.status_code}")
        logger.info(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            logger.info("Authentication successful!")
            logger.info(f"Access Token: {data.get('tokens', {}).get('access')}")
            return True
        else:
            logger.error(f"Authentication failed: {response.status_code}")
            return False
            
    except Exception as e:
        logger.exception("Error during authentication:")
        return False

if __name__ == "__main__":
    test_auth()
