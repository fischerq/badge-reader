import logging
from homeassistant_api import Client


async def _send_notification(config, ha_url, ha_token, title, message, person=None):
    """Sends a notification using the Home Assistant notify service."""
    if not ha_token:
        logging.warning("SUPERVISOR_TOKEN not found, cannot send notification.")
        return

    if person and person.get("email"):
        primary_recipients = [person["email"]]
        cc_recipients = [
            email for email in config.notification_emails if email != person["email"]
        ]
    else:
        primary_recipients = config.notification_emails
        cc_recipients = []

    if not primary_recipients:
        logging.warning("No recipients found for notification.")
        return

    service_data = {"title": title, "message": message, "target": primary_recipients}

    if cc_recipients:
        service_data["data"] = {"cc": cc_recipients}

    logging.info(
        f"Attempting to send notification to {primary_recipients} (CC: {cc_recipients}). "
        f"Domain: '{config.notification_domain}', Service: '{config.notification_service}', Data: {service_data}"
    )

    try:
        async with Client(ha_url, ha_token, use_async=True) as client:
            await client.async_trigger_service(
                config.notification_domain, config.notification_service, **service_data
            )
        logging.info(
            f"Successfully sent notification with title: '{title}' to {primary_recipients}"
        )
    except Exception as e:
        logging.error(
            f"Error sending notification to {primary_recipients}: {e}", exc_info=True
        )


async def send_shift_start_notification(config, ha_url, ha_token, person):
    """Sends a notification when a shift starts."""
    person_name = person["name"]
    title = f"{person_name} - Schicht gestartet"
    message = f"Hallo {person_name}, deine Schicht hat gerade begonnen. Einen schönen und produktiven Tag!"
    await _send_notification(config, ha_url, ha_token, title, message, person)


async def send_shift_end_notification(config, ha_url, ha_token, person, duration_str):
    """Sends a notification when a shift ends."""
    person_name = person["name"]
    title = f"{person_name} - Schicht beendet"
    message = f"Hallo {person_name}, deine Schicht ist nun zu Ende. Deine heutige Arbeitszeit betrug {duration_str}."
    message += " Wir wünschen dir einen schönen Feierabend!"
    await _send_notification(config, ha_url, ha_token, title, message, person)


async def send_unrecognized_card_notification(config, ha_url, ha_token, card_uid):
    """Sends a notification for an unrecognized card."""
    title = "Unbekannter Badge gescannt"
    message = (
        f"Hallo, gerade wurde ein unbekannter Badge mit der UID {card_uid} gescannt."
    )
    await _send_notification(config, ha_url, ha_token, title, message)
