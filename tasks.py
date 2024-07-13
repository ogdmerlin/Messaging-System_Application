import os
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from celery import Celery
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

EMAIL = os.getenv('EMAIL')
PASSWORD = os.getenv('PASSWORD')
SMTP_SERVER = os.getenv('SMTP_SERVER')
SMTP_PORT = int(os.getenv('SMTP_PORT'))

# Initialize Celery
celery = Celery('tasks', broker='amqp://ogdmerlin:dyusuf1@3.92.133.203:5672//', backend='rpc://3.92.133.203')

# Update Celery configuration
celery.conf.update(
    result_expires=60,  # Task results will expire 1 minute after being stored
)


# Create logs directory if it doesn't exist
log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, 'messaging_system.log')

# Configure logging
logging.basicConfig(
    filename=log_file,
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.DEBUG
)

@celery.task
def send_email(to_email):
    try:
        # Set up SMTP server connection
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()  # Upgrade connection to secure
        print(f"EMAIL: {EMAIL}, PASSWORD: {PASSWORD}")
        server.login(EMAIL, PASSWORD)  # Log in to the SMTP server


        # Create email message
        msg = MIMEMultipart()
        msg['From'] = EMAIL
        msg['To'] = to_email
        msg['Subject'] = "Test Email"
        body = "This is a test email sent from my messaging system application."
        msg.attach(MIMEText(body, 'plain'))

        # Send email and close server connection
        server.sendmail(EMAIL, to_email, msg.as_string())
        server.quit()

        # Log success
        logging.info(f'Email sent to {to_email}')
        return f'Email sent to {to_email}'
    except Exception as e:
        # Log any exceptions during email send process
        logging.error(f'Failed to send email to {to_email}: {e}')
        raise

@celery.task
def log_time():
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        with open(log_file, 'a') as f:
            f.write(f"Current time: {current_time}\n")
        logging.info(f'Time logged: {current_time}')
        return current_time
    except Exception as e:
        logging.error(f'Failed to log time: {e}')
        raise
