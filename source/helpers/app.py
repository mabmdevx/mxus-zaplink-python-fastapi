from fastapi import Request
import shortuuid
import logging
import requests
import os
import json
from urllib.parse import urlparse
from dotenv import load_dotenv
load_dotenv()


# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_current_domain(request: Request):
    scheme = request.url.scheme
    host = request.url.hostname
    port = request.url.port
    current_domain = f"{scheme}://{host}" + (f":{port}" if port and port != 80 else "")
    return current_domain


def get_shortened_url(db, req_original_url: str):
    # Check if the original URL already exists
    existing_slug = get_url_by_original_url(db, req_original_url)
    if existing_slug:
        logger.info("Original URL: " + req_original_url + " already exists, returning existing slug: " + existing_slug)
        return existing_slug  # Return existing slug if it exists

    # Generate a short URL slug and verify it is unique before inserting into database
    short_url_slug = shortuuid.ShortUUID().random(length=8)
    while check_short_url_exists(db, short_url_slug):
        logger.info("Found existing slug: " + short_url_slug + ", generating new slug.")
        short_url_slug = shortuuid.ShortUUID().random(length=8)

    # Check if URL is safe or not
    url_is_safe_result = check_is_url_safe(req_original_url)

    url_is_safe = url_is_safe_result["is_safe"]
    url_is_safe_details_str = json.dumps(url_is_safe_result)

    # Insert the new URL into the database
    create_url(db, req_original_url, short_url_slug, url_is_safe, url_is_safe_details_str)

    if url_is_safe:
        return short_url_slug
    else:
        return "UNSAFE"


def check_short_url_exists(db, short_url: str) -> bool:
    cursor = db.cursor()
    query = "SELECT COUNT(*) FROM urls WHERE urlx_is_safe = true AND urlx_slug = %s"
    cursor.execute(query, (short_url,))
    count = cursor.fetchone()[0]
    cursor.close()
    return count > 0


def create_url(db, req_original_url: str, short_url_slug: str, url_is_safe: bool, unsafe_details: str):
    # Insert into database
    cursor = db.cursor()
    query = "INSERT INTO urls (urlx_original_url, urlx_slug, urlx_is_safe, urlx_unsafe_details) VALUES (%s, %s, %s, %s)"
    cursor.execute(query, (req_original_url, short_url_slug, url_is_safe, unsafe_details))
    db.commit()
    cursor.close()
    logger.info("Inserted new url in database - slug: " + short_url_slug)


def get_url_by_original_url(db, req_original_url: str):
    cursor = db.cursor(dictionary=True)
    query = "SELECT urlx_id, urlx_slug FROM urls WHERE urlx_is_safe = true AND urlx_original_url = %s LIMIT 1"
    cursor.execute(query, (req_original_url,))
    result = cursor.fetchone()
    cursor.close()
    if result:
        return result.get('urlx_slug')  # Safely get the 'urlx_slug' value
    return None  # Return None if no result is found


def get_url_by_slug(db, req_slug: str):
    cursor = db.cursor(dictionary=True)
    query = "SELECT urlx_id, urlx_original_url FROM urls WHERE urlx_is_safe = true AND urlx_slug = %s"
    cursor.execute(query, (req_slug,))
    result = cursor.fetchone()
    cursor.close()
    if result:
        return result.get('urlx_original_url')  # Safely get the 'urlx_original_url' value
    return None  # Return None if no result is found


def update_url_visit_count(db, req_slug: str):
    cursor = db.cursor()
    query = "UPDATE urls SET urlx_visit_count = urlx_visit_count + 1 WHERE urlx_is_safe = true AND urlx_slug = %s"
    cursor.execute(query, (req_slug,))
    db.commit()
    cursor.close()


def extract_slug(full_short_url: str) -> str:
    parsed_url = urlparse(full_short_url)
    slug = parsed_url.path.strip('/')  # Remove leading and trailing slashes
    return slug


def validate_url(url: str) -> bool:
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False


def get_recaptcha_secret_key():
    # Load your CAPTCHA secret key from an environment variable or configuration file
    recaptcha_secret_key = os.getenv('RECAPTCHA_SECRET_KEY')
    if not recaptcha_secret_key:
        raise ValueError("reCAPTCHA secret key not set")
    return recaptcha_secret_key


def verify_recaptcha(token: str):
    recaptcha_secret_key = get_recaptcha_secret_key()
    payload = {
        'secret': recaptcha_secret_key,
        'response': token
    }
    response = requests.post("https://www.google.com/recaptcha/api/siteverify", data=payload)
    result = response.json()
    return result.get("success", False)


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




