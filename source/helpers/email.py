import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


# Load environment variables
from dotenv import load_dotenv
load_dotenv()


def send_email(to_email, subject, content):
    sendgrid_api_key = os.getenv('SENDGRID_API_KEY')

    # Create the email object
    message = Mail(
        from_email=os.getenv('SITE_ADMIN_EMAIL'),
        to_emails=to_email,
        subject=subject,
        html_content=content
    )

    try:
        # Create the SendGrid API client
        sg = SendGridAPIClient(sendgrid_api_key)

        # Send the email
        response = sg.send(message)

        # Print response for debugging
        print(f"Status Code: {response.status_code}")
        print(f"Body: {response.body}")
        print(f"Headers: {response.headers}")

    except Exception as e:
        print(f"An error occurred: {e}")


# Example usage
"""
send_email(
    to_email="recipient@example.com",
    subject="Test Email from SendGrid",
    content="<strong>This is a test email sent using SendGrid!</strong>"
)
"""
