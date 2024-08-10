from urllib.parse import urlparse
import os
import requests
import json
import logging
import hashlib


# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def validate_url(url: str) -> bool:
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False


def check_is_url_safe(url: str):
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
    # Encode the URL to bytes, since hash functions require byte input
    url_bytes = url.encode('utf-8')

    # Create a SHA-256 hash object
    sha256_hash = hashlib.sha256()

    # Update the hash object with the URL bytes
    sha256_hash.update(url_bytes)

    # Get the hexadecimal representation of the hash
    hash_hex = sha256_hash.hexdigest()

    return hash_hex
