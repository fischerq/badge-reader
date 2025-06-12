"""Tests for the base entity classes."""
from unittest.mock import MagicMock # Added import
from homeassistant.helpers.entity import Entity

from custom_components.badgereader.entity import BadgeReaderEntity


def test_badge_reader_entity_base_class():
    """Test the BadgeReaderEntity base class."""

    class MockBadgeReaderEntity(BadgeReaderEntity):
        """Mock entity for testing."""

        @property
        def unique_id(self) -> str:
            """Return a unique ID."""
            return "mock_unique_id"

    # Create a mock coordinator with a config_entry and unique_id
    # Also mock reader_ip as it's used in device_info
    mock_coordinator = MagicMock() # Need to import MagicMock
    mock_coordinator.config_entry = MagicMock()
    mock_coordinator.config_entry.unique_id = "badgereader_device" # Expected unique_id
    mock_coordinator.reader_ip = "1.2.3.4" # Mock reader_ip

    # The entity expects the coordinator as the first argument.
    # The second argument config_entry_data is optional and defaults to None.
    entity = MockBadgeReaderEntity(coordinator=mock_coordinator)

    assert isinstance(entity, Entity)
    assert entity.should_poll is False  # Custom components should not poll by default
    assert entity.unique_id == "mock_unique_id"
    assert entity.device_info is not None
    assert entity.device_info["identifiers"] == {("badgereader", "badgereader_device")}
    assert entity.device_info["name"] == "Badge Reader"
    assert entity.device_info["manufacturer"] == "Your Name or Project Name"
    assert entity.device_info["model"] == "NFC Badge Reader"