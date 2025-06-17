# Home Assistant NFC Badge Reader & Time Keeping System

This project provides a Home Assistant Add-on that integrates a µFR Nano Online NFC reader with Home Assistant and Google Sheets for automated timekeeping, specifically designed for tracking housekeeper work hours.

Utilizing the µFR Nano Online's HTTP REST API, the system allows a housekeeper to clock in and out by simply tapping an NFC card to the reader. These events are processed by Home Assistant, automatically logged to a shared Google Sheet (which tracks a running hours balance), and can optionally trigger email notifications.

## Features

*   **Easy Clock In/Out:** Housekeeper taps an NFC card on the µFR Nano Online reader.
*   **Automated Time Logging:** Clock-in and clock-out times are automatically recorded.
*   **Google Sheets Integration:**
    *   Calculates shift duration.
    *   Appends data (Date, Times, Duration, Special Hours, Target Hours, Net Change, Running Balance) to a specified Google Sheet.
    *   Maintains a running hours balance against target hours.
*   **Optional Email Notifications:** Send an email summary of the shift (including hours balance) upon clock-out to configured recipients.
*   **Provides Home Assistant Entities:** Offers sensors and binary sensors for housekeeper status (Checked In/Out/Away), last activity times, current hours balance, and reader status.
*   **End-of-Month PDF Report:** Generate a detailed summary report of hours worked for a specific month, including targets and balance evolution.
*   **Utilizes Reader's HTTP REST API:** Simplifies setup by leveraging the reader's ability to POST card data to Home Assistant.
*   **Visual/Audible Feedback:** Configurable LED colors and attempts at buzzer control via the reader's API upon successful/failed scans.

## Requirements

*   A **Home Assistant** installation running Home Assistant OS or Supervised.
*   A **µFR Nano Online** NFC reader connected to your local Wi-Fi network.
*   A compatible **NFC Card** for the housekeeper (only the UID is needed).
*   A **Google Account** to set up Google Sheets API access.
*   An **SMTP server** for optional email notifications.
*   Home Assistant host and µFR Nano Online reader on the same local network.
*   The µFR Nano Online reader must be configured to send HTTP POST requests to a Home Assistant webhook URL upon card scans (see Configuration).

## Add-on Installation

[![Open your Home Assistant instance and open the repository in the Supervisor Add-on Store.](https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg)](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2Ffischerq%2Fbadgereader-ha-addon)

1. Go to your Home Assistant instance.
2. In the sidebar, click on "Supervisor" (or "Settings" > "Add-ons" if Supervisor is not directly visible).
3. Click on the "Add-on store" button in the top right.
4. Click on the three dots in the top right corner and select "Repositories".
5. In the "Manage add-on repositories" dialog, paste the URL `https://github.com/fischerq/badgereader-ha-addon` and click "Add".
6. Close the dialog and refresh the page.
7. The "BadgeReader Add-on Repository" should now be visible in the Add-on store, and the "BadgeReader Add-on" should be available to install.

## Configuration

The add-on requires initial setup for the NFC reader and Google Sheets API. Further configuration options, if available, can typically be found within the add-on's "Configuration" tab in Home Assistant after installation.

1.  **Configure the µFR Nano Online Reader:**
    *   Access the reader's web interface.
    *   Configure Wi-Fi to connect to your local network. Assign a static IP address via DHCP reservation on your router or use a reliable mDNS hostname.
    *   Crucially, configure the reader to send an HTTP POST request to a specific URL (webhook) exposed by the add-on. Details on finding this URL will be available in the add-on's documentation or interface once the add-on is running. The payload should include the card's UID (often as JSON, e.g., `{"uid": "..."}`).
    *   Note: The badging requests from the reader to Home Assistant are handled via this add-on provided webhook. The `ports: 5000/tcp: 5000` entry sometimes seen in `badgereader_addon/config.yaml` is related to the add-on's internal web server and may not be directly accessible depending on your network configuration and the add-on's setup.
2.  **Set up Google Sheets API:**
    *   Follow the Google Cloud documentation to enable the Google Sheets API and create a service account.
    *   Download the service account JSON key file.
    *   Share your Google Sheet with the email address of the service account. This JSON key will be needed for the add-on's configuration.
