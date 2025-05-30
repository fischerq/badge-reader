"""The badge reader component."""
import logging

from homeassistant.core import HomeAssistant

DOMAIN = "badgereader"
PLATFORMS = ["sensor", "binary_sensor"]

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the badge reader component."""
    hass.data[DOMAIN] = {}

    # You can add more setup logic here in the future, like
    # registering services or setting up config flow.

    _LOGGER.info("Badge Reader component is setting up.")

    # Return boolean to indicate that initialization was successful
    return True