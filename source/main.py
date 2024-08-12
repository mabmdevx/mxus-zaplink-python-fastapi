from fastapi import FastAPI, Form, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import os
from dotenv import load_dotenv
import traceback

# Import helper functions
from source.helpers.common import initialize_logging, error_page, extract_filename_with_relative_path
from source.helpers.db_connection import get_db_connection
from source.helpers.email import send_email
from source.helpers.url import validate_url
from source.helpers.captcha import verify_recaptcha
from source.helpers.app import (get_shortened_url, get_url_by_slug,
                                get_current_domain, update_url_visit_count, extract_slug)

# Load environment variables
load_dotenv()

# Initialize logging
logger = initialize_logging("main.py")

# Initialize FastAPI app
app = FastAPI()

# Initialize Jinja2 Templates
templates = Jinja2Templates(directory="templates")

# Mount static assets path
app.mount("/assets", StaticFiles(directory="assets"), name="assets")

# Env
SITE_NAME = os.getenv("SITE_NAME")
RECAPTCHA_SITE_KEY = os.getenv("RECAPTCHA_SITE_KEY")


# Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.info("global_exception_handler() called.")

    # Extract traceback information
    tb_str = traceback.format_exception(None, exc, exc.__traceback__)

    # Extract function name from the traceback
    exc_occurred_in = "Unknown"
    if len(tb_str) >= 2:
        second_last_line = tb_str[-2]
        exc_occurred_in = second_last_line.strip()

    # Log the traceback for debugging
    # logger.error(tb_str) # Commented out: Not required for now

    # Log the function name and the error
    logger.info(f"global_exception_handler() :: Exception occurred in: {exc_occurred_in}")
    logger.info(f"global_exception_handler() :: Exception details: {str(exc)}")

    # Send an email alert to Site Admin - if an unsafe URL is submitted
    env_site_admin_email = os.getenv('SITE_ADMIN_EMAIL')
    env_site_name = os.getenv('SITE_NAME')

    exc_filename = extract_filename_with_relative_path(exc_occurred_in)

    send_email(
        to_email=env_site_admin_email,
        subject=env_site_name + ": Global exception",
        content="Global exception occurred in: " + exc_filename + ".<br/><br/>Details: " + str(exc)
    )

    return error_page(request, error_code=500, error_message="An unexpected error occurred")


# Routes
# List of predefined static routes
predefined_routes = [
    "/",
    "/get-original-url"
]


# This function prevents /{slug} route being called for existing routes
def check_conflicting_routes(short_url_slug: str):
    # Check if the slug matches any predefined route
    if f"/{short_url_slug}" in predefined_routes:
        raise ValueError(f"The slug '{short_url_slug}' matches an existing route")
    return short_url_slug


# Route - Landing page
@app.get("/", response_class=HTMLResponse)
async def form_short_url(request: Request):
    logger.info("GET Route=/ :: form_short_url() called.")

    return templates.TemplateResponse("landing.html", {
        "request": request,
        "SITE_NAME": SITE_NAME,
        "postback": False,
        "RECAPTCHA_SITE_KEY": RECAPTCHA_SITE_KEY
    })


# Route - Get Shortened URL
@app.post("/", response_class=HTMLResponse)
async def result_short_url(request: Request, original_url: str = Form(...), db=Depends(get_db_connection)):
    logger.info("POST Route=/ :: result_short_url() called.")

    # Get the CAPTCHA response from the form
    form_data = await request.form()
    g_recaptcha_response = form_data.get("g-recaptcha-response")
    logger.debug("result_short_url() :: g_recaptcha_response: " + g_recaptcha_response)

    # Check if CAPTCHA is valid
    if not verify_recaptcha(g_recaptcha_response):
        logger.info("result_short_url() :: CAPTCHA validation failed.")
        return error_page(request, error_code=400, error_message="Invalid reCAPTCHA")
    logger.info("result_short_url() :: CAPTCHA validation successful.")

    # Check if the URL is valid before returning the response
    if validate_url(original_url):
        short_url_slug = get_shortened_url(db, original_url)

        current_domain = get_current_domain(request)

        if short_url_slug == "UNSAFE":
            short_url_val = "UNSAFE"
        else:
            short_url_val = f"{current_domain}/{short_url_slug}"

        return templates.TemplateResponse("landing.html", {
            "request": request,
            "SITE_NAME": SITE_NAME,
            "postback": True,
            "original_url": original_url,
            "short_url": short_url_val
        })
    else:
        error_message = "Invalid URL provided. Please enter a valid URL."
        return templates.TemplateResponse("landing.html", {
            "request": request,
            "SITE_NAME": SITE_NAME,
            "postback": True,
            "error_message": error_message,
            "RECAPTCHA_SITE_KEY": RECAPTCHA_SITE_KEY
        })


