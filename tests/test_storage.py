
import pytest
from unittest.mock import MagicMock, patch, call
from datetime import datetime, timedelta
from io import BytesIO
import openpyxl

# Mock the libnfs module before it is imported by the storage module
with patch.dict("sys.modules", {"libnfs": MagicMock()}):
    from badgereader_addon.badgereader.storage import NFSStorage

@pytest.fixture
def mock_config():
    """Provides a mock configuration object."""
    config = MagicMock()
    config.nfs_server_address = "mock-server"
    config.nfs_share_path = "/mock-share"
    config.people_map = {"person1": {"name": "Fin"}}
    return config

@pytest.fixture
def nfs_storage(mock_config):
    """Provides an NFSStorage instance with a mocked NFS client."""
    # This patch replaces the NFS class with a mock, so the storage instance will have a mock NFS client
    with patch("badgereader_addon.badgereader.storage.NFS") as mock_nfs_class:
        storage = NFSStorage(config=mock_config)
        yield storage

def test_get_sheet_filename(nfs_storage):
    """Ensures the filename is generated correctly."""
    date_obj = datetime(2024, 7, 10)
    assert nfs_storage._get_sheet_filename("Fin", date_obj) == "Arbeitszeit Fin July 2024.xlsx"


def test_create_new_sheet(nfs_storage):
    """Tests that a new sheet is created with the correct initial values and format."""
    with patch.object(nfs_storage.nfs, 'open', MagicMock()) as mock_nfs_open, \
         patch("openpyxl.Workbook") as mock_workbook_class:

        mock_wb = MagicMock()
        mock_ws = MagicMock()
        mock_wb.active = mock_ws
        mock_workbook_class.return_value = mock_wb

        # Mock the save method to write to a real BytesIO buffer
        buffer = BytesIO()
        mock_wb.save.side_effect = buffer.write

        result = nfs_storage._create_new_sheet("test.xlsx", initial_balance=50)

        assert result is True
        mock_ws.__setitem__.assert_any_call('B2', 50)
        mock_ws.append.assert_called_once()
        mock_nfs_open.assert_called_once_with("test.xlsx", "wb")

def test_ensure_sheet_exists_when_it_already_does(nfs_storage):
    """Tests that the existing filename is returned if the sheet exists."""
    now = datetime.now()
    person_name = "Fin"
    expected_filename = nfs_storage._get_sheet_filename(person_name, now)

    with patch.object(nfs_storage.nfs, 'exists', return_value=True) as mock_exists:
        filename = nfs_storage._ensure_sheet_exists(person_name, now)
        mock_exists.assert_called_once_with(expected_filename)
        assert filename == expected_filename

def test_ensure_sheet_exists_copies_from_previous_month(nfs_storage):
    """Tests that a new sheet is created with the balance from the previous month."""
    now = datetime(2024, 8, 1)
    person_name = "Fin"
    current_filename = nfs_storage._get_sheet_filename(person_name, now)
    prev_month_date = now.replace(day=1) - timedelta(days=1)
    prev_filename = nfs_storage._get_sheet_filename(person_name, prev_month_date)

    # Create a workbook to represent the previous month's file
    prev_wb = openpyxl.Workbook()
    prev_ws = prev_wb.active
    prev_ws['B4'] = 120.0  # Ending balance
    prev_buffer = BytesIO()
    prev_wb.save(prev_buffer)
    prev_buffer.seek(0)

    with patch.object(nfs_storage.nfs, 'exists', side_effect=[False, True]) as mock_exists, \
         patch.object(nfs_storage.nfs, 'open') as mock_nfs_open, \
         patch.object(nfs_storage, '_create_new_sheet') as mock_create:

        # The read of the previous month's file
        mock_nfs_open.return_value.__enter__.return_value.read.return_value = prev_buffer.getvalue()

        nfs_storage._ensure_sheet_exists(person_name, now)

        mock_exists.assert_has_calls([call(current_filename), call(prev_filename)])
        mock_nfs_open.assert_called_with(prev_filename, "rb")
        mock_create.assert_called_once_with(current_filename, 120.0)

def test_append_to_sheet(nfs_storage):
    """Tests that a shift is correctly appended and the balance updated."""
    filename = "test.xlsx"
    action = {'name': 'Fin', 'duration_minutes': 330, 'shift_start': '-', 'shift_end': '-'}

    # Create an in-memory workbook to be read
    wb = openpyxl.Workbook()
    ws = wb.active
    ws["B2"] = 50.0  # Starting balance
    ws["B3"] = 300.0 # Target
    ws.append(["H1", "H2", "H3", "H4", "H5", "H6", "H7"])
    ws.append(["D1", "D2", "D3", "D4", "D5", "D6", 100.0]) # Last shift's balance
    read_buffer = BytesIO()
    wb.save(read_buffer)
    read_buffer.seek(0)

    # This buffer will capture the final saved workbook
    write_buffer = BytesIO()

    def open_side_effect(path, mode):
        if mode == 'rb':
            mock_file = MagicMock()
            mock_file.read.return_value = read_buffer.getvalue()
            return MagicMock(__enter__=MagicMock(return_value=mock_file))
        elif mode == 'wb':
            # When writing, we can use a real BytesIO to capture the output
            return MagicMock(__enter__=MagicMock(return_value=write_buffer))

    with patch.object(nfs_storage.nfs, 'open', side_effect=open_side_effect) as mock_open:
        new_balance = nfs_storage._append_to_sheet(filename, action)

    assert new_balance == 130.0 # 100 + 330 - 300

    # Verify the contents of the saved workbook
    write_buffer.seek(0)
    final_wb = openpyxl.load_workbook(write_buffer)
    final_ws = final_wb.active
    assert final_ws['B4'].value == 130.0
    last_row_values = [cell.value for cell in final_ws[final_ws.max_row]]
    assert last_row_values[6] == 130.0

def test_register_shift(nfs_storage):
    """High-level test to ensure register_shift orchestrates correctly."""
    action = {'person_id': 'person1', 'name': 'Fin', 'duration_minutes': 400}
    test_now = datetime(2024, 7, 15)

    # Mock the dependencies of register_shift
    with patch("badgereader_addon.badgereader.storage.datetime") as mock_datetime, \
         patch.object(nfs_storage, '_ensure_sheet_exists', return_value="sheet.xlsx") as mock_ensure, \
         patch.object(nfs_storage, '_append_to_sheet', return_value=500.0) as mock_append:

        mock_datetime.now.return_value = test_now

        result = nfs_storage.register_shift(action)

        assert result == 500.0
        mock_ensure.assert_called_once_with("Fin", test_now)
        mock_append.assert_called_once_with("sheet.xlsx", action)

