"""Constants for the Badge Reader integration."""

import logging # Added import

DOMAIN = "badgereader"
LOGGER = logging.getLogger(__name__) # Added LOGGER

# Configuration keys
CONF_NFC_UID = "nfc_uid"
CONF_READER_IP = "reader_ip"
CONF_READER_PORT = "reader_port"
CONF_READER_USERNAME = "reader_username"
CONF_READER_PASSWORD = "reader_password"
CONF_GOOGLE_SHEET_ID = "google_sheet_id"
CONF_GOOGLE_API_CREDENTIALS = "google_api_credentials"
CONF_EMAIL_RECIPIENTS = "email_recipients"
CONF_TARGET_WEEKLY_HOURS = "target_weekly_hours"
CONF_USUAL_WORK_DAYS = "usual_work_days"
CONF_PDF_OUTPUT_PATH = "pdf_output_path"
CONF_SPECIAL_HOURS_COLUMN = "special_hours_column"
CONF_TARGET_DAILY_HOURS_COLUMN = "target_daily_hours_column"
CONF_NET_CHANGE_COLUMN = "net_change_column"
CONF_RUNNING_BALANCE_COLUMN = "running_balance_column"
CONF_INITIAL_BALANCE = "initial_balance"

# Service names
SERVICE_GENERATE_MONTHLY_REPORT = "generate_monthly_report"

# Entity names
ENTITY_STATUS = "housekeeper_status"
ENTITY_LAST_CHECK_IN = "housekeeper_last_check_in"
ENTITY_LAST_CHECK_OUT = "housekeeper_last_check_out"
ENTITY_LAST_SHIFT_DURATION = "housekeeper_last_shift_duration"
ENTITY_HOURS_BALANCE = "housekeeper_hours_balance"
ENTITY_PRESENCE = "housekeeper_present"
ENTITY_READER_STATUS = "nfc_reader_status"

# Attributes
ATTR_HOURS_BALANCE = "hours_balance"
ATTR_LAST_CHECK_IN = "last_check_in"

# Data Update Coordinator constants
CONF_SCAN_INTERVAL = "scan_interval"
DEFAULT_SCAN_INTERVAL = 300 # Seconds (5 minutes) - Reader status check
READER_STATUS_INTERVAL = 60 # Added constant

# Webhook constants
WEBHOOK_ID = "badgereader_webhook"

# Default values
DEFAULT_READER_PORT = 80
DEFAULT_USUAL_WORK_DAYS = [0, 1, 2, 3, 4] # Changed to list (Mon-Fri)
DEFAULT_TARGET_WEEKLY_HOURS = 40.0 # Assuming a standard full-time work week
DEFAULT_PDF_OUTPUT_PATH = "/config/pdf_reports" # Added constant
DEFAULT_INITIAL_BALANCE = 0.0 # Added constant

# Reader API Endpoints
READER_API_SETLED = "/setled"
READER_API_UART1 = "/uart1"
READER_API_CHANGEHOST = "/changehost" # For configuring where the reader POSTs
READER_API_TOGGLEPOST = "/togglepost" # For enabling/disabling POSTing

# Reader LED Colors (Hex strings for /setled)
LED_COLOR_GREEN = "00FF00"
LED_COLOR_RED = "FF0000"
LED_COLOR_OFF = "000000"

# Home Assistant States
STATE_CHECKED_IN = "Checked In"
STATE_CHECKED_OUT = "Checked Out"
STATE_AWAY = "Away"
STATE_READER_OFFLINE = "Reader Offline"
STATE_ONLINE = "Online"
STATE_OFFLINE = "Offline"