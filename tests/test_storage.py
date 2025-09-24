
import pytest
from unittest.mock import MagicMock, patch, call, ANY
from datetime import datetime
from io import BytesIO
import openpyxl

# Mock NFS before it's imported by the storage module
with patch.dict("sys.modules", {"libnfs": MagicMock()}):
    from badgereader_addon.badgereader.storage import NFSStorage

@pytest.fixture
def mock_config():
    """Fixture to create a mock config object."""
    config = MagicMock()
    config.nfs_server_address = "mock_server"
    config.nfs_share_path = "/mock_share"
    config.people_map = {"person1": {"name": "Fin"}}
    return config

@pytest.fixture
def mock_nfs_instance():
    """Fixture for a mocked NFS instance."""
    return MagicMock()

@pytest.fixture
def nfs_storage(mock_config, mock_nfs_instance):
    """Fixture for an NFSStorage instance with a mocked NFS client."""
    with patch("badgereader_addon.badgereader.storage.NFS", return_value=mock_nfs_instance):
        storage = NFSStorage(config=mock_config)
        return storage

def test_get_sheet_filename(nfs_storage):
    """Test the generation of the Excel sheet filename."""
    date_obj = datetime(2024, 7, 10)
    filename = nfs_storage._get_sheet_filename("Fin", date_obj)
    assert filename == "Arbeitszeit Fin July 2024.xlsx"

def test_create_new_sheet(nfs_storage, mock_nfs_instance):
    """Test the creation of a new timesheet from scratch."""
    filename = "test_sheet.xlsx"
    mock_file = MagicMock()
    mock_nfs_instance.open.return_value.__enter__.return_value = mock_file

    with patch("openpyxl.Workbook") as mock_workbook_class:
        mock_wb = MagicMock()
        mock_ws = MagicMock()
        mock_wb.active = mock_ws
        mock_workbook_class.return_value = mock_wb

        # Mock the __getitem__ to return a mock cell, which is what openpyxl does
        mock_ws.__getitem__.return_value = MagicMock()

        nfs_storage._create_new_sheet(filename, initial_balance=50)

        # Verify that the cells were written to correctly
        # Check that __getitem__ was called for the right cells
        mock_ws.__getitem__.assert_any_call('A2')
        mock_ws.__getitem__.assert_any_call('B2')
        mock_ws.__getitem__.assert_any_call('A4')
        mock_ws.__getitem__.assert_any_call('B4')

        # Verify headers were added
        mock_ws.append.assert_called_once()

        # Verify file write operation
        mock_nfs_instance.open.assert_called_with(filename, "wb")
        mock_wb.save.assert_called_once()


def test_ensure_sheet_exists_already_exists(nfs_storage, mock_nfs_instance):
    """Test that if the sheet for the current month exists, it is returned."""
    now = datetime(2024, 7, 10)
    current_filename = nfs_storage._get_sheet_filename("Fin", now)
    mock_nfs_instance.exists.return_value = True

    filename = nfs_storage._ensure_sheet_exists("person1", now)

    mock_nfs_instance.exists.assert_called_with(current_filename)
    assert filename == current_filename

def test_ensure_sheet_exists_copies_previous(nfs_storage, mock_nfs_instance):
    """Test that a new sheet is created by copying the previous month's sheet."""
    now = datetime(2024, 8, 1)
    current_filename = "Arbeitszeit Fin August 2024.xlsx"
    prev_filename = "Arbeitszeit Fin July 2024.xlsx"

    mock_nfs_instance.exists.side_effect = [False, True]

    wb_data_only = openpyxl.Workbook()
    ws_data_only = wb_data_only.active
    ws_data_only['B4'].value = 120
    buffer = BytesIO()
    wb_data_only.save(buffer)
    buffer.seek(0)

    mock_file = MagicMock()
    mock_file.read.return_value = buffer.getvalue()
    mock_nfs_instance.open.return_value.__enter__.return_value = mock_file

    with patch.object(nfs_storage, '_create_new_sheet') as mock_create:
        nfs_storage._ensure_sheet_exists("person1", now)

        mock_nfs_instance.exists.assert_has_calls([call(current_filename), call(prev_filename)])
        mock_nfs_instance.open.assert_called_with(prev_filename, "rb")
        mock_create.assert_called_once_with(current_filename, 120)


def test_append_to_sheet(nfs_storage, mock_nfs_instance):
    """Test that a new shift is correctly appended and the balance is updated."""
    filename = "test_sheet.xlsx"
    action = {
        'name': 'Fin',
        'shift_start': '2024-07-10T09:00:00',
        'shift_end': '2024-07-10T14:30:00',
        'duration_minutes': 330
    }

    # Create a workbook instance that will be returned by load_workbook
    mock_wb = openpyxl.Workbook()
    mock_ws = mock_wb.active
    mock_ws["B2"] = 50  # Previous balance
    mock_ws["B3"] = 300 # Target hours
    # Simulate a header and some data so that max_row is realistic
    mock_ws.append(["H1", "H2", "H3", "H4", "H5", "H6", "H7"])
    mock_ws.append(["D1", "D2", "D3", "D4", "D5", "D6", 50])

    # When the function reads the file, we'll have it load our mock workbook
    with patch("openpyxl.load_workbook", return_value=mock_wb) as mock_load_workbook, \
         patch.object(nfs_storage.nfs, "open", MagicMock()) as mock_nfs_open, \
         patch.object(mock_wb, "save") as mock_save:

        # We need to mock the context manager for the file open
        mock_file_content = BytesIO()
        mock_nfs_open.return_value.__enter__.return_value.read.return_value = mock_file_content

        new_balance = nfs_storage._append_to_sheet(filename, action)

        assert new_balance == 80  # 50 + (330 - 300)

        # Check that the workbook was loaded and saved
        mock_load_workbook.assert_called_once()
        mock_save.assert_called_once()

        # Check the values of the appended row
        # The last row should have been appended by the function
        last_row = list(mock_ws.values)[-1]
        assert last_row[0] == action["name"]
        assert last_row[3] == action["duration_minutes"]
        assert last_row[6] == 80 # New balance

        # Check that the running balance is updated
        assert mock_ws["B4"].value == 80

def test_register_shift_orchestrates_correctly(nfs_storage):
    """Test that register_shift calls the helper functions correctly."""
    action = {'person_id': 'person1', 'duration_minutes': 315}
    sheet_filename = "Arbeitszeit Fin July 2024.xlsx"
    expected_balance = 100

    with patch.object(nfs_storage, '_ensure_sheet_exists', return_value=sheet_filename) as mock_ensure, \
         patch.object(nfs_storage, '_append_to_sheet', return_value=expected_balance) as mock_append:

        balance = nfs_storage.register_shift(action)

        mock_ensure.assert_called_once_with(action['person_id'], ANY)
        mock_append.assert_called_once_with(sheet_filename, action)
        assert balance == expected_balance
