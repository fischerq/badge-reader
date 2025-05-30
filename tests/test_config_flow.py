"""Tests for the Badge Reader config flow."""
from unittest.mock import patch

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType


async def test_form(hass: HomeAssistant) -> None:
    """Test we get the form."""
    result = await hass.config_entries.flow.async_init(
        "badgereader", context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "user"

    with patch(
        "custom_components.badgereader.config_flow.PlaceholderHub.authenticate",
        return_value=True,
    ):
        with patch(
            "custom_components.badgereader.async_setup_entry",
            return_value=True,
        ) as mock_setup_entry:
            result2 = await hass.config_entries.flow.async_configure(
                result["flow_id"],
                {
                    "nfc_card_uid": "TEST_UID",
                    "reader_ip": "192.168.1.100",
                    "google_sheet_id": "TEST_SHEET_ID",
                },
            )
            await hass.async_block_till_done()

    assert result2["type"] == FlowResultType.CREATE_ENTRY
    assert result2["title"] == "Badge Reader"
    assert result2["data"] == {
        "nfc_card_uid": "TEST_UID",
        "reader_ip": "192.168.1.100",
        "google_sheet_id": "TEST_SHEET_ID",
    }
    assert len(mock_setup_entry.mock_calls) == 1

# You would add tests for invalid input, connection errors, etc.
# For example:
# async def test_form_invalid_auth(hass: HomeAssistant) -> None:
#     """Test invalid authentication."""
#     result = await hass.config_entries.flow.async_init(
#         "badgereader", context={"source": config_entries.SOURCE_USER}
#     )
#
#     with patch(
#         "custom_components.badgereader.config_flow.PlaceholderHub.authenticate",
#         return_value=False,
#     ):
#         result2 = await hass.config_entries.flow.async_configure(
#             result["flow_id"],
#             {
#                 "nfc_card_uid": "TEST_UID",
#                 "reader_ip": "192.168.1.100",
#                 "google_sheet_id": "TEST_SHEET_ID",
#             },
#         )
#
#     assert result2["type"] == FlowResultType.FORM
#     assert result2["errors"] == {"base": "invalid_auth"}