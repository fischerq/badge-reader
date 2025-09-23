import pytest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock

# Since homeassistant_api is not a real package, we need to mock it before importing the notification module.
import sys

mock_homeassistant_api = MagicMock()
sys.modules["homeassistant_api"] = mock_homeassistant_api

from badgereader.notification import (
    _send_notification,
    send_shift_start_notification,
    send_shift_end_notification,
    send_unrecognized_card_notification,
)


@pytest.fixture
def mock_config():
    config = MagicMock()
    config.notification_domain = "test_domain"
    config.notification_service = "test_service"
    config.notification_emails = ["admin@example.com", "user@example.com"]
    return config


@patch("badgereader.notification.Client")
def test_send_notification_success(mock_client_constructor, mock_config):
    """Test that _send_notification successfully sends a notification."""

    async def run_test():
        ha_url = "http://ha.test"
        ha_token = "test_token"
        title = "Test Title"
        message = "Test Message"
        person = {"name": "Test User", "email": "user@example.com"}

        # Configure the mock
        mock_client = AsyncMock()
        mock_context_manager = AsyncMock()
        mock_context_manager.__aenter__.return_value = mock_client
        mock_client_constructor.return_value = mock_context_manager

        with patch("logging.info") as mock_log_info:
            await _send_notification(
                mock_config, ha_url, ha_token, title, message, person
            )

            mock_client.async_trigger_service.assert_awaited_once_with(
                mock_config.notification_domain,
                mock_config.notification_service,
                title=title,
                message=message,
                target=["user@example.com"],
                data={"cc": ["admin@example.com"]},
            )
            mock_log_info.assert_any_call(
                f"Successfully sent notification with title: '{title}' to ['user@example.com']"
            )

    asyncio.run(run_test())


def test_send_notification_no_token(mock_config):
    """Test that a warning is logged when no HA token is provided."""

    async def run_test():
        with patch("logging.warning") as mock_log_warning:
            await _send_notification(
                mock_config, "http://ha.test", None, "title", "message"
            )
            mock_log_warning.assert_called_with(
                "SUPERVISOR_TOKEN not found, cannot send notification."
            )

    asyncio.run(run_test())


def test_send_notification_no_recipients():
    """Test that a warning is logged when there are no recipients."""

    async def run_test():
        mock_config = MagicMock()
        mock_config.notification_emails = []
        with patch("logging.warning") as mock_log_warning:
            await _send_notification(
                mock_config, "http://ha.test", "token", "title", "message"
            )
            mock_log_warning.assert_called_with("No recipients found for notification.")

    asyncio.run(run_test())


@patch("badgereader.notification._send_notification", new_callable=AsyncMock)
def test_send_shift_start_notification(mock_send, mock_config):
    """Test the content of the shift start notification."""

    async def run_test():
        person = {"name": "Test User"}
        await send_shift_start_notification(mock_config, "url", "token", person)
        mock_send.assert_awaited_once_with(
            mock_config,
            "url",
            "token",
            f"{person['name']} - Schicht gestartet",
            f"Hallo {person['name']}, deine Schicht hat gerade begonnen. Einen schönen und produktiven Tag!",
            person,
        )

    asyncio.run(run_test())


@patch("badgereader.notification._send_notification", new_callable=AsyncMock)
def test_send_shift_end_notification(mock_send, mock_config):
    """Test the content of the shift end notification."""

    async def run_test():
        person = {"name": "Test User"}
        duration = "8 hours"
        await send_shift_end_notification(mock_config, "url", "token", person, duration)
        mock_send.assert_awaited_once_with(
            mock_config,
            "url",
            "token",
            f"{person['name']} - Schicht beendet",
            f"Hallo {person['name']}, deine Schicht ist nun zu Ende. Deine heutige Arbeitszeit betrug {duration}. Wir wünschen dir einen schönen Feierabend!",
            person,
        )

    asyncio.run(run_test())


@patch("badgereader.notification._send_notification", new_callable=AsyncMock)
def test_send_unrecognized_card_notification(mock_send, mock_config):
    """Test the content of the unrecognized card notification."""

    async def run_test():
        uid = "unknown_uid"
        await send_unrecognized_card_notification(mock_config, "url", "token", uid)
        mock_send.assert_awaited_once_with(
            mock_config,
            "url",
            "token",
            "Unbekannter Badge gescannt",
            f"Hallo, gerade wurde ein unbekannter Badge mit der UID {uid} gescannt.",
        )

    asyncio.run(run_test())
