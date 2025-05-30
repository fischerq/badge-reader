import pytest
from unittest.mock import patch, MagicMock

from custom_components.badgereader.google_sheets import append_row_to_sheet

@patch('custom_components.badgereader.google_sheets.gspread.service_account')
def test_append_row_to_sheet(mock_service_account):
    """Tests the append_row_to_sheet function."""
    mock_gc = MagicMock()
    mock_sheet = MagicMock()
    mock_worksheet = MagicMock()

    mock_service_account.return_value = mock_gc
    mock_gc.open_by_key.return_value = mock_sheet
    mock_sheet.sheet1.return_value = mock_worksheet

    sheet_id = "test_sheet_id"
    credentials_path = "/fake/credentials.json"
    row_data = ["Data1", "Data2", "Data3"]

    append_row_to_sheet(sheet_id, credentials_path, row_data)

    mock_service_account.assert_called_once_with(filename=credentials_path)
    mock_gc.open_by_key.assert_called_once_with(sheet_id)
    mock_sheet.sheet1.assert_called_once()
    mock_worksheet.append_row.assert_called_once_with(row_data)

@patch('custom_components.badgereader.google_sheets.gspread.service_account')
def test_append_row_to_sheet_error_handling(mock_service_account):
    """Tests error handling in append_row_to_sheet."""
    mock_service_account.side_effect = Exception("Auth Error")

    sheet_id = "test_sheet_id"
    credentials_path = "/fake/credentials.json"
    row_data = ["Data1", "Data2", "Data3"]

    with pytest.raises(Exception, match="Auth Error"):
        append_row_to_sheet(sheet_id, credentials_path, row_data)

    mock_service_account.assert_called_once_with(filename=credentials_path)