# Zaplink

## Description
- URL Shortener
- Built using Python FastAPI
- Creation Start Date: 2024-07-27

## Install dependencies
- pip install fastapi uvicorn jinja2 python-multipart
- pip install python-dotenv mysql-connector-python pydantic shortuuid

## Generate requirements.txt
- pip freeze > requirements.txt

## Running the app in development mode
- fastapi dev main.py
- OR
- uvicorn main:app --reload

Application will start on http://localhost:8000

# Features
- Inverse lookup
- Display validation error messages to users
- Protect using CAPTCHA (using Google RECAPTCHA)
- Protect using Safe URL Check API (using Google Safe Browsing API)
- Save URLs as unique hashes in DB
- Logging standard [PENDING]
- Error handling [PENDING]

# Notes - Google RECAPTCHA API
- Generate the API key and add it to .env file

# Notes - Google Safe Browsing API
- Generate the API key and add it to .env file
- Restrict the key to just Google Safe Browsing API for security
- https://testsafebrowsing.appspot.com/ = This website has list of urls for testing.
