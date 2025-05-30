import pytest
from unittest.mock import patch, MagicMock

from custom_components.badgereader.email import send_shift_summary_email

@patch("custom_components.badgereader.email.smtplib.SMTP")
def test_send_shift_summary_email(mock_smtp):
    """Test the send_shift_summary_email function."""
    mock_server = MagicMock()
    mock_smtp.return_value.__enter__.return_value = mock_server

    sender_email = "sender@example.com"
    sender_password = "password"
    recipient_emails = ["recipient1@example.com", "recipient2@example.com"]
    shift_summary = {
        "date": "2023-10-27",
        "check_in": "08:00",
        "check_out": "16:00",
        "duration": "8.00",
        "hours_balance": "+5.00",
    }

    send_shift_summary_email(sender_email, sender_password, recipient_emails, shift_summary)

    mock_smtp.assert_called_once_with("smtp.gmail.com", 587)
    mock_server.starttls.assert_called_once()
    mock_server.login.assert_called_once_with(sender_email, sender_password)

    expected_subject = "Housekeeper Shift Summary - 2023-10-27"
    expected_body = """
Shift Summary for 2023-10-27:
Check-in: 08:00
Check-out: 16:00
Duration: 8.00 hours
Current Hours Balance: +5.00
"""
    mock_server.sendmail.assert_called_once()
    call_args, _ = mock_server.sendmail.call_args
    sent_from, sent_to, sent_message = call_args

    assert sent_from == sender_email
    assert sent_to == recipient_emails
    assert expected_subject in sent_message
    assert expected_body.strip() in sent_message

@patch("custom_components.badgereader.email.smtplib.SMTP")
def test_send_shift_summary_email_failure(mock_smtp):
    """Test send_shift_summary_email handles exceptions."""
    mock_server = MagicMock()
    mock_smtp.return_value.__enter__.return_value = mock_server
    mock_server.login.side_effect = Exception("Login Failed")

    sender_email = "sender@example.com"
    sender_password = "wrong_password"
    recipient_emails = ["recipient@example.com"]
    shift_summary = {}

    with pytest.raises(Exception, match="Login Failed"):
        send_shift_summary_email(sender_email, sender_password, recipient_emails, shift_summary)

    mock_server.login.assert_called_once_with(sender_email, sender_password)
    mock_server.sendmail.assert_not_called()