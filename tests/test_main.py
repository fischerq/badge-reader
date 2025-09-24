import pytest
import asyncio
from unittest.mock import MagicMock, AsyncMock, patch
from datetime import datetime
import sys


# --- Mock Exceptions ---
class MockHTTPException(BaseException):
    def __init__(self, *args, **kwargs):
        self.kwargs = kwargs
        super().__init__(*args)


class MockHTTPUnauthorized(MockHTTPException):
    pass


class MockHTTPBadRequest(MockHTTPException):
    pass


# Mock external dependencies before they are imported by other modules
mock_aiohttp = MagicMock()
mock_aiohttp.web.HTTPException = MockHTTPException
mock_aiohttp.web.HTTPUnauthorized = MockHTTPUnauthorized
mock_aiohttp.web.HTTPBadRequest = MockHTTPBadRequest
mock_aiohttp.web.Response = MagicMock()
sys.modules["aiohttp"] = mock_aiohttp
sys.modules["aiohttp.web"] = mock_aiohttp.web

sys.modules["gspread"] = MagicMock()
sys.modules["openpyxl"] = MagicMock()
mock_oauth2client = MagicMock()
sys.modules["oauth2client"] = mock_oauth2client
sys.modules["oauth2client.service_account"] = mock_oauth2client.service_account
sys.modules["homeassistant_api"] = MagicMock()
sys.modules["libnfs"] = MagicMock()

from badgereader.main import handle_post, handle_get


def test_handle_post_success():
    async def run_test():
        badge_uid = "12345678"
        person_id = "person_a"
        person_name = "Person A"

        mock_request = AsyncMock()
        post_data = MagicMock()
        post_data.get.side_effect = lambda key, default=None: {
            "UID": badge_uid,
            "accessKey": "SolalindensteinBadgeReaderSecret",
        }.get(key, default)
        mock_request.post = AsyncMock(return_value=post_data)
        mock_request.query = {}
        mock_request.remote = "127.0.0.1"

        # Configure the mock response
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.text = f"Welcome, {person_name}. Your shift has started."
        mock_aiohttp.web.Response.return_value = mock_response

        with patch("badgereader.main.config") as mock_config, patch(
            "badgereader.main.state_manager"
        ) as mock_state_manager, patch(
            "badgereader.main.storage"
        ) as mock_storage, patch(
            "badgereader.main.send_shift_start_notification", new_callable=AsyncMock
        ) as mock_send_notification:

            mock_config.badge_map = {badge_uid.strip().lower(): person_id}
            mock_config.people_map = {person_id: {"name": person_name}}
            mock_state_manager.is_swipe_debounced.return_value = False
            mock_state_manager.handle_swipe.return_value = (
                "in",
                {"new_state": "in"},
                "8 hours",
            )
            with patch(
                "badgereader.main.ACCESS_KEY", "SolalindensteinBadgeReaderSecret"
            ):
                response = await handle_post(mock_request)

            mock_state_manager.handle_swipe.assert_called_once()
            mock_storage.log_swipe.assert_called_once()
            mock_send_notification.assert_called_once()
            assert response.status == 200
            assert f"Welcome, {person_name}" in response.text

    asyncio.run(run_test())


def test_handle_unauthorized_post():
    async def run_test():
        mock_request = AsyncMock()
        post_data = MagicMock()
        post_data.get.return_value = "wrong_key"
        mock_request.post = AsyncMock(return_value=post_data)
        mock_request.query = {}

        with patch("badgereader.main.ACCESS_KEY", "SolalindensteinBadgeReaderSecret"):
            with pytest.raises(MockHTTPUnauthorized):
                await handle_post(mock_request)

    asyncio.run(run_test())


def test_handle_get_request():
    async def run_test():
        mock_request = AsyncMock()
        mock_request.path = "/"
        mock_request.remote = "127.0.0.1"

        # Configure the mock response
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.text = "Badge Reader Addon HTTP Server"
        mock_response.content_type = "text/html"
        mock_aiohttp.web.Response.return_value = mock_response

        response = await handle_get(mock_request)
        assert response.status == 200
        assert "Badge Reader Addon HTTP Server" in response.text
        assert response.content_type == "text/html"

    asyncio.run(run_test())
