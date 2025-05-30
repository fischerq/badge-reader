"""DataUpdateCoordinator for the NFC Badge Reader integration."""

import asyncio
import logging
from datetime import timedelta

import aiohttp

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .api import UfrNanoOnlineApi
from .const import DOMAIN, LOGGER, READER_STATUS_INTERVAL

_LOGGER = logging.getLogger(__name__)


class UfrNanoOnlineCoordinator(DataUpdateCoordinator):
    """Coordinator for the NFC Badge Reader."""

    def __init__(
        self,
        hass: HomeAssistant,
        api: UfrNanoOnlineApi,
        reader_ip: str,
        reader_port: int,
    ) -> None:
        """Initialize coordinator."""
        super().__init__(
            hass,
            LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=READER_STATUS_INTERVAL),
        )
        self.api = api
        self._reader_ip = reader_ip
        self._reader_port = reader_port
        self.reader_online = False

    async def _async_update_data(self):
        """Fetch data from the reader API."""
        try:
            # Attempt to send a simple command to check if the reader is online
            # This assumes the /setled endpoint is always available when the reader is online
            # A more robust check might be needed if the reader has a dedicated status endpoint
            await self.api.set_led(0, 0, 0)  # Try setting LEDs to off
            self.reader_online = True
            _LOGGER.debug("NFC reader is online.")
        except (aiohttp.ClientError, asyncio.TimeoutError):
            self.reader_online = False
            _LOGGER.debug("NFC reader is offline.")
        except Exception as err:
            self.reader_online = False
            raise UpdateFailed(f"Error communicating with reader API: {err}") from err

        # In a more complex scenario, this could fetch other data from the reader
        # if relevant status endpoints existed. For this project, the primary "data"
        # is the reader's online status and the card UID received via webhook.

        # The coordinator's primary role here is to keep track of the reader's
        # online status for the binary sensor. Card read events are handled
        # by the webhook directly, which will then trigger entity updates.

        return {"reader_online": self.reader_online}

    def process_card_read(self, card_uid: str):
        """Process a card read event received via the webhook."""
        # This method is called by the webhook handler when a card is scanned.
        # It's the entry point for handling the actual badge tap logic.
        _LOGGER.debug("Card UID received via webhook: %s", card_uid)
        # TODO: Implement logic to compare UID, determine check-in/out, update
        # Home Assistant entities, update Google Sheet, send email, etc.
        # This will likely involve dispatching events within Home Assistant or
        # calling other methods on the coordinator or a separate data manager.

        # For now, we'll just log it. The actual state updates for sensors
        # will be triggered by the logic implemented after this file.