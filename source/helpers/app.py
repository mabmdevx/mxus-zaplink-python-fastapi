from fastapi import Request
import shortuuid
import logging
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

    # Insert the new URL into the database
    create_url(db, req_original_url, short_url_slug)

    return short_url_slug


def check_short_url_exists(db, short_url: str) -> bool:
    cursor = db.cursor()
    query = "SELECT COUNT(*) FROM urls WHERE urlx_slug = %s"
    cursor.execute(query, (short_url,))
    count = cursor.fetchone()[0]
    cursor.close()
    return count > 0


def create_url(db, req_original_url: str, short_url_slug: str):
    # Insert into database
    cursor = db.cursor()
    query = "INSERT INTO urls (urlx_original_url, urlx_slug) VALUES (%s, %s)"
    cursor.execute(query, (req_original_url, short_url_slug))
    db.commit()
    cursor.close()
    logger.info("Inserted new url in database - slug: " + short_url_slug)


def get_url_by_original_url(db, req_original_url: str):
    cursor = db.cursor(dictionary=True)
    query = "SELECT urlx_id, urlx_slug FROM urls WHERE urlx_original_url = %s LIMIT 1"
    cursor.execute(query, (req_original_url,))
    result = cursor.fetchone()
    cursor.close()
    if result:
        return result.get('urlx_slug')  # Safely get the 'urlx_slug' value
    return None  # Return None if no result is found


def get_url_by_slug(db, req_slug: str):
    cursor = db.cursor(dictionary=True)
    query = "SELECT urlx_id, urlx_original_url FROM urls WHERE urlx_slug = %s"
    cursor.execute(query, (req_slug,))
    result = cursor.fetchone()
    cursor.close()
    if result:
        return result.get('urlx_original_url')  # Safely get the 'urlx_original_url' value
    return None  # Return None if no result is found


def update_url_visit_count(db, req_slug: str):
    cursor = db.cursor()
    query = "UPDATE urls SET urlx_visit_count = urlx_visit_count + 1 WHERE urlx_slug = %s"
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
