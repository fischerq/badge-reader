import pytest
from aioresponses import aioresponses

from custom_components.badgereader.api import set_led, attempt_buzzer_control

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

    with aioresponses() as m:
        m.post(url, status=200)

        await set_led(
            READER_IP, READER_PORT, READER_USERNAME, READER_PASSWORD, color_hex
        )
        m.assert_called_once_with(url, data=color_hex, auth=auth)


@pytest.mark.asyncio
async def test_set_led_failure():
    """Test setting LED color with a non-200 response."""
    url = f"http://{READER_IP}:{READER_PORT}/setled"
    color_hex = "FF0000"  # Red
    auth = aiohttp.BasicAuth(READER_USERNAME, READER_PASSWORD)

    with aioresponses() as m:
        m.post(url, status=401)

        with pytest.raises(Exception):  # Or a more specific exception
            await set_led(
                READER_IP, READER_PORT, READER_USERNAME, READER_PASSWORD, color_hex
            )
        m.assert_called_once_with(url, data=color_hex, auth=auth)


@pytest.mark.asyncio
async def test_attempt_buzzer_control_success():
    """Test attempting buzzer control via /uart1 successfully."""
    url = f"http://{READER_IP}:{READER_PORT}/uart1"
    command_hex = "AABBCCDD"  # Example command

    with aioresponses() as m:
        m.post(url, status=200)

        await attempt_buzzer_control(READER_IP, READER_PORT, command_hex)
        m.assert_called_once_with(url, data=command_hex)


@pytest.mark.asyncio
async def test_attempt_buzzer_control_failure():
    """Test attempting buzzer control via /uart1 with a non-200 response."""
    url = f"http://{READER_IP}:{READER_PORT}/uart1"
    command_hex = "AABBCCDD"  # Example command

    with aioresponses() as m:
        m.post(url, status=500)

        with pytest.raises(Exception):  # Or a more specific exception
            await attempt_buzzer_control(READER_IP, READER_PORT, command_hex)
        m.assert_called_once_with(url, data=command_hex)


@pytest.mark.asyncio
async def test_attempt_buzzer_control_connection_error():
    """Test attempting buzzer control when the reader is unreachable."""
    url = f"http://{READER_IP}:{READER_PORT}/uart1"
    command_hex = "AABBCCDD"  # Example command

    with aioresponses() as m:
        m.post(url, exception=aiohttp.ClientConnectorError(None, None))

        await attempt_buzzer_control(READER_IP, READER_PORT, command_hex)
        m.assert_called_once_with(url, data=command_hex)