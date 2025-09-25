import json
import logging
import os
import openpyxl
from libnfs import NFS
from datetime import datetime, timedelta
from io import BytesIO


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


class NFSStorage(Storage):
    def __init__(self, config):
        self.config = config
        nfs_url = f"nfs://{self.config.nfs_server_address}{self.config.nfs_share_path}"
        self.nfs = NFS(nfs_url)
        self.log_file_path = "swipe_log.jsonl"

    def log_swipe(self, timestamp, badge_id, action_json):
        try:
            log_entry = {
                "timestamp": timestamp,
                "badge_id": badge_id,
                "action": json.loads(action_json),
            }
            log_line = json.dumps(log_entry) + "\n"
            with self.nfs.open(self.log_file_path, "a") as f:
                f.write(log_line.encode())
            logging.info(f"Logged to NFS: {log_entry}")
        except Exception as e:
            logging.error(f"Error logging to NFS: {e}", exc_info=True)

    def check(self):
        logging.info(f"Checking NFS storage access at {self.config.nfs_server_address}:{self.config.nfs_share_path}...")
        try:
            self.nfs.listdir(".")
            logging.info("NFS storage is accessible.")
        except Exception as e:
            logging.error(f"Error accessing NFS storage: {e}", exc_info=True)

    def read_latest_states(self):
        logging.info("Reading latest states from NFS...")
        latest_states = {}
        try:
            if not self.nfs.exists(self.log_file_path):
                logging.warning(f"Storage file not found on NFS: {self.log_file_path}")
                return {}

            with self.nfs.open(self.log_file_path, "r") as f:
                for line in f:
                    log_entry = json.loads(line)
                    badge_id = log_entry["badge_id"].strip().lower()
                    if badge_id in self.config.badge_map:
                        latest_states[badge_id] = {
                            "state": log_entry["action"].get("new_state"),
                            "timestamp": log_entry["timestamp"],
                        }
            logging.info(f"Found {len(latest_states)} latest states in NFS.")
            return latest_states
        except Exception as e:
            logging.error(f"Error reading latest states from NFS: {e}", exc_info=True)
            return {}

    def _get_sheet_filename(self, person_name, date_obj):
        month_str = date_obj.strftime('%B')
        year = date_obj.year
        return f"Arbeitszeit {person_name} {month_str} {year}.xlsx"

    def _create_new_sheet(self, filename, initial_balance=0):
        try:
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "Data"
            ws['A1'] = "Badge Reader Data"

            ws['A2'] = "Time Balance from Previous Month (min)"
            ws['B2'] = initial_balance

            ws['A3'] = "Target Hours per Shift (min)"
            ws['B3'] = 300  # 5 hours * 60 minutes

            ws['A4'] = "Current Running Balance (min)"
            ws['B4'] = initial_balance # Initially the same as the start balance

            # Headers for the data table
            headers = ["Person", "Shift Start", "Shift End", "Shift Duration (min)", "Target for Day (min)", "Net Change for Day (min)", "Running Balance (min)"]
            ws.append(headers)

            buffer = BytesIO()
            wb.save(buffer)
            buffer.seek(0)

            with self.nfs.open(filename, "wb") as f:
                f.write(buffer.read())
            logging.info(f"Successfully created new sheet: {filename}")
            return True
        except Exception as e:
            logging.error(f"Error creating new sheet {filename}: {e}", exc_info=True)
            return False

    def _ensure_sheet_exists(self, person_name, now):
        current_filename = self._get_sheet_filename(person_name, now)

        if self.nfs.exists(current_filename):
            return current_filename

        logging.info(f"Sheet for {person_name} for {now.strftime('%B')} {now.year} not found. Looking for previous month's sheet.")

        first_day_of_current_month = now.replace(day=1)
        last_day_of_previous_month = first_day_of_current_month - timedelta(days=1)
        prev_month_filename = self._get_sheet_filename(person_name, last_day_of_previous_month)

        initial_balance = 0
        if self.nfs.exists(prev_month_filename):
            logging.info(f"Found previous month's sheet: {prev_month_filename}. Reading end of month balance.")
            try:
                with self.nfs.open(prev_month_filename, "rb") as f:
                    file_content = f.read()
                    workbook_stream = BytesIO(file_content)
                    # Use data_only=True to read the calculated value of a formula
                    wb_data_only = openpyxl.load_workbook(workbook_stream, data_only=True)
                    ws_data_only = wb_data_only.active
                    balance_value = ws_data_only['B4'].value
                    if balance_value is not None:
                        initial_balance = float(balance_value)
                    logging.info(f"Balance from previous month is {initial_balance}")

            except Exception as e:
                logging.error(f"Error reading balance from {prev_month_filename}: {e}", exc_info=True)

        if self._create_new_sheet(current_filename, initial_balance):
            return current_filename

        return None  # Indicate failure

    def _append_to_sheet(self, filename, action):
        try:
            with self.nfs.open(filename, "rb") as f:
                file_content = f.read()
                workbook_stream = BytesIO(file_content)
                wb = openpyxl.load_workbook(workbook_stream)

            ws = wb.active

            # Find the last row with data
            last_row = ws.max_row
            
            # Determine the previous running balance
            if last_row < 6: # Header is on row 5, so first data row is 6
                previous_balance = ws['B2'].value # From previous month
            else:
                previous_balance = ws.cell(row=last_row, column=7).value

            shift_duration = action.get('duration_minutes', 0)
            target_for_day = ws['B3'].value
            net_change = shift_duration - target_for_day
            new_balance = previous_balance + net_change

            row_data = [
                action.get('name'),
                action.get('shift_start'),
                action.get('shift_end'),
                shift_duration,
                target_for_day,
                net_change,
                new_balance
            ]
            ws.append(row_data)

            # Update the current running balance in the header
            ws['B4'] = new_balance

            buffer = BytesIO()
            wb.save(buffer)
            buffer.seek(0)

            with self.nfs.open(filename, "wb") as f:
                f.write(buffer.read())
            logging.info(f"Successfully registered shift in {filename}")
            return new_balance
        except Exception as e:
            logging.error(f"Error appending to sheet {filename}: {e}", exc_info=True)
            return None

    def register_shift(self, action):
        person_name = action.get("name")
        if not person_name:
            person_id = action.get("person_id")
            person_info = self.config.people_map.get(person_id)
            if person_info:
                person_name = person_info.get("name")

        if not person_name:
            logging.error(f"Could not determine person name from action: {action}")
            return None

        now = datetime.now()
        sheet_filename = self._ensure_sheet_exists(person_name, now)

        if sheet_filename:
            return self._append_to_sheet(sheet_filename, action)
        else:
            logging.error(f"Failed to ensure sheet exists for {person_name}. Cannot register shift.")
            return None
