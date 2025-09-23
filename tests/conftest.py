import pytest
from unittest.mock import MagicMock, AsyncMock
import os

# Make sure the app's modules can be imported
import sys

sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "badgereader_addon")),
)

from badgereader.config import Config


@pytest.fixture
def mock_config():
    """Fixture for a mock Config object."""
    cfg = MagicMock(spec=Config)
    cfg.badge_map = {
        "12345678": "person_a",
        "87654321": "person_b",
    }
    cfg.people_map = {
        "person_a": {"name": "Person A", "email": "person.a@example.com"},
        "person_b": {"name": "Person B", "email": "person.b@example.com"},
    }
    cfg.swipe_debounce_minutes = 1
    cfg.swipe_time_buffer_minutes = 5
    cfg.notification_emails = ["test@example.com"]
    cfg.storage_backend = "file"  # Default to file storage for tests
    cfg.version = "1.0.0"
    cfg.notification_domain = "notify"
    cfg.notification_service = "email_inbox"

    return cfg


@pytest.fixture
def mock_storage(mock_config):
    """Fixture for a mock Storage object."""
    storage = MagicMock()
    storage.read_latest_states.return_value = {}
    return storage


@pytest.fixture
def mock_aiohttp_app():
    """Fixture for a mock aiohttp web application."""
    app = MagicMock()
    app.router.add_post = MagicMock()
    app.router.add_get = MagicMock()
    return app
