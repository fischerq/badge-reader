import http.server
import socketserver
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

PORT = 5000

class BadgeRequestHandler(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)

        logging.info("Received POST request to %s from %s", self.path, self.client_address[0])
        logging.debug("Headers:\n%s", str(self.headers).strip())

        response_code = 200
        response_message = "POST request processed."

        try:
            decoded_data = post_data.decode('utf-8')
            logging.debug("Raw Body:\n%s", decoded_data)

            # Attempt to parse as JSON, similar to handle_webhook
            import json
            try:
                data = json.loads(decoded_data)
                card_uid = data.get("uid")

                if not card_uid:
                    logging.warning("Received data with no 'uid' field: %s", data)
                    response_code = 400
                    response_message = "Missing 'uid' in payload"
                else:
                    logging.info("Extracted card UID: %s", card_uid)

                    # Placeholder for comparing with a configured UID
                    # This would typically come from add-on options / environment variables
                    # Example: configured_uid = os.environ.get("NFC_CARD_UID_TO_MATCH")
                    # if configured_uid and card_uid == configured_uid:
                    #     logging.info("Recognized card: %s", card_uid)
                    #     response_message = "Card recognized"
                    # elif configured_uid:
                    #     logging.warning("Unrecognized card: %s (expected %s)", card_uid, configured_uid)
                    #     response_message = "Unrecognized card"
                    #     response_code = 401 # Unauthorized
                    # else:
                    #     # No specific UID configured to match, just acknowledging receipt
                    #     response_message = "Card UID received"
                    #     pass

            except json.JSONDecodeError:
                logging.error("Received invalid JSON data. Body was: %s", decoded_data)
                response_code = 400
                response_message = "Invalid JSON"

        except UnicodeDecodeError:
            logging.warning("Could not decode POST data as UTF-8. Logging raw bytes.")
            logging.debug("Body (raw bytes):\n%s", post_data)
            response_code = 400
            response_message = "Invalid data encoding, expected UTF-8"
        except Exception as e:
            logging.error("Error processing POST request: %s", e, exc_info=True)
            response_code = 500
            response_message = "Internal server error"

        self.send_response(response_code)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(response_message.encode('utf-8'))

    def do_GET(self):
        # Simple health check / status page
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        html_response = """
        <html>
            <head><title>Badge Reader Addon Server</title></head>
            <body>
                <h1>Badge Reader Addon HTTP Server</h1>
                <p>This server is running and listening for POST requests for badge data.</p>
            </body>
        </html>
        """
        self.wfile.write(html_response.encode('utf-8'))
        logging.info(f"Served GET request to {self.path} from {self.client_address[0]}")


if __name__ == "__main__":
    # Get port from environment variable if available, otherwise default to PORT
    # In Home Assistant add-ons, options are often passed as environment variables.
    # However, for the listening port *inside* the container, it's often fixed
    # and mapped in config.yaml. We'll use the fixed PORT 5000 here as identified.

    listen_port = PORT # Fixed internal port

    with socketserver.TCPServer(("", listen_port), BadgeRequestHandler) as httpd:
        logging.info(f"Starting HTTP server for badge reader on port {listen_port}...")
        # To get the container's IP is not straightforward from within Python easily.
        # The important part is that it's listening on 0.0.0.0 (all interfaces) inside the container.
        # The URL to be used externally would depend on the Docker networking and HA setup.
        # We can log that it's listening on the specified port.
        logging.info(f"Server listening on 0.0.0.0:{listen_port}")
        logging.info(f"Badge messages should be sent to http://<ADDON_IP_ADDRESS>:{listen_port}/")
        httpd.serve_forever()
