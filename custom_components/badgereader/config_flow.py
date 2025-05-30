"""Config flow for Badge Reader integration."""
import logging

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required("nfc_card_uid"): str,
        vol.Required("reader_ip"): str,
        vol.Required("google_sheet_id"): str,
    }
)


class BadgeReaderConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Badge Reader."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(step_id="user", data_schema=STEP_USER_DATA_SCHEMA)

        # For now, just log the input and finish the flow
        _LOGGER.debug("Received configuration: %s", user_input)

        return self.async_create_entry(title="Badge Reader", data=user_input)