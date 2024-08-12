import os
from dotenv import load_dotenv
from fastapi import Request
import shortuuid
import json
from urllib.parse import urlparse

# Import helper functions
from source.helpers.common import initialize_logging
from source.helpers.email import send_email
from source.helpers.url import (check_is_url_safe, generate_url_hash)

# Load environment variables
load_dotenv()

# Initialize logging
logger = initialize_logging("app.py")


def get_current_domain(request: Request):
    logger.debug("get_current_domain() called.")

    scheme = request.url.scheme
    host = request.url.hostname
    port = request.url.port
    current_domain = f"{scheme}://{host}" + (f":{port}" if port and port != 80 else "")
    return current_domain


def get_shortened_url(db, req_original_url: str):
    logger.debug("get_shortened_url() called.")

    # Check if the original URL already exists
    existing_slug = get_url_by_original_url(db, req_original_url)
    if existing_slug:
        logger.info("get_shortened_url() :: Original URL: " + req_original_url + " already exists, returning existing "
                                                                              "slug: " + existing_slug)
        return existing_slug  # Return existing slug if it exists

    # Generate a short URL slug and verify it is unique before inserting into database
    short_url_slug = shortuuid.ShortUUID().random(length=8)
    while check_short_url_exists(db, short_url_slug):
        logger.info("get_shortened_url() :: Found existing slug: " + short_url_slug + ", generating new slug.")
        short_url_slug = shortuuid.ShortUUID().random(length=8)

    # Check if URL is safe or not
    url_is_safe_result = check_is_url_safe(req_original_url)

    url_is_safe = url_is_safe_result["is_safe"]
    url_is_safe_details_str = json.dumps(url_is_safe_result)

    # Insert the new URL into the database
    create_url(db, req_original_url, short_url_slug, url_is_safe, url_is_safe_details_str)

    if url_is_safe:
        logger.info(f"get_shortened_url() :: short_url_slug: {{ short_url_slug }}.")
        return short_url_slug
    else:
        logger.info("get_shortened_url() :: Unsafe URL has been submitted.")

        # Send an email alert to Site Admin - if an unsafe URL is submitted
        env_site_admin_email = os.getenv('SITE_ADMIN_EMAIL')
        env_site_name = os.getenv('SITE_NAME')

        send_email(
            to_email=env_site_admin_email,
            subject=env_site_name + ": Unsafe URL submitted",
            content="Unsafe URL Submitted.<br/><br/>URL Slug: " + short_url_slug
        )

        return "UNSAFE"


def check_short_url_exists(db, short_url: str) -> bool:
    logger.debug("check_short_url_exists() called.")

    cursor = db.cursor()
    query = "SELECT COUNT(*) FROM urls WHERE urlx_is_safe = true AND urlx_slug = %s"
    cursor.execute(query, (short_url,))
    count = cursor.fetchone()[0]
    cursor.close()
    return count > 0


def create_url(db, req_original_url: str, short_url_slug: str, url_is_safe: bool, unsafe_details: str):
    logger.debug("create_url() called.")

    # Generate the hash for the original url
    original_url_hash = generate_url_hash(req_original_url)

    # Insert into database
    cursor = db.cursor()
    query = ("INSERT INTO urls (urlx_original_url, urlx_hash, urlx_slug, urlx_is_safe, urlx_unsafe_details) VALUES ("
             "%s, %s, %s, %s, %s)")
    cursor.execute(query, (req_original_url, original_url_hash, short_url_slug, url_is_safe, unsafe_details))
    db.commit()
    cursor.close()
    logger.info("Inserted new url in database - slug: " + short_url_slug)


def get_url_by_original_url(db, req_original_url: str):
    logger.debug("get_url_by_original_url() called.")

    # Generate the hash for the original url
    original_url_hash = generate_url_hash(req_original_url)

    cursor = db.cursor(dictionary=True)
    query = "SELECT urlx_id, urlx_slug FROM urls WHERE urlx_is_safe = true AND urlx_hash = %s LIMIT 1"
    cursor.execute(query, (original_url_hash,))
    result = cursor.fetchone()
    cursor.close()
    if result:
        return result.get('urlx_slug')  # Safely get the 'urlx_slug' value
    return None  # Return None if no result is found


def get_url_by_slug(db, req_slug: str):
    logger.debug("get_url_by_slug() called.")

    cursor = db.cursor(dictionary=True)
    query = "SELECT urlx_id, urlx_original_url FROM urls WHERE urlx_is_safe = true AND urlx_slug = %s"
    cursor.execute(query, (req_slug,))
    result = cursor.fetchone()
    cursor.close()
    if result:
        return result.get('urlx_original_url')  # Safely get the 'urlx_original_url' value
    return None  # Return None if no result is found


def update_url_visit_count(db, req_slug: str):
    logger.debug("update_url_visit_count() called.")

    cursor = db.cursor()
    query = "UPDATE urls SET urlx_visit_count = urlx_visit_count + 1 WHERE urlx_is_safe = true AND urlx_slug = %s"
    cursor.execute(query, (req_slug,))
    db.commit()
    cursor.close()


def extract_slug(full_short_url: str) -> str:
    logger.debug("extract_slug() called.")

    parsed_url = urlparse(full_short_url)
    slug = parsed_url.path.strip('/')  # Remove leading and trailing slashes
    return slug



