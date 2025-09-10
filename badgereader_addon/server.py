import logging
import os
import yaml
from datetime import datetime, timedelta
from aiohttp import web
from homeassistant_api import Client
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

PORT = 8199
ACCESS_KEY = "SolalindensteinBadgeReaderSecret"
HA_URL = "http://supervisor/core/api/"
HA_TOKEN = os.environ.get("SUPERVISOR_TOKEN")
VERSION = "unknown"
people = []
SWIPE_DEBOUNCE_MINUTES = 1
last_swipe_times = {}  # Stores the last swipe time for each UID
shift_state = {} # uid -> 'in'/'out'
shift_start_times = {} # uid -> datetime

# Google Sheets configuration
CREDS_FILE = '/share/google_credentials_solalindenstein_docs_user.json'
SPREADSHEET_URL = 'https://docs.google.com/spreadsheets/d/1KbvS_5aVuok2uCnqSCoU_5R7Wbu9M5F-MFGwTCCaWTA/edit'
WORKSHEET_NAME = 'Data'

def get_sheet():
    """Authenticates with Google Sheets and returns the worksheet."""
    try:
        client = gspread.service_account(filename=CREDS_FILE)
        spreadsheet = client.open_by_url(SPREADSHEET_URL)
        sheet = spreadsheet.worksheet(WORKSHEET_NAME)
        return sheet
    except Exception as e:
        logging.error(f"Error accessing Google Sheet: {e}", exc_info=True)
        return None

def log_swipe_to_sheet(person_name, action, timestamp):
    """Logs a badge swipe to the Google Sheet."""
    sheet = get_sheet()
    if sheet:
        try:
            row = [person_name, action, timestamp.strftime("%Y-%m-%d %H:%M:%S")]
            sheet.append_row(row)
            logging.info(f"Logged to Google Sheet: {row}")
        except Exception as e:
            logging.error(f"Error logging to Google Sheet: {e}", exc_info=True)

# Load config from config.yaml
try:
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
        options = config.get('options', {})
        people = options.get('people', [])
        SWIPE_DEBOUNCE_MINUTES = options.get('swipe_debounce_minutes', 1)
        VERSION = config.get('version', 'unknown')
except FileNotFoundError:
    logging.error("config.yaml not found. Please ensure it exists in the same directory.")
except yaml.YAMLError as e:
    logging.error(f"Error parsing config.yaml: {e}")

if people:
    logging.info(f"Loaded {len(people)} people from config: {[p.get('name') for p in people]}")
    logging.debug(f"Loaded UIDs: {[p.get('uid') for p in people]}")
    for person in people:
        person_uid = person.get('uid')
        if person_uid:
            sanitized_person_uid = str(person_uid).strip().lower()
            shift_state[sanitized_person_uid] = 'out'
else:
    logging.warning("No people configured in config.yaml or config file not found/invalid.")

logging.info(f"Swipe debounce time set to {SWIPE_DEBOUNCE_MINUTES} minute(s).")

async def send_notification(title, message):
    """Sends a notification using the Home Assistant notify service."""
    if not HA_TOKEN:
        logging.warning("SUPERVISOR_TOKEN not found, cannot send notification.")
        return

    domain = "notify"
    service = "quirin_niedernhuber_gmail_com"
    service_data = {
        'title': title,
        'message': message,
        'target': "quirin.niedernhuber@gmail.com" 
    }

    logging.info(f"Attempting to send notification. Domain: '{domain}', Service: '{service}', Data: {service_data}")

    try:
        async with Client(HA_URL, HA_TOKEN, use_async=True) as client:
            await client.async_trigger_service(domain, service, **service_data)
        logging.info(f"Successfully sent notification with title: '{title}'")
    except Exception as e:
        logging.error(f"Error sending notification: {e}", exc_info=True)

