import os
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import Error
import logging

# Import helper functions
from source.helpers.common import initialize_logging

# Load environment variables from .env file
load_dotenv()

# Initialize logging
logger = initialize_logging("db_connection.py")

# Load database info from ENV
DATABASE_HOST = os.getenv("DATABASE_HOST")
DATABASE_USER = os.getenv("DATABASE_USER")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")
DATABASE_NAME = os.getenv("DATABASE_NAME")


def create_connection():
    logger.debug("create_connection() called.")

    connection = None
    try:
        connection = mysql.connector.connect(
            host=DATABASE_HOST,
            user=DATABASE_USER,
            passwd=DATABASE_PASSWORD,
            database=DATABASE_NAME
        )
        logging.info("Successfully connected to the database")
    except Error as e:
        logging.error(f"The error '{e}' occurred")
    return connection


def get_db_connection():
    logger.debug("get_db_connection() called.")

    db = create_connection()
    try:
        yield db
    finally:
        db.close()
