import pytest
from unittest.mock import patch, MagicMock

from custom_components.badgereader.email import send_shift_summary_email

@patch("custom_components.badgereader.email.smtplib.SMTP_SSL") # Changed to SMTP_SSL
def test_send_shift_summary_email(mock_smtp_ssl): # Changed mock name
    """Test the send_shift_summary_email function."""
    mock_server = MagicMock()
    mock_smtp_ssl.return_value.__enter__.return_value = mock_server # Corrected variable name

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
    subject = f"Housekeeper Shift Summary - {shift_summary.get('date', 'N/A')}"
    body = f"""
Shift Summary for {shift_summary.get('date', 'N/A')}:
Check-in: {shift_summary.get('check_in', 'N/A')}
Check-out: {shift_summary.get('check_out', 'N/A')}
Duration: {shift_summary.get('duration', 'N/A')} hours
Current Hours Balance: {shift_summary.get('hours_balance', 'N/A')}
"""

    # The email function expects a single recipient string, not a list for this version
    for recipient_email in recipient_emails:
        send_shift_summary_email(sender_email, sender_password, recipient_email, subject, body)

    assert mock_smtp_ssl.call_count == len(recipient_emails) # Called for each recipient
    mock_smtp_ssl.assert_called_with("smtp.gmail.com", 465) # Check last call or any call if appropriate, port for SSL
    # mock_server.starttls.assert_called_once() # SMTP_SSL does not use starttls
    assert mock_server.login.call_count == len(recipient_emails)
    mock_server.login.assert_called_with(sender_email, sender_password) # Checks the arguments of the calls

    expected_subject = "Housekeeper Shift Summary - 2023-10-27"
    expected_body = """
Shift Summary for 2023-10-27:
Check-in: 08:00
Check-out: 16:00
Duration: 8.00 hours
Current Hours Balance: +5.00
"""
    assert mock_server.sendmail.call_count == len(recipient_emails)
    # To check arguments of each call, you might need to inspect mock_server.sendmail.call_args_list
    # For now, checking the count is the main fix for the specific error.
    # If we need to check arguments for each, the test would be more complex.
    # We can check the last call's arguments as a sample:
    call_args, _ = mock_server.sendmail.call_args
    sent_from, sent_to_last_call, sent_message = call_args # Renamed for clarity

    assert sent_from == sender_email
    # Check if the last recipient it was sent to is part of the original list.
    # And that sent_to_last_call is indeed the last one in the loop context.
    assert sent_to_last_call == recipient_email # recipient_email is the last one from the loop
    assert expected_subject in sent_message
    assert expected_body.strip() in sent_message

@patch("custom_components.badgereader.email.smtplib.SMTP_SSL") # Changed to SMTP_SSL
def test_send_shift_summary_email_failure(mock_smtp_ssl): # Changed mock name
    """Test send_shift_summary_email handles exceptions."""
    mock_server = MagicMock()
    mock_smtp_ssl.return_value.__enter__.return_value = mock_server
    mock_server.login.side_effect = Exception("Login Failed")

    sender_email = "sender@example.com"
    sender_password = "wrong_password"
    recipient_emails = ["recipient@example.com"] # Corrected to be a list as per original test
    shift_summary = {}
    subject = "Test Subject (Failure)"
    body = "Test Body (Failure)"


    with pytest.raises(Exception, match="Login Failed"):
        # The email function expects a single recipient string
        send_shift_summary_email(sender_email, sender_password, recipient_emails[0], subject, body)

    mock_server.login.assert_called_once_with(sender_email, sender_password)
    mock_server.sendmail.assert_not_called()