# Zaplink

## Description
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