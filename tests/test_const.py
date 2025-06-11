"""Tests for the const.py file."""
import pytest

# Import all constants from const.py for testing
from custom_components.badgereader.const import (
    DOMAIN,
    CONF_NFC_UID, # Changed from CONF_CARD_UID
    CONF_READER_IP,
    CONF_GOOGLE_SHEET_ID,
    SERVICE_GENERATE_MONTHLY_REPORT,
)
from custom_components.badgereader.const import (  # pylint: disable=redefined-builtin
    CONF_READER_PORT,
    CONF_READER_USERNAME,
    CONF_READER_PASSWORD,
    CONF_GOOGLE_API_CREDENTIALS,
    CONF_EMAIL_RECIPIENTS,
    CONF_TARGET_WEEKLY_HOURS,
    CONF_USUAL_WORK_DAYS,
    CONF_PDF_OUTPUT_PATH,
    CONF_INITIAL_BALANCE,
    DEFAULT_READER_PORT,
    DEFAULT_USUAL_WORK_DAYS,
    DEFAULT_PDF_OUTPUT_PATH,
    DEFAULT_INITIAL_BALANCE,
    ATTR_HOURS_BALANCE,
    ATTR_LAST_CHECK_IN,
)


def test_constants_exist_and_are_strings():
    """Test that essential constants are defined and are strings."""
    assert isinstance(DOMAIN, str)
    assert DOMAIN == "badgereader"
    assert isinstance(CONF_NFC_UID, str) # Changed from CONF_CARD_UID
    assert isinstance(CONF_READER_IP, str)
    assert isinstance(CONF_GOOGLE_SHEET_ID, str)
    assert isinstance(SERVICE_GENERATE_MONTHLY_REPORT, str)
    assert isinstance(CONF_READER_PORT, str)
    assert isinstance(CONF_READER_USERNAME, str)
    assert isinstance(CONF_READER_PASSWORD, str)
    assert isinstance(CONF_GOOGLE_API_CREDENTIALS, str)
    assert isinstance(CONF_EMAIL_RECIPIENTS, str)
    assert isinstance(CONF_TARGET_WEEKLY_HOURS, str)
    assert isinstance(CONF_USUAL_WORK_DAYS, str)
    assert isinstance(CONF_PDF_OUTPUT_PATH, str)
    assert isinstance(CONF_INITIAL_BALANCE, str)
    assert isinstance(ATTR_HOURS_BALANCE, str)
    assert isinstance(ATTR_LAST_CHECK_IN, str)

def test_configuration_keys_are_lowercase():
    """Test that configuration keys are in lowercase."""
    assert CONF_NFC_UID.islower() # Changed from CONF_CARD_UID
    assert CONF_READER_IP.islower()
    assert CONF_GOOGLE_SHEET_ID.islower()
    assert CONF_READER_PORT.islower()
    assert CONF_READER_USERNAME.islower()
    assert CONF_READER_PASSWORD.islower()
    assert CONF_GOOGLE_API_CREDENTIALS.islower()
    assert CONF_EMAIL_RECIPIENTS.islower()
    assert CONF_TARGET_WEEKLY_HOURS.islower()
    assert CONF_USUAL_WORK_DAYS.islower()
    assert CONF_PDF_OUTPUT_PATH.islower()
    assert CONF_INITIAL_BALANCE.islower()
    assert ATTR_HOURS_BALANCE.islower()
    assert ATTR_LAST_CHECK_IN.islower()


def test_default_values_exist():
    """Test that default values are defined with expected types."""
    assert isinstance(DEFAULT_READER_PORT, int)
    assert DEFAULT_READER_PORT > 0
    assert isinstance(DEFAULT_USUAL_WORK_DAYS, list)
    assert isinstance(DEFAULT_PDF_OUTPUT_PATH, str)
    assert isinstance(DEFAULT_INITIAL_BALANCE, (int, float))

def test_service_name_format():
    """Test the format of the service name."""
    assert "_" in SERVICE_GENERATE_MONTHLY_REPORT
    assert SERVICE_GENERATE_MONTHLY_REPORT.islower()