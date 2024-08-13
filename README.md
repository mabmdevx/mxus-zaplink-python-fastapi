# ZapLink

## Description
- App Info: URL Shortener
- Tech Stack: Python FastAPI, MySQL
- Creation Start Date: 2024-07-27

## Dev Environment Setup
### Install dependencies
```
pip install fastapi uvicorn jinja2 python-multipart
pip install python-dotenv mysql-connector-python pydantic shortuuid
```

### Generate requirements.txt
```
pip freeze > requirements.txt
```

### Running the app in development mode
```
fastapi dev main.py
```
OR
```
uvicorn main:app --reload
```

Application will start on http://localhost:8000

## Features 
(apart from Short URL generation)
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

## Notes
### Google RECAPTCHA API
- Generate the API key and add it to .env file

### Google Safe Browsing API
- Generate the API key and add it to .env file
- Restrict the key to just Google Safe Browsing API for security
- https://testsafebrowsing.appspot.com/ = This website has list of urls for testing.

### SendGrid API
- Generate the API key and add it to .env file

### Favicon
- Observed that the browser requests /favicon.ico and that triggers a call to /{slug} route, which should be prevented.
- Hence added a favicon to prevent that.
- Favicon generated using https://cooltext.com PNG and https://favicon.io

## Production Setup
### 1) Setup your server with the required packages
### First update and upgrade your server
```commandline
sudo apt update && sudo apt upgrade -y
```
### Install required packages
```
sudo apt install python3-pip python3-venv nginx -y
```

### Setup a virtual environment
```
python3 -m venv venv
source venv/bin/activate
```

### Install python dependencies
```
pip install fastapi uvicorn[standard]
pip install jinja2 python-multipart
pip install python-dotenv mysql-connector-python pydantic shortuuid
```

### 2) Setup Gunicorn as production server
Note: FastAPI’s built-in Uvicorn server is great for development but not recommended for production. 
Use Gunicorn with Uvicorn workers.
### Install Gunicorn
```
pip install gunicorn
```

### Create a Gunicorn Configuration
Create the Gunicorn config file: gunicorn_config.py
```
bind = "0.0.0.0:8001"
workers = 4
worker_class = "uvicorn.workers.UvicornWorker"
```

### Start Gunicorn
```
gunicorn -c gunicorn_config.py main:app
```

### 3) Set Up Nginx as a Reverse Proxy
### Install Nginx
```
sudo apt install nginx
```

### Configure Nginx
Create a configuration file for your site:
e.g., /etc/nginx/sites-available/zaplink_python_fastapi:
```
server {
    listen 80;
    server_name your-domain.com;  # Replace with your domain

    location / {
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Enable the NGINX configuration
```commandline
sudo ln -s /etc/nginx/sites-available/zaplink_python_fastapi /etc/nginx/sites-enabled
sudo nginx -t
sudo systemctl restart nginx
```

### 4) Set Up SSL with Let's Encrypt
### Install Certbot
```commandline
sudo apt install certbot python3-certbot-nginx -y
```

### Obtain and Install the SSL Certificate
```commandline
sudo certbot --nginx -d your-domain.com
```

### Auto-Renew SSL Certificates:
Certbot automatically sets up a cron job for renewal. You can check it with
```commandline
sudo systemctl status certbot.timer
```

### 5) Set Up Process Management with Systemd
Create a Systemd Service File:
Create /etc/systemd/system/zaplink_python_fastapi.service:
```commandline
[Unit]
Description=Gunicorn instance to serve Zaplink Python FastAPI
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/your/app
ExecStart=/path/to/your/venv/bin/gunicorn -c /path/to/your/gunicorn_config.py main:app

[Install]
WantedBy=multi-user.target
```

### Start and Enable the Service:
```commandline
sudo systemctl start zaplink_python_fastapi
sudo systemctl enable zaplink_python_fastapi
```
