"""API for interacting with the µFR Nano Online NFC reader."""

import aiohttp
import base64
import logging

_LOGGER = logging.getLogger(__name__)

class UfrReaderApi:
    """API client for the µFR Nano Online reader."""

    def __init__(self, host: str, port: int, username: str = None, password: str = None):
        """Initialize the API client."""
        self._base_url = f"http://{host}:{port}"
        self._auth_header = None
        if username and password:
            auth_string = f"{username}:{password}"
            self._auth_header = {
                "Authorization": "Basic " + base64.b64encode(auth_string.encode()).decode()
            }
        self._session = None

    async def _get_session(self):
        """Get or create an aiohttp client session."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def set_led(self, hex_color: str):
        """Set the reader LED color."""
        url = f"{self._base_url}/setled"
        payload = hex_color
        headers = {"Content-Type": "text/plain"}
        if self._auth_header:
            headers.update(self._auth_header)

        try:
            session = await self._get_session()
            async with session.post(url, data=payload, headers=headers) as response:
                response.raise_for_status()
                _LOGGER.debug(f"Set LED to {hex_color}. Status: {response.status}")
        except aiohttp.ClientError as err:
            _LOGGER.error(f"Error setting LED to {hex_color}: {err}")
            raise

    async def send_uart_command(self, hex_command: str):
        """Send a raw command as a HEX string via the /uart1 endpoint."""
        url = f"{self._base_url}/uart1"
        payload = hex_command
        headers = {"Content-Type": "text/plain"}
        if self._auth_header:
            headers.update(self._auth_header)

        try:
            session = await self._get_session()
            async with session.post(url, data=payload, headers=headers) as response:
                response.raise_for_status()
                # The response might contain the reader's response via UART
                response_text = await response.text()
                _LOGGER.debug(f"Sent UART command {hex_command}. Status: {response.status}, Response: {response_text}")
                return response_text
        except aiohttp.ClientError as err:
            _LOGGER.error(f"Error sending UART command {hex_command}: {err}")
            raise

    async def close_session(self):
        """Close the aiohttp client session."""
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None

    # Placeholder for potential future methods, e.g., getting reader status
    # async def get_status(self):
    #     """Get reader status (if a status endpoint exists)."""
    #     url = f"{self._base_url}/status" # Example endpoint, verify actual API
    #     headers = {}
    #     if self._auth_header:
    #          headers.update(self._auth_header)
    #     try:
    #         session = await self._get_session()
    #         async with session.get(url, headers=headers) as response:
    #             response.raise_for_status()
    #             return await response.json() # Or response.text()
    #     except aiohttp.ClientError as err:
    #         _LOGGER.error(f"Error getting reader status: {err}")
    #         return None