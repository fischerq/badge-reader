import pytest
import os
import json
from unittest.mock import MagicMock, patch
import sys

# Mock gspread, openpyxl, and oauth2client before they are imported by the storage module
sys.modules["gspread"] = MagicMock()
sys.modules["openpyxl"] = MagicMock()
mock_oauth2client = MagicMock()
sys.modules["oauth2client"] = mock_oauth2client
sys.modules["oauth2client.service_account"] = mock_oauth2client.service_account

from badgereader.storage import FileStorage


@pytest.fixture
def mock_config(tmp_path):
    """Fixture to create a mock config object."""
    config = MagicMock()
    config.storage_file_path = str(tmp_path / "test_log.jsonl")
    config.storage_sheets_dir = str(tmp_path)
    config.badge_map = {"badge1": "person1", "badge2": "person2", "badge3": "person3"}
    config.people_map = {"person1": {"name": "Person 1"}}
    return config


@pytest.fixture
def file_storage(mock_config):
    """Fixture for a FileStorage instance using a mock config."""
    with patch("logging.info"), patch("logging.error"), patch("logging.warning"):
        storage = FileStorage(config=mock_config)
        yield storage


def test_file_storage_init(file_storage, mock_config):
    """Test the initialization of the FileStorage class."""
    assert file_storage.file_path == mock_config.storage_file_path


def test_log_swipe(file_storage, mock_config):
    """Test that log_swipe correctly writes a log entry to the file."""
    timestamp = "2024-01-01T12:00:00"
    badge_id = "test_badge"
    action = {"action": "test"}
    action_json = json.dumps(action)

    file_storage.log_swipe(timestamp, badge_id, action_json)

    with open(mock_config.storage_file_path, "r") as f:
        log_entry = json.loads(f.readline())
        assert log_entry["timestamp"] == timestamp
        assert log_entry["badge_id"] == badge_id
        assert log_entry["action"] == action


def test_read_latest_states_no_file(tmp_path):
    """Test read_latest_states when the log file does not exist."""
    mock_config = MagicMock()
    mock_config.storage_file_path = str(tmp_path / "non_existent.jsonl")
    storage = FileStorage(config=mock_config)
    states = storage.read_latest_states()
    assert states == {}


def test_read_latest_states(file_storage, mock_config):
    """Test read_latest_states to correctly read the last known state."""
    # Log a few swipes
    file_storage.log_swipe(
        "2024-01-01T12:00:00", "badge1", json.dumps({"new_state": "in"})
    )
    file_storage.log_swipe(
        "2024-01-01T12:05:00", "badge2", json.dumps({"new_state": "in"})
    )
    file_storage.log_swipe(
        "2024-01-01T12:10:00", "badge1", json.dumps({"new_state": "out"})
    )
    file_storage.log_swipe(
        "2024-01-01T12:15:00", "badge3", json.dumps({"new_state": "in"})
    )
    file_storage.log_swipe(
        "2024-01-01T12:20:00", "badge2", json.dumps({"new_state": "out"})
    )
    file_storage.log_swipe(
        "2024-01-01T12:25:00", "badge1", json.dumps({"new_state": "in"})
    )

    latest_states = file_storage.read_latest_states()

    expected_states = {
        "badge1": {"state": "in", "timestamp": "2024-01-01T12:25:00"},
        "badge2": {"state": "out", "timestamp": "2024-01-01T12:20:00"},
        "badge3": {"state": "in", "timestamp": "2024-01-01T12:15:00"},
    }
    assert latest_states == expected_states


def test_check_success(file_storage):
    """Test that the check method succeeds when the file is accessible."""
    with patch("logging.info") as mock_log_info:
        file_storage.check()
        mock_log_info.assert_any_call(
            f"Checking file storage access at {file_storage.file_path}..."
        )
        mock_log_info.assert_any_call("File storage is accessible.")


def test_check_failure(tmp_path):
    """Test that the check method logs an error when the file is not accessible."""
    read_only_dir = tmp_path / "read_only"
    os.makedirs(read_only_dir, mode=0o555)
    inaccessible_file = read_only_dir / "test.jsonl"

    mock_config = MagicMock()
    mock_config.storage_file_path = str(inaccessible_file)

    storage = FileStorage(config=mock_config)

    with patch("logging.error") as mock_log_error:
        storage.check()
        mock_log_error.assert_called_once()
        assert "Error accessing file storage" in mock_log_error.call_args[0][0]
