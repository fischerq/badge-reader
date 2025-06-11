"""Tests for the badgereader component."""

import pytest

from homeassistant.core import HomeAssistant
from homeassistant.setup import async_setup_component # Changed import

async def test_async_setup(hass: HomeAssistant) -> None:
    """Test that the component is loaded correctly."""
    assert await async_setup_component(hass, "badgereader", {}) is True # Changed function call