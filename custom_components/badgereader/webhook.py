import json
import logging

from homeassistant.components.webhook import async_register_webhook
from homeassistant.core import HomeAssistant

from .const import DOMAIN, CONF_HOUSEKEEPER_CARD_UID

_LOGGER = logging.getLogger(__name__)

async def async_setup_webhook(hass: HomeAssistant, config_entry):
    """Set up the webhook to receive data from the NFC reader."""
    webhook_id = f"{DOMAIN}_{config_entry.entry_id}"
    _LOGGER.debug("Registering webhook with ID: %s", webhook_id)
    async_register_webhook(
        hass,
        DOMAIN,
        "Badge Reader",
        webhook_id,
        lambda hass, webhook_id, request: handle_webhook(hass, config_entry, request),
    )
    _LOGGER.info("Webhook registered with ID: %s", webhook_id)
    return webhook_id

async def handle_webhook(hass: HomeAssistant, config_entry, request):
    """Handle incoming webhook requests from the NFC reader."""
    _LOGGER.debug("Webhook received request")
    try:
        data = await request.json()
        _LOGGER.debug("Received data: %s", data)
        card_uid = data.get("uid")
        if not card_uid:
            _LOGGER.warning("Webhook received data with no 'uid' field: %s", data)
            return web.Response(status=400, text="Missing 'uid' in payload")

        configured_uid = config_entry.data.get(CONF_HOUSEKEEPER_CARD_UID)

        if card_uid == configured_uid:
            _LOGGER.info("Recognized housekeeper card tapped. UID: %s", card_uid)
            # TODO: Implement clock-in/clock-out logic and state updates
            return web.Response(status=200, text="Card recognized")
        else:
            _LOGGER.warning("Unrecognized card tapped. UID: %s", card_uid)
            # TODO: Implement feedback for unrecognized card (e.g., red light)
            return web.Response(status=401, text="Unrecognized card")

    except json.JSONDecodeError:
        _LOGGER.error("Webhook received invalid JSON data")
        return web.Response(status=400, text="Invalid JSON")
    except Exception as e:
        _LOGGER.error("Error processing webhook request: %s", e)
        return web.Response(status=500, text="Internal server error")