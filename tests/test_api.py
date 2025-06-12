import pytest
import aiohttp # Added for BasicAuth
from aioresponses import aioresponses

from custom_components.badgereader.api import UfrReaderApi # Changed import
# from custom_components.badgereader.api import attempt_buzzer_control # Commented out

READER_IP = "192.168.1.100"
READER_PORT = 80
READER_USERNAME = "test_user"
READER_PASSWORD = "test_password"


@pytest.mark.asyncio
async def test_set_led_success():
    """Test setting LED color successfully."""
    url = f"http://{READER_IP}:{READER_PORT}/setled"
    color_hex = "00FF00"  # Green
    auth = aiohttp.BasicAuth(READER_USERNAME, READER_PASSWORD)
    api = UfrReaderApi(READER_IP, READER_PORT, READER_USERNAME, READER_PASSWORD)

    with aioresponses() as m:
        m.post(url, status=200)

        await api.set_led(color_hex)
        expected_headers = {"Content-Type": "text/plain"}
        if api._auth_header:
            expected_headers.update(api._auth_header)
        m.assert_called_once_with(url, method="POST", data=color_hex, headers=expected_headers)
    await api.close_session()


@pytest.mark.asyncio
async def test_set_led_failure():
    """Test setting LED color with a non-200 response."""
    url = f"http://{READER_IP}:{READER_PORT}/setled"
    color_hex = "FF0000"  # Red
    auth = aiohttp.BasicAuth(READER_USERNAME, READER_PASSWORD)
    api = UfrReaderApi(READER_IP, READER_PORT, READER_USERNAME, READER_PASSWORD)

    with aioresponses() as m:
        m.post(url, status=401)

        with pytest.raises(Exception):  # Or a more specific exception
            await api.set_led(color_hex)
        expected_headers = {"Content-Type": "text/plain"}
        if api._auth_header:
            expected_headers.update(api._auth_header)
        m.assert_called_once_with(url, method="POST", data=color_hex, headers=expected_headers)
    await api.close_session()


# @pytest.mark.asyncio
# async def test_attempt_buzzer_control_success():
#     """Test attempting buzzer control via /uart1 successfully."""
#     url = f"http://{READER_IP}:{READER_PORT}/uart1"
#     command_hex = "AABBCCDD"  # Example command
#     api = UfrReaderApi(READER_IP, READER_PORT)

#     with aioresponses() as m:
#         m.post(url, status=200)

#         await api.send_uart_command(command_hex) # Assuming this is the intended replacement
#         m.assert_called_once_with(url, data=command_hex)
#     await api.close_session()


# @pytest.mark.asyncio
# async def test_attempt_buzzer_control_failure():
#     """Test attempting buzzer control via /uart1 with a non-200 response."""
#     url = f"http://{READER_IP}:{READER_PORT}/uart1"
#     command_hex = "AABBCCDD"  # Example command
#     api = UfrReaderApi(READER_IP, READER_PORT)

#     with aioresponses() as m:
#         m.post(url, status=500)

#         with pytest.raises(Exception):  # Or a more specific exception
#             await api.send_uart_command(command_hex) # Assuming this is the intended replacement
#         m.assert_called_once_with(url, data=command_hex)
#     await api.close_session()


# @pytest.mark.asyncio
# async def test_attempt_buzzer_control_connection_error():
#     """Test attempting buzzer control when the reader is unreachable."""
#     url = f"http://{READER_IP}:{READER_PORT}/uart1"
#     command_hex = "AABBCCDD"  # Example command
#     api = UfrReaderApi(READER_IP, READER_PORT)

#     with aioresponses() as m:
#         m.post(url, exception=aiohttp.ClientConnectorError(None, None))

#         # This test might need adjustment based on how UfrReaderApi handles ClientConnectorError
#         # For now, assume it might raise an exception or return a specific value.
#         # If send_uart_command raises the error, then the following is fine.
#         with pytest.raises(aiohttp.ClientError): # More specific error
#             await api.send_uart_command(command_hex)
#         m.assert_called_once_with(url, data=command_hex)
#     await api.close_session()