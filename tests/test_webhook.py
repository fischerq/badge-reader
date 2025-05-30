"""Tests for the badgereader webhook."""

import json
from unittest.mock import patch

from homeassistant.components import webhook
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr

from .const import DOMAIN

async def test_webhook_receives_data(hass: HomeAssistant, hass_client) -> None:
    """Test the webhook receives and processes data."""
    hass.async_create_task(
        hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": "user"},
            data={
                "name": "Test Badge Reader",
                "card_uid": "TEST_UID_12345",
                "reader_ip": "192.168.1.100",
                "reader_api_password": "password",
                "google_sheet_id": "sheet_id",
                "google_credential_path": "/config/credentials.json",
                "weekly_target_hours": 40,
                "usual_work_days": 5,
                "pdf_output_path": "/config/pdf_reports",
            },
        )
    )
    await hass.async_block_till_done()

    webhook_id = None
    for entry in hass.config_entries.async_entries(DOMAIN):
        webhook_id = entry.data.get(webhook.CONF_WEBHOOK_ID)
        break

    assert webhook_id is not None

    client = await hass_client()

    # Test with a valid UID
    payload = {"uid": "TEST_UID_12345"}
    with patch(
        "custom_components.badgereader.webhook.process_badge_scan"
    ) as mock_process_badge_scan:
        resp = await client.post(
            f"/api/webhook/{webhook_id}", data=json.dumps(payload)
        )
        assert resp.status == 200
        assert mock_process_badge_scan.called
        assert mock_process_badge_scan.call_args[0][1] == "TEST_UID_12345"

    # Test with an invalid UID
    payload = {"uid": "INVALID_UID_67890"}
    with patch(
        "custom_components.badgereader.webhook.process_badge_scan"
    ) as mock_process_badge_scan:
        resp = await client.post(
            f"/api/webhook/{webhook_id}", data=json.dumps(payload)
        )
        assert resp.status == 401  # Unauthorized
        assert not mock_process_badge_scan.called

    # Test with missing UID
    payload = {"other_data": "value"}
    with patch(
        "custom_components.badgereader.webhook.process_badge_scan"
    ) as mock_process_badge_scan:
        resp = await client.post(
            f"/api/webhook/{webhook_id}", data=json.dumps(payload)
        )
        assert resp.status == 400  # Bad Request
        assert not mock_process_badge_scan.called

    # Test with non-JSON payload
    payload_str = "uid=TEST_UID_12345"
    with patch(
        "custom_components.badgereader.webhook.process_badge_scan"
    ) as mock_process_badge_scan:
        resp = await client.post(
            f"/api/webhook/{webhook_id}", data=payload_str
        )
        # The webhook handler expects JSON, so this should fail
        assert resp.status == 400
        assert not mock_process_badge_scan.called