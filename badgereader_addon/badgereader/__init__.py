"""The badge reader component."""
import logging

from homeassistant.core import HomeAssistant
from homeassistant.components.frontend import async_register_built_in_panel

DOMAIN = "badgereader"
PLATFORMS = ["sensor", "binary_sensor"]

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry):
    """Set up a config entry."""
    # This is where you would normally set up your integration from the config entry.
    # For example, hass.data[DOMAIN][entry.entry_id] = ...

    await async_register_built_in_panel(
        hass,
        "badgereader",
        "Badge Reader",
        "mdi:badge-account",
        frontend_url_path="badgereader_panel",
        config={"path": "/api/panel_custom/badgereader/index.html"},
        require_admin=True,
    )

    return True


async def async_unload_entry(hass: HomeAssistant, entry):
    """Unload a config entry."""
    # This is where you would normally unload your integration.
    # For example, hass.data[DOMAIN].pop(entry.entry_id)

    await hass.components.frontend.async_remove_panel("badgereader")
    return True


async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the badge reader component."""
    hass.data[DOMAIN] = {}

    # You can add more setup logic here in the future, like
    # registering services or setting up config flow.

    _LOGGER.info("Badge Reader component is setting up.")

    # Return boolean to indicate that initialization was successful
    return True