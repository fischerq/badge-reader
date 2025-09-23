import json
import logging


class Config:
    def __init__(self, config_path="/data/options.json"):
        # Default values
        self.notification_domain = "notify"
        self.notification_service = "gmail_solalindenstein"
        self.notification_emails = []
        self.badges = []
        self.people = []
        self.swipe_debounce_minutes = 1
        self.swipe_time_buffer_minutes = 3
        self.storage_backend = "google_sheets"
        self.storage_file_path = "/share/badge-reader-mount/swipe_log.jsonl"
        self.storage_sheets_dir = "/share/badge-reader-mount"
        self.google_spreadsheet_url = "https://docs.google.com/spreadsheets/d/1qZ3-8Q3z4Nn3q_V3RArP3p8G_sWn3j8aC5H6j2k_4zE/edit#gid=0"  # Dummy URL, replace with your actual URL
        self.google_worksheet_name = "Data"
        self.version = "unknown"
        self.people_map = {}
        self.badge_map = {}
        self.badge_to_person_map = {}

        self.load_from_file(config_path)

    def load_from_file(self, config_path):
        try:
            with open(config_path, "r") as f:
                options = json.load(f)
                self.notification_domain = options.get(
                    "notification_domain", self.notification_domain
                )
                self.notification_service = options.get(
                    "notification_service", self.notification_service
                )
                self.notification_emails = options.get(
                    "notification_emails", self.notification_emails
                )
                self.badges = options.get("badges", self.badges)
                self.people = options.get("people", self.people)
                self.swipe_debounce_minutes = options.get(
                    "swipe_debounce_minutes", self.swipe_debounce_minutes
                )
                self.swipe_time_buffer_minutes = options.get(
                    "swipe_time_buffer_minutes", self.swipe_time_buffer_minutes
                )
                self.storage_backend = options.get(
                    "storage_backend", self.storage_backend
                )
                self.storage_file_path = options.get(
                    "storage_file_path", self.storage_file_path
                )
                self.storage_sheets_dir = options.get(
                    "storage_sheets_dir", self.storage_sheets_dir
                )
                self.google_spreadsheet_url = options.get(
                    "google_spreadsheet_url", self.google_spreadsheet_url
                )
                self.google_worksheet_name = options.get(
                    "google_worksheet_name", self.google_worksheet_name
                )
                # self.version = config.get('version', self.version) # Version is not in options.json
        except FileNotFoundError:
            logging.error(
                f"{config_path} not found. Please ensure it exists in the add-on's data directory."
            )
        except json.JSONDecodeError as e:
            logging.error(f"Error parsing {config_path}: {e}")

        # Create lookups for easier access
        self.people_map = {person["id"]: person for person in self.people}
        self.badge_map = {
            badge["uid"].lower().strip(): badge["peopleID"] for badge in self.badges
        }
        self.badge_to_person_map = {
            uid: self.people_map.get(pid) for uid, pid in self.badge_map.items()
        }
