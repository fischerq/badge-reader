import json
import logging
import os
import gspread
import openpyxl
from oauth2client.service_account import ServiceAccountCredentials


# --- Storage Classes ---
class Storage:
    def log_swipe(self, timestamp, badge_id, action_json):
        raise NotImplementedError

    def check(self):
        raise NotImplementedError

    def read_latest_states(self):
        raise NotImplementedError

    def register_shift(self, action):
        raise NotImplementedError


class GoogleSheetStorage(Storage):
    def __init__(self, config):
        self.config = config
        self.scope = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive.file",
            "https://www.googleapis.com/auth/drive",
        ]
        self.creds_file = "/share/google_credentials_solalindenstein_docs_user.json"
        self.sheet = self._get_sheet()

    def _get_sheet(self):
        """Authenticates with Google Sheets and returns the worksheet."""
        try:
            creds = ServiceAccountCredentials.from_json_keyfile_name(
                self.creds_file, self.scope
            )
            client = gspread.authorize(creds)
            spreadsheet = client.open_by_url(self.config.google_spreadsheet_url)
            sheet = spreadsheet.worksheet(self.config.google_worksheet_name)
            return sheet
        except Exception as e:
            logging.error(f"Error accessing Google Sheet: {e}", exc_info=True)
            return None

    def log_swipe(self, timestamp, badge_id, action_json):
        if self.sheet:
            try:
                row = [timestamp, badge_id, action_json]
                self.sheet.insert_row(row, 3)
                logging.info(f"Logged to Google Sheet: {row}")
            except Exception as e:
                logging.error(f"Error logging to Google Sheet: {e}", exc_info=True)

    def check(self):
        logging.info("Checking Google Sheet access...")
        if self.sheet:
            try:
                cell_c1 = self.sheet.cell(1, 3).value  # C1
                logging.info(
                    f"Successfully accessed Google Sheet. Cell C1 contains: '{cell_c1}'"
                )

                headers = self.sheet.row_values(2)  # Assuming headers are in row 2
                expected_headers = ["Timestamp", "BadgeID", "Action"]
                if headers[: len(expected_headers)] == expected_headers:
                    logging.info(f"Google Sheet headers are correct: {headers}")
                else:
                    logging.warning(
                        f"Google Sheet headers are not as expected. "
                        f"Expected: {expected_headers}, Found: {headers}"
                    )
            except Exception as e:
                logging.error(f"Error reading from Google Sheet: {e}")
        else:
            logging.error("Could not access Google Sheet.")

    def read_latest_states(self):
        logging.info("Reading latest states from Google Sheet...")
        if not self.sheet:
            return {}
        try:
            all_records = self.sheet.get_all_values()  # Gets all data, headers included
            swipe_records = all_records[2:]  # Skip header rows
            swipe_records.reverse()

            latest_states = {}
            all_badge_uids = self.config.badge_map.keys()

            for record in swipe_records:
                if len(latest_states) == len(all_badge_uids):
                    break  # Found the latest state for all known badges

                timestamp_str, badge_id, action_str = record[0], record[1], record[2]
                badge_id = badge_id.strip().lower()

                if badge_id in all_badge_uids and badge_id not in latest_states:
                    action = json.loads(action_str)
                    latest_states[badge_id] = {
                        "state": action.get("new_state"),
                        "timestamp": int(timestamp_str),
                    }
            logging.info(f"Found {len(latest_states)} latest states in Google Sheet.")
            return latest_states
        except Exception as e:
            logging.error(
                f"Error reading latest states from Google Sheet: {e}", exc_info=True
            )
            return {}

    def register_shift(self, action):
        pass


class FileStorage(Storage):
    def __init__(self, config):
        self.config = config
        self.file_path = self.config.storage_file_path
        self.sheets_dir = self.config.storage_sheets_dir

    def log_swipe(self, timestamp, badge_id, action_json):
        try:
            with open(self.file_path, "a") as f:
                log_entry = {
                    "timestamp": timestamp,
                    "badge_id": badge_id,
                    "action": json.loads(action_json),
                }
                f.write(json.dumps(log_entry) + "\n")
            logging.info(f"Logged to file: {log_entry}")
        except Exception as e:
            logging.error(f"Error logging to file: {e}", exc_info=True)

    def check(self):
        logging.info(f"Checking file storage access at {self.file_path}...")
        try:
            with open(self.file_path, "a") as f:
                pass
            logging.info("File storage is accessible.")
        except Exception as e:
            logging.error(f"Error accessing file storage: {e}", exc_info=True)

    def read_latest_states(self):
        logging.info("Reading latest states from file...")
        latest_states = {}
        try:
            if not os.path.exists(self.file_path):
                logging.warning(f"Storage file not found: {self.file_path}")
                return {}

            with open(self.file_path, "r") as f:
                for line in f:
                    log_entry = json.loads(line)
                    badge_id = log_entry["badge_id"].strip().lower()
                    if badge_id in self.config.badge_map:
                        latest_states[badge_id] = {
                            "state": log_entry["action"].get("new_state"),
                            "timestamp": log_entry["timestamp"],
                        }
            logging.info(f"Found {len(latest_states)} latest states in file.")
            return latest_states
        except Exception as e:
            logging.error(f"Error reading latest states from file: {e}", exc_info=True)
            return {}

    def register_shift(self, action):
        person_name = self.config.people_map.get(action["person_id"], {}).get("name")
        full_filename = f"{self.sheets_dir}/monthly_data_{person_name}.xlsx"

        # create file if doesnt exist yet
        if not os.path.exists(full_filename):
            logging.warning(f"Sheets not found, dir: {self.sheets_dir}")
            os.listdir(self.sheets_dir)
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "Data"
            ws.append(["Badge Reader Data"])
            ws.append(["Person", "Shift Start", "Shift End", "Shift Duration (min)"])
            wb.save(filename=full_filename)

        wb = openpyxl.load_workbook(filename=full_filename)
        ws = wb.active
        ws.append(action)
        wb.save(filename=full_filename)
