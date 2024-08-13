# ZapLink

## Description
- App Info: URL Shortener
- Tech Stack: Python FastAPI, MySQL
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

# Features (apart from Short URL generation)
- Inverse lookup
- Bootstrap template
- Display validation error messages to users
- Protect using CAPTCHA (using Google RECAPTCHA)
- Protect using Safe URL Check API (using Google Safe Browsing API)
- Save URLs as unique hashes in DB
- Logging
- Error handling
- Get email alerts (using SendGrid) for failures
- Get email alerts (using SendGrid) if unsafe url is submitted
- Statcounter

# Notes
## Google RECAPTCHA API
- Generate the API key and add it to .env file

## Google Safe Browsing API
- Generate the API key and add it to .env file
- Restrict the key to just Google Safe Browsing API for security
- https://testsafebrowsing.appspot.com/ = This website has list of urls for testing.

## SendGrid API
- Generate the API key and add it to .env file

## Favicon
- Observed that the browser requests /favicon.ico and that triggers a call to /{slug} route, which should be prevented.
- Hence added a favicon to prevent that.
- Favicon generated using https://cooltext.com PNG and https://favicon.io