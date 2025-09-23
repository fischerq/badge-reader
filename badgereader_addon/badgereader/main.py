import datetime
import json
import logging
import os

from aiohttp import web
from datetime import datetime, timedelta

from .config import Config
from .storage import GoogleSheetStorage, FileStorage
from .state_manager import StateManager
from .notification import (
    send_shift_start_notification,
    send_shift_end_notification,
    send_unrecognized_card_notification,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# --- Global constants and objects ---
PORT = 8199
ACCESS_KEY = "SolalindensteinBadgeReaderSecret"
HA_URL = "http://supervisor/core/api/"
HA_TOKEN = os.environ.get("SUPERVISOR_TOKEN")

# Load configuration
config = Config()

# Initialize storage backend
if config.storage_backend == "google_sheets":
    storage = GoogleSheetStorage(config)
elif config.storage_backend == "file":
    storage = FileStorage(config)
else:
    raise ValueError(f"Invalid storage backend: {config.storage_backend}")

# Initialize state manager
state_manager = StateManager(config, storage)

logging.info(f"Loaded {len(config.badges)} badges and {len(config.people)} people.")
logging.info(f"Notification emails: {config.notification_emails}")
logging.info(f"Swipe debounce time set to {config.swipe_debounce_minutes} minute(s).")
logging.info(f"Swipe time buffer set to {config.swipe_time_buffer_minutes} minute(s).")


async def process_card_swipe(card_uid, data):
    """Processes a card swipe after the UID has been extracted."""
    sanitized_card_uid = str(card_uid).strip().lower()

    if sanitized_card_uid in config.badge_map:
        people_id = config.badge_map[sanitized_card_uid]
        person = config.people_map.get(people_id)

        if not person:
            logging.error(
                f"Badge with UID {sanitized_card_uid} is mapped to a non-existent person with ID {people_id}"
            )
            return web.HTTPInternalServerError(
                text="Internal server error - bad configuration"
            )

        person_name = person["name"]
        now = datetime.now()

        # Check for multi-swipes
        if state_manager.is_swipe_debounced(sanitized_card_uid, now):
            return web.Response(text=f"Duplicate swipe for {person_name}. Please wait.")

        unix_timestamp = int(now.timestamp())
        logging.info(f"Recognized card for: {person_name}")

        new_state, action, duration_str = state_manager.handle_swipe(
            sanitized_card_uid, people_id, now
        )

        storage.log_swipe(unix_timestamp, sanitized_card_uid, json.dumps(action))

        if new_state == "in":
            await send_shift_start_notification(config, HA_URL, HA_TOKEN, person)
            return web.Response(text=f"Welcome, {person_name}. Your shift has started.")
        else:  # new_state == 'out'
            storage.register_shift(action)
            await send_shift_end_notification(
                config, HA_URL, HA_TOKEN, person, duration_str
            )
            return web.Response(text=f"Goodbye, {person_name}. Your shift has ended.")

    else:
        logging.warning(f"Unrecognized card: {card_uid}. Full request data: {data}")
        await send_unrecognized_card_notification(config, HA_URL, HA_TOKEN, card_uid)
        raise web.HTTPUnauthorized(text="Unrecognized card")


async def handle_post(request):
    try:
        data = await request.post()
        access_key = request.query.get("accessKey") or data.get("accessKey")

        if access_key != ACCESS_KEY:
            logging.warning(
                f"Unauthorized request from {request.remote}. URL query: '{request.query_string}'. POST data: {data}"
            )
            raise web.HTTPUnauthorized(text="Unauthorized")

        card_uid = data.get("UID")
        if not card_uid:
            logging.warning(f"Received data with no 'UID' field: {data}")
            raise web.HTTPBadRequest(text="Missing 'UID' in payload")

        logging.info(f"Extracted card UID: {card_uid}")
        return await process_card_swipe(card_uid, data)

    except web.HTTPException as e:
        raise e
    except Exception as e:
        logging.error(f"Error processing POST request: {e}", exc_info=True)
        raise web.HTTPInternalServerError(text="Internal server error")


async def handle_get(request):
    html_response = """
    <html>
        <head><title>Badge Reader Addon Server</title></head>
        <body>
            <h1>Badge Reader Addon HTTP Server</h1>
            <p>This server is running and listening for POST requests for badge data.</p>
        </body>
    </html>
    """
    logging.info(f"Served GET request to {request.path} from {request.remote}")
    return web.Response(text=html_response, content_type="text/html")


app = web.Application()
app.add_routes(
    [
        web.post("/", handle_post),
        web.get("/", handle_get),
    ]
)

if __name__ == "__main__":
    if not HA_TOKEN:
        logging.warning(
            "SUPERVISOR_TOKEN environment variable not set. Home Assistant integration will be disabled."
        )

    # --- Debugging: Log directory contents ---
    logging.info("--- Logging /share directory contents ---")
    share_path = "/share"
    try:
        share_contents = os.listdir(share_path)
        logging.info(f"Contents of {share_path}: {share_contents}")

        badge_reader_mount_path = "/share/badge-reader-mount"
        if os.path.exists(badge_reader_mount_path):
            badge_reader_mount_contents = os.listdir(badge_reader_mount_path)
            logging.info(f"Contents of {badge_reader_mount_path}: {badge_reader_mount_contents}")
        else:
            logging.warning(f"Directory not found: {badge_reader_mount_path}")
            
        test_file_path = "/share/badge-reader-mount/testfile.txt"
        if os.path.exists(test_file_path):
            with open(test_file_path) as f:
                logging.info(f"Contents of {test_file_path}:\n{f.read()}")
        else:
            logging.warning(f"File not found: {test_file_path}")

    except Exception as e:
        logging.error(f"Error listing directory contents: {e}", exc_info=True)
    logging.info("--- End of directory logging ---")
    # --- End Debugging ---

    storage.check()
    state_manager.initialize_states()

    logging.info(f"Hello from Badge Reader server, version {config.version}")
    logging.info(f"Starting HTTP server for badge reader on port {PORT}...")
    logging.info(f"Server listening on 0.0.0.0:{PORT}")
    logging.info(
        f"Badge messages should be sent to http://<ADDON_IP_ADDRESS>:{PORT}/?accessKey={ACCESS_KEY}"
    )
    web.run_app(app, host="0.0.0.0", port=PORT)
