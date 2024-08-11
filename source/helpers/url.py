import os
from dotenv import load_dotenv
from urllib.parse import urlparse
import requests
import json
import hashlib

# Import helper functions
from source.helpers.common import initialize_logging

# Load environment variables
load_dotenv()

# Initialize logging
logger = initialize_logging("url.py")


def validate_url(url: str) -> bool:
    logger.debug("validate_url() called.")

    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False


def check_is_url_safe(url: str):
    logger.debug("check_is_url_safe() called.")

    api_key = os.getenv('GOOGLE_SAFE_BROWSING_API_KEY')
    if not api_key:
        raise ValueError("Google Safe Browsing API key not set")

    endpoint = "https://safebrowsing.googleapis.com/v4/threatMatches:find"
    payload = {
        "client": {
            "clientId": "yourcompanyname",
            "clientVersion": "1.0"
        },
        "threatInfo": {
            "threatTypes": ["MALWARE", "SOCIAL_ENGINEERING"],
            "platformTypes": ["ANY_PLATFORM"],
            "threatEntryTypes": ["URL"],
            "threatEntries": [
                {"url": url}
            ]
        }
    }
    params = {'key': api_key}
    response = requests.post(endpoint, json=payload, params=params)
    result = response.json()

    if "matches" in result:
        url_safety_check_result = {"is_safe": False, "details": result}
        logger.info("url_safety_check_result: " + json.dumps(url_safety_check_result))
        return url_safety_check_result
    else:
        url_safety_check_result = {"is_safe": True}
        logger.info("url_safety_check_result: " + json.dumps(url_safety_check_result))
        return url_safety_check_result


def generate_url_hash(url):
    logger.debug("generate_url_hash() called.")

    # Encode the URL to bytes, since hash functions require byte input
    url_bytes = url.encode('utf-8')

    # Create a SHA-256 hash object
    sha256_hash = hashlib.sha256()

    # Update the hash object with the URL bytes
    sha256_hash.update(url_bytes)

    # Get the hexadecimal representation of the hash
    hash_hex = sha256_hash.hexdigest()

    return hash_hex
