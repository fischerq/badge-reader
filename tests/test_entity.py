"""Tests for the base entity classes."""
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

    entity = MockBadgeReaderEntity({})  # Pass a mock config_entry data

    assert isinstance(entity, Entity)
    assert entity.should_poll is False  # Custom components should not poll by default
    assert entity.unique_id == "mock_unique_id"
    assert entity.device_info is not None
    assert entity.device_info["identifiers"] == {("badgereader", "badgereader_device")}
    assert entity.device_info["name"] == "Badge Reader"
    assert entity.device_info["manufacturer"] == "Your Name or Project Name"
    assert entity.device_info["model"] == "NFC Badge Reader"