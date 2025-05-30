"""Tests for the badgereader component."""

import pytest

from homeassistant.core import HomeAssistant
from homeassistant.helpers import setup_component

async def test_async_setup(hass: HomeAssistant) -> None:
    """Test that the component is loaded correctly."""
    assert await setup_component(hass, "badgereader", {}) is True