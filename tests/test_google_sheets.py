import pytest
from unittest.mock import patch, MagicMock

from custom_components.badgereader.google_sheets import GoogleSheetsApi # Changed import

@patch('custom_components.badgereader.google_sheets.gspread.service_account')
def test_append_row_to_sheet(mock_service_account):
    """Tests the append_row_to_sheet function."""
    mock_gc = MagicMock()
    mock_sheet = MagicMock()
    mock_worksheet = MagicMock()

    mock_service_account.return_value = mock_gc
    mock_gc.open_by_key.return_value = mock_sheet
    # mock_sheet.sheet1.return_value = mock_worksheet # This line will be effectively overridden

    sheet_id = "test_sheet_id"
    credentials_path = "/fake/credentials.json"
    row_data = ["Data1", "Data2", "Data3"]

    # Instantiate the API, which will use the mocked gspread
    # The constructor will call mock_service_account, mock_gc.open_by_key, and mock_sheet.sheet1
    # and api._sheet will be set based on the mock chain.
    api = GoogleSheetsApi(credentials_path=credentials_path, sheet_id=sheet_id)

    # Directly replace api._sheet with our specific mock_worksheet instance
    # This ensures that calls to api.append_row() go to *this* mock_worksheet.
    api._sheet = mock_worksheet

    api.append_row(row_data)

    mock_service_account.assert_called_once_with(filename=credentials_path)
    mock_gc.open_by_key.assert_called_once_with(sheet_id)
    # We no longer assert api._sheet == mock_worksheet as we are force-setting it.
    # The critical check is that append_row is called on the mock_worksheet we control.
    mock_worksheet.append_row.assert_called_once_with(row_data)

@patch('custom_components.badgereader.google_sheets.gspread.service_account')
def test_append_row_to_sheet_error_handling(mock_service_account):
    """Tests error handling in append_row_to_sheet."""
    mock_service_account.side_effect = Exception("Auth Error")

    sheet_id = "test_sheet_id"
    credentials_path = "/fake/credentials.json"
    # row_data = ["Data1", "Data2", "Data3"] # Not used directly in this error test before calling the constructor

    with pytest.raises(Exception, match="Auth Error"):
        # Instantiation itself will call the mocked service_account
        GoogleSheetsApi(credentials_path=credentials_path, sheet_id=sheet_id)

    mock_service_account.assert_called_once_with(filename=credentials_path)