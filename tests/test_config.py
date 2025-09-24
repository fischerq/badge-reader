import pytest
import json
from unittest.mock import patch, mock_open
from badgereader_addon.badgereader.config import Config
from pathlib import Path


@pytest.fixture
def mock_config_path(tmp_path: Path) -> Path:
    return tmp_path / "options.json"


def test_config_defaults():
    """Test that the Config class initializes with default values when the config file is empty."""
    with patch("builtins.open", mock_open(read_data="{}")):
        config = Config(config_path="/nonexistent/path")
        assert config.notification_domain == "notify"
        assert config.notification_service == "gmail_solalindenstein"
        assert config.notification_emails == []
        assert config.badges == []
        assert config.people == []
        assert config.swipe_debounce_minutes == 1
        assert config.swipe_time_buffer_minutes == 3
        assert config.people_map == {}
        assert config.badge_map == {}
        assert config.badge_to_person_map == {}


def test_config_loading(mock_config_path: Path):
    """Test loading configuration from a JSON file."""
    config_data = {
        "notification_emails": ["test@example.com"],
        "badges": [{"uid": "12345", "peopleID": "p1"}],
        "people": [{"id": "p1", "name": "Test Person"}],
        "swipe_debounce_minutes": 5,
    }
    mock_config_path.write_text(json.dumps(config_data))

    config = Config(config_path=str(mock_config_path))

    assert config.notification_emails == ["test@example.com"]
    assert config.swipe_debounce_minutes == 5
    assert len(config.badges) == 1
    assert len(config.people) == 1
    assert config.people_map == {"p1": {"id": "p1", "name": "Test Person"}}
    assert config.badge_map == {"12345": "p1"}
    assert config.badge_to_person_map == {"12345": {"id": "p1", "name": "Test Person"}}


def test_config_file_not_found():
    """Test handling of a non-existent config file."""
    with patch("logging.error") as mock_log_error:
        Config(config_path="/nonexistent/options.json")
        mock_log_error.assert_called_with(
            "/nonexistent/options.json not found. Please ensure it exists in the add-on's data directory."
        )


def test_config_invalid_json(mock_config_path: Path):
    """Test handling of a malformed JSON config file."""
    mock_config_path.write_text("this is not json")
    with patch("logging.error") as mock_log_error:
        Config(config_path=str(mock_config_path))
        mock_log_error.assert_called_once()
        assert "Error parsing" in mock_log_error.call_args[0][0]
