import os
from dotenv import load_dotenv
import logging
from fastapi.templating import Jinja2Templates

# Load environment variables
load_dotenv()

# Initialize Jinja2 Templates
templates = Jinja2Templates(directory="templates")


def initialize_logging(filename):
    print("init_logging() called - file: " + filename)
    # -- Initialize logging --
    # Default log level if the environment variable is not set
    default_log_level = 'INFO'

    # Get the log level from the environment variable
    env_log_level = os.getenv('LOG_LEVEL', default_log_level).upper()

    # Map the string log level to the logging level
    log_level = getattr(logging, env_log_level, logging.INFO)
    print("LOG_LEVEL: " + env_log_level)

    logging.basicConfig(level=log_level,
                        format='%(asctime)s | %(levelname)s | %(filename)s | %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    logger = logging.getLogger(__name__)
    return logger


# Initialize logging
logger = initialize_logging("common.py")


def error_page(request, error_code, error_message):
    logger.info("error_page() called.")

    # Env
    env_site_name = os.getenv("SITE_NAME")

    return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "SITE_NAME": env_site_name,
                "error_code": error_code,
                "error_message": error_message,
            },
            status_code=error_code
        )
