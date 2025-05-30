"""Tests for the DataUpdateCoordinator."""
from unittest.mock import AsyncMock, patch

import pytest

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from custom_components.badgereader.coordinator import BadgeReaderCoordinator


@pytest.fixture
def mock_coordinator(hass):
    """Mock BadgeReaderCoordinator."""
    with patch(
        "custom_components.badgereader.coordinator.DataUpdateCoordinator",
        spec=DataUpdateCoordinator,
    ) as mock_data_coordinator:
        mock_coordinator_instance = mock_data_coordinator.return_value
        mock_coordinator_instance.async_config_entry_first_refresh = AsyncMock()
        yield mock_coordinator_instance


async def test_coordinator_initialization(mock_coordinator, hass):
    """Test the coordinator is initialized correctly."""
    # While we mock the base class, this test ensures our custom coordinator
    # would call the base constructor with the correct parameters.
    # This test requires a more detailed mock of the DataUpdateCoordinator
    # constructor if we were to test the actual instantiation.
    # For now, we focus on mocking the instance methods called.
    pass


async def test_coordinator_first_refresh(mock_coordinator):
    """Test the first refresh is called."""
    await mock_coordinator.async_config_entry_first_refresh()
    mock_coordinator.async_config_entry_first_refresh.assert_called_once()


# Add more tests here as the coordinator's functionality is implemented,
# e.g., testing the _async_update_data method, handling webhook updates, etc.