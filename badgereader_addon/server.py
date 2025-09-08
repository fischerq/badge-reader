import logging
import os
import yaml
from aiohttp import web
from homeassistant_api import Client

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

PORT = 8199
ACCESS_KEY = "SolalindensteinBadgeReaderSecret"
HA_URL = "http://supervisor/core/api/"
HA_TOKEN = os.environ.get("SUPERVISOR_TOKEN")
VERSION = "unknown"
people = []

# Load config from config.yaml
try:
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
        people = config.get('options', {}).get('people', [])
        VERSION = config.get('version', 'unknown')
except FileNotFoundError:
    logging.error("config.yaml not found. Please ensure it exists in the same directory.")
except yaml.YAMLError as e:
    logging.error(f"Error parsing config.yaml: {e}")

if people:
    logging.info(f"Loaded {len(people)} people from config: {[p.get('name') for p in people]}")
    logging.debug(f"Loaded UIDs: {[p.get('uid') for p in people]}")
else:
    logging.warning("No people configured in config.yaml or config file not found/invalid.")

async def send_notification(title, message):
    """Sends a notification using the Home Assistant notify service."""
    if not HA_TOKEN:
        logging.warning("SUPERVISOR_TOKEN not found, cannot send notification.")
        return

    try:
        async with Client(HA_URL, HA_TOKEN, use_async=True) as client:
            await client.async_trigger_service(
                'quirin_niedernhuber_gmail_com', 'notify',
                service_data={
                    'title': title,
                    'message': message,
                    'target': 'quirin.niedernhuber@gmail.com'
                }
            )
        logging.info(f"Successfully sent notification with title: '{title}'")
    except Exception as e:
        logging.error(f"Error sending notification: {e}")

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
            logging.info(f"Recognized card for: {person['name']}")
            
            await send_notification(
                title='HA - Badge Scan',
                message=f"Hi from HA. {person['name']} just swiped their badge."
            )
            
            return web.Response(text=f"Welcome, {person['name']}")

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
    logging.info(f"Hello from Badge Reader server, version {VERSION}")
    logging.info(f"Starting HTTP server for badge reader on port {PORT}...")
    logging.info(f"Server listening on 0.0.0.0:{PORT}")
    logging.info(f"Badge messages should be sent to http://<ADDON_IP_ADDRESS>:{PORT}/?accessKey={ACCESS_KEY}")
    web.run_app(app, host='0.0.0.0', port=PORT)
