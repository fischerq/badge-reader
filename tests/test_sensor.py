"""Tests for the sensor platform."""

from unittest.mock import patch

from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er

async def test_sensor_setup(hass: HomeAssistant):
    """Test sensor setup."""
    # Mock the async_setup_entry method of the sensor platform
    with patch(
        "custom_components.badgereader.sensor.async_setup_entry",
        return_value=True,
    ) as mock_setup_entry:
        # Load the sensor platform
        await hass.helpers.discovery.async_load_platform(
            "sensor",
            "badgereader",
            {},
            {"domain": "badgereader"},
        )
        await hass.async_block_till_done()

        # Assert that the async_setup_entry method was called
        assert mock_setup_entry.called


async def test_housekeeper_status_sensor(hass: HomeAssistant):
    """Test the housekeeper status sensor."""
    # Mock the creation of the sensor entity
    with patch(
        "custom_components.badgereader.sensor.HousekeeperStatusSensor",
    ) as mock_sensor:
        await hass.helpers.discovery.async_load_platform(
            "sensor",
            "badgereader",
            {},
            {"domain": "badgereader"},
        )
        await hass.async_block_till_done()

        # Assert that the sensor entity was created
        assert mock_sensor.called

    # You would typically add more tests here to check the sensor's state
    # and attributes after it's been created and updated. This requires
    # more detailed mocking of the component's internal state and
    # updates.