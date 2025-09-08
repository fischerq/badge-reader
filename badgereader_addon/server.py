import logging
import os
import yaml
from aiohttp import web
from homeassistant_api import Client

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

PORT = 8199
ACCESS_KEY = "SecretTTCReader81243"
HA_URL = "http://supervisor/core/api/"
HA_TOKEN = os.environ.get("SUPERVISOR_TOKEN")

# Load people from config.yaml
try:
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
        people = config.get('options', {}).get('people', [])
except FileNotFoundError:
    logging.error("config.yaml not found. Please ensure it exists in the same directory.")
    people = []
except yaml.YAMLError as e:
    logging.error(f"Error parsing config.yaml: {e}")
    people = []

async def handle_post(request):
    # Check for access key
    if request.query.get('accessKey') != ACCESS_KEY:
        logging.warning("Unauthorized request from %s", request.remote)
        raise web.HTTPUnauthorized(text="Unauthorized")

    # The data is URL-encoded
    try:
        data = await request.post()
        card_uid = data.get("UID")

        if not card_uid:
            logging.warning("Received data with no 'UID' field: %s", data)
            raise web.HTTPBadRequest(text="Missing 'UID' in payload")

        logging.info("Extracted card UID: %s", card_uid)

        # Check if the UID belongs to a known person
        for person in people:
            if person['uid'] == card_uid:
                logging.info("Recognized card for: %s", person['name'])
                
                # Trigger Home Assistant action
                try:
                    if HA_TOKEN:
                        async with Client(HA_URL, HA_TOKEN, use_async=True) as client:
                            await client.async_trigger_service(
                                'notify', 'quirin_niedernhuber_gmail_com',
                                service_data={
                                    'message': f"Hi from HA. {person['name']} just swiped their badge.",
                                    'title': 'HA - Badge Scan',
                                    'target': 'quirin.niedernhuber@gmail.com'
                                }
                            )
                        logging.info("Successfully triggered Home Assistant action.")
                    else:
                        logging.warning("SUPERVISOR_TOKEN not found, cannot trigger Home Assistant action.")
                except Exception as e:
                    logging.error(f"Error triggering Home Assistant action: {e}")
                    # Log the error but continue, so the badge reader gets a success response
                
                return web.Response(text=f"Welcome, {person['name']}")

        logging.warning("Unrecognized card: %s", card_uid)
        # Also notify on unrecognized card
        try:
            if HA_TOKEN:
                async with Client(HA_URL, HA_TOKEN, use_async=True) as client:
                    await client.async_trigger_service(
                        'notify', 'quirin_niedernhuber_gmail_com',
                        service_data={
                            'message': f"Unrecognized card swiped: {card_uid}",
                            'title': 'HA - Unrecognized Badge Scan',
                            'target': 'quirin.niedernhuber@gmail.com'
                        }
                    )
                logging.info("Successfully triggered Home Assistant action for unrecognized card.")
            else:
                logging.warning("SUPERVISOR_TOKEN not found, cannot trigger Home Assistant action for unrecognized card.")
        except Exception as e:
            logging.error(f"Error triggering Home Assistant action for unrecognized card: {e}")

        raise web.HTTPUnauthorized(text="Unrecognized card")

    except Exception as e:
        logging.error("Error processing POST request: %s", e, exc_info=True)
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
    logging.info(f"Hello from Badge Reader server")
    logging.info(f"Starting HTTP server for badge reader on port {PORT}...")
    logging.info(f"Server listening on 0.0.0.0:{PORT}")
    logging.info(f"Badge messages should be sent to http://<ADDON_IP_ADDRESS>:{PORT}/?accessKey=SecretTTCReader81243")
    web.run_app(app, host='0.0.0.0', port=PORT)