# Route - Landing page
@app.get("/get-original-url", response_class=HTMLResponse)
async def form_original_url(request: Request):
    logger.info("GET Route=/get-original-url :: form_original_url() called.")

    return templates.TemplateResponse("get_original_url.html", {
        "request": request,
        "SITE_NAME": SITE_NAME,
        "postback": False,
        "RECAPTCHA_SITE_KEY": RECAPTCHA_SITE_KEY
    })


# Route - Get Original URL from Short URL
@app.post("/get-original-url", response_class=HTMLResponse)
async def result_original_url(request: Request, short_url: str = Form(...), db=Depends(get_db_connection)):
    logger.info("POST Route=/get-original-url :: result_original_url() called.")

    # Get the CAPTCHA response from the form
    form_data = await request.form()
    g_recaptcha_response = form_data.get("g-recaptcha-response")
    logger.debug("result_original_url() :: g_recaptcha_response: " + g_recaptcha_response)

    # Check if CAPTCHA is valid
    if not verify_recaptcha(g_recaptcha_response):
        logger.info("result_original_url() :: CAPTCHA validation failed.")
        return error_page(request, error_code=400, error_message="Invalid reCAPTCHA")
    logger.info("result_original_url() :: CAPTCHA validation successful.")

    # Check if the URL is valid before returning the response
    if validate_url(short_url):
        short_url_slug = extract_slug(short_url)
        original_url = get_url_by_slug(db, short_url_slug)

        current_domain = get_current_domain(request)

        return templates.TemplateResponse("get_original_url.html", {
            "request": request,
            "SITE_NAME": SITE_NAME,
            "postback": True,
            "original_url": original_url,
            "short_url": f"{current_domain}/{short_url_slug}"
        })
    else:
        error_message = "Invalid URL provided. Please enter a valid URL."
        return templates.TemplateResponse("get_original_url.html", {
            "request": request,
            "SITE_NAME": SITE_NAME,
            "postback": True,
            "error_message": error_message,
            "RECAPTCHA_SITE_KEY": RECAPTCHA_SITE_KEY
        })


# Route - Request to the short url
@app.get("/{short_url_slug}", name="redirect", response_class=HTMLResponse)
def request_short_url(request: Request, short_url_slug: str = Depends(check_conflicting_routes),
                      db=Depends(get_db_connection)):
    logger.info("GET Route=/{short_url_slug} :: result_short_url() called.")

    # Get the original url by slug
    original_url_from_db = get_url_by_slug(db, short_url_slug)

    if original_url_from_db is None:
        logger.info("request_short_url() :: Short URL slug not found in database: " + short_url_slug)
        return error_page(request, error_code=404, error_message="URL not found")
    logger.info("request_short_url() :: Short URL slug found in database: " + short_url_slug + ", "
                                                                                               "original_url_from_db: " + original_url_from_db)

    # Update visit count
    update_url_visit_count(db, short_url_slug)

    # Redirect to the original URL
    return RedirectResponse(original_url_from_db)


if __name__ == "__main__":
    import uvicorn

    host = "localhost"
    port = 8000
    logger.info("App running on Host: " + host + " Port: " + str(port))
    uvicorn.run(app, host=host, port=port)
