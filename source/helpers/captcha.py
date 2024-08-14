import os
from dotenv import load_dotenv
import requests

# Import helper functions
from helpers.common import initialize_logging

# Load environment variables
load_dotenv()

# Initialize logging
logger = initialize_logging("captcha.py")


def get_recaptcha_secret_key():
    logger.debug("get_recaptcha_secret_key() called.")

    # Load your CAPTCHA secret key from an environment variable or configuration file
    recaptcha_secret_key = os.getenv('RECAPTCHA_SECRET_KEY')
    if not recaptcha_secret_key:
        raise ValueError("reCAPTCHA secret key not set")
    return recaptcha_secret_key


def verify_recaptcha(token: str):
    logger.debug("verify_recaptcha() called.")

    recaptcha_secret_key = get_recaptcha_secret_key()
    payload = {
        'secret': recaptcha_secret_key,
        'response': token
    }
    response = requests.post("https://www.google.com/recaptcha/api/siteverify", data=payload)
    result = response.json()
    return result.get("success", False)