async def process_card_swipe(card_uid, data):
    """Processes a card swipe after the UID has been extracted."""
    # Sanitize the UID for comparison
    sanitized_card_uid = str(card_uid).strip().lower()

    # Check if the UID belongs to a known person
    for person in people:
        person_uid = person.get('uid')
        if not person_uid:
            continue

        sanitized_person_uid = str(person_uid).strip().lower()
        if sanitized_person_uid == sanitized_card_uid:
            # Check for multi-swipes
            now = datetime.now()
            last_swipe = last_swipe_times.get(sanitized_person_uid)

            if last_swipe:
                time_since_last_swipe = now - last_swipe
                if time_since_last_swipe < timedelta(minutes=SWIPE_DEBOUNCE_MINUTES):
                    logging.warning(
                        f"Ignoring duplicate swipe for {person['name']} ({sanitized_card_uid}). "
                        f"Last swipe was {time_since_last_swipe.total_seconds():.1f} seconds ago. "
                        f"Debounce is set to {SWIPE_DEBOUNCE_MINUTES} minute(s)."
                    )
                    return web.Response(text=f"Duplicate swipe for {person['name']}. Please wait.")
            
            # Update the last swipe time before processing
            last_swipe_times[sanitized_person_uid] = now

            logging.info(f"Recognized card for: {person['name']}")

            # Shift state logic
            current_state = shift_state.get(sanitized_person_uid, 'out')

            if current_state == 'out':
                shift_state[sanitized_person_uid] = 'in'
                shift_start_times[sanitized_person_uid] = now
                log_swipe_to_sheet(person['name'], 'in', now)
                await send_notification(
                    title='HA - Shift Started',
                    message=f"Hi from HA. {person['name']} just started their shift."
                )
                return web.Response(text=f"Welcome, {person['name']}. Your shift has started.")
            else: # current_state == 'in'
                shift_state[sanitized_person_uid] = 'out'
                start_time = shift_start_times.pop(sanitized_person_uid, now) 
                duration = now - start_time
                log_swipe_to_sheet(person['name'], 'out', now)
                await send_notification(
                    title='HA - Shift Ended',
                    message=f"Hi from HA. {person['name']} just ended their shift. Duration: {duration}."
                )
                return web.Response(text=f"Goodbye, {person['name']}. Your shift has ended.")

    logging.warning(f"Unrecognized card: {card_uid}. Full request data: {data}")
    # Add detailed log for debugging comparison
    known_uids_sanitized = [str(p.get('uid')).strip().lower() for p in people]
    logging.info(f"Comparing sanitized UID '{sanitized_card_uid}' with sanitized known UIDs: {known_uids_sanitized}")
    
    # Also notify on unrecognized card
    await send_notification(
        title='HA - Unrecognized Badge Scan',
        message=f"Unrecognized card swiped: {card_uid}"
    )

    raise web.HTTPUnauthorized(text="Unrecognized card")


async def handle_post(request):
    try:
        data = await request.post()

        # Check for access key in query string OR post body
        access_key = request.query.get('accessKey') or data.get('accessKey')

        if access_key != ACCESS_KEY:
            logging.warning(f"Unauthorized request from {request.remote}. URL query: '{request.query_string}'. POST data: {data}")
            raise web.HTTPUnauthorized(text="Unauthorized")

        card_uid = data.get("UID")

        if not card_uid:
            logging.warning(f"Received data with no 'UID' field: {data}")
            raise web.HTTPBadRequest(text="Missing 'UID' in payload")

        logging.info(f"Extracted card UID: {card_uid}")

        return await process_card_swipe(card_uid, data)

    except web.HTTPException:
        # Re-raise HTTP exceptions to be handled by aiohttp
        raise
    except Exception as e:
        logging.error(f"Error processing POST request: {e}", exc_info=True)
        raise web.HTTPInternalServerError(text="Internal server error")

async def handle_get(request):
    # Simple health check / status page
    html_response = '''
    <html>
        <head><title>Badge Reader Addon Server</title></head>
        <body>
            <h1>Badge Reader Addon HTTP Server</h1>
            <p>This server is running and listening for POST requests for badge data.</p>
        </body>
    </html>
    '''
    logging.info(f"Served GET request to {request.path} from {request.remote}")
    return web.Response(text=html_response, content_type='text/html')

app = web.Application()
app.add_routes([
    web.post('/', handle_post),
    web.get('/', handle_get),
])

if __name__ == "__main__":
    if not HA_TOKEN:
        logging.warning("SUPERVISOR_TOKEN environment variable not set. Home Assistant integration will be disabled.")
    
    # Check Google Sheet access
    logging.info("Checking Google Sheet access...")
    sheet = get_sheet()
    if sheet:
        try:
            cell_c1 = sheet.cell(1, 3).value # C1
            logging.info(f"Successfully accessed Google Sheet. Cell C1 contains: '{cell_c1}'")
        except Exception as e:
            logging.error(f"Error reading from Google Sheet: {e}")
    else:
        logging.error("Could not access Google Sheet.")

    logging.info(f"Hello from Badge Reader server, version {VERSION}")
    logging.info(f"Starting HTTP server for badge reader on port {PORT}...")
    logging.info(f"Server listening on 0.0.0.0:{PORT}")
    logging.info(f"Badge messages should be sent to http://<ADDON_IP_ADDRESS>:{PORT}/?accessKey={ACCESS_KEY}")
    web.run_app(app, host='0.0.0.0', port=PORT)
