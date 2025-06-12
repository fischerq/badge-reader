"""Tests for the binary_sensor platform."""
from unittest.mock import patch

import pytest

from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry


async def test_binary_sensor_setup(hass: HomeAssistant) -> None:
    """Test the binary sensor platform setup."""
    config_entry = MockConfigEntry(domain="badgereader", data={"test": "test"})
    config_entry.add_to_hass(hass)

    with patch(
        "custom_components.badgereader.binary_sensor.async_setup_entry",
        return_value=True,
    ) as mock_setup_entry:
        await hass.config_entries.async_setup(config_entry.entry_id)
        await hass.async_block_till_done()

    assert mock_setup_entry.called