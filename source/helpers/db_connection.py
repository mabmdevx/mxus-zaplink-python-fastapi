import mysql.connector
from mysql.connector import Error
import logging
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

DATABASE_HOST = os.getenv("DATABASE_HOST")
DATABASE_USER = os.getenv("DATABASE_USER")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")
DATABASE_NAME = os.getenv("DATABASE_NAME")


def create_connection():
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
    db = create_connection()
    try:
        yield db
    finally:
        db.close()
