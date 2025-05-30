"""Module for sending email notifications."""
import smtplib
from email.mime.text import MIMEText
import logging

_LOGGER = logging.getLogger(__name__)

def send_shift_summary_email(sender_email, sender_password, recipient_email, subject, body):
    """Sends an email with the shift summary and hours balance."""
    message = MIMEText(body)
    message['Subject'] = subject
    message['From'] = sender_email
    message['To'] = recipient_email

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_email, message.as_string())
        _LOGGER.info("Shift summary email sent successfully")
    except Exception as e:
        _LOGGER.error("Failed to send shift summary email: %s", e)