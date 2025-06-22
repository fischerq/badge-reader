"""Google Sheets interaction module."""

import gspread

class GoogleSheetsApi:
    """Handles interactions with Google Sheets."""

    def __init__(self, credentials_path, sheet_id):
        """Initialize the Google Sheets API client.

        Args:
            credentials_path (str): Path to the Google API credentials file.
            sheet_id (str): The ID of the Google Sheet.
        """
        self._client = gspread.service_account(filename=credentials_path)
        self._sheet = self._client.open_by_key(sheet_id).sheet1 # Assuming data is on the first sheet

    def append_row(self, data):
        """Appends a row of data to the Google Sheet.

        Args:
            data (list): A list of values representing a row to append.
        """
        self._sheet.append_row(data)

    # TODO: Implement functions for reading data for reports
    # def read_data(self, start_date, end_date):
    #     """Reads data from the Google Sheet within a date range."""
    #     pass