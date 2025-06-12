# Home Assistant NFC Badge Reader & Time Keeping System

[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg)](https://github.com/custom-components/hacs)

This project provides a Home Assistant custom component that integrates a µFR Nano Online NFC reader with Home Assistant and Google Sheets for automated timekeeping, specifically designed for tracking housekeeper work hours.

Utilizing the µFR Nano Online's HTTP REST API, the system allows a housekeeper to clock in and out by simply tapping an NFC card to the reader. These events are processed by Home Assistant, automatically logged to a shared Google Sheet (which tracks a running hours balance), and can optionally trigger email notifications.

## Features

*   **Easy Clock In/Out:** Housekeeper taps an NFC card on the µFR Nano Online reader.
*   **Automated Time Logging:** Clock-in and clock-out times are automatically recorded.
*   **Google Sheets Integration:**
    *   Calculates shift duration.
    *   Appends data (Date, Times, Duration, Special Hours, Target Hours, Net Change, Running Balance) to a specified Google Sheet.
    *   Maintains a running hours balance against target hours.
*   **Optional Email Notifications:** Send an email summary of the shift (including hours balance) upon clock-out to configured recipients.
*   **Home Assistant Integration:**
    *   Provides sensors and binary sensors for housekeeper status (Checked In/Out/Away), last activity times, current hours balance, and reader status.
    *   Installable via HACS (Home Assistant Community Store).
*   **End-of-Month PDF Report:** Generate a detailed summary report of hours worked for a specific month, including targets and balance evolution.
*   **Utilizes Reader's HTTP REST API:** Simplifies setup by leveraging the reader's ability to POST card data to Home Assistant.
*   **Visual/Audible Feedback:** Configurable LED colors and attempts at buzzer control via the reader's API upon successful/failed scans.

## Requirements

*   A **Home Assistant** installation (OS, Supervised, or Core in Docker).
*   A **µFR Nano Online** NFC reader connected to your local Wi-Fi network.
*   A compatible **NFC Card** for the housekeeper (only the UID is needed).
*   A **Google Account** to set up Google Sheets API access.
*   An **SMTP server** for optional email notifications.
*   Home Assistant host and µFR Nano Online reader on the same local network.
*   The µFR Nano Online reader must be configured to send HTTP POST requests to a Home Assistant webhook URL upon card scans (see Configuration).

## Installation

This component is designed to be installed via **Home Assistant Community Store (HACS)**.

1.  **Add this repository to HACS:**
    *   In Home Assistant, navigate to HACS -> Integrations.
    *   Click the three dots in the top right corner and select "Custom repositories".
    *   Enter the URL of this GitHub repository.
    *   Select the category "Integration".
    *   Click "Add".
2.  **Install the integration:**
    *   Search for "NFC Badge Reader" or similar in the HACS Integrations list.
    *   Click on the integration and select "Download".
    *   Restart Home Assistant.

## Configuration

Configuration is done via `configuration.yaml` or potentially a Config Flow UI in the future.

1.  **Configure the µFR Nano Online Reader:**
    *   Access the reader's web interface.
    *   Configure Wi-Fi to connect to your local network. Assign a static IP address via DHCP reservation on your router or use a reliable mDNS hostname.
    *   Crucially, configure the reader to send an HTTP POST request to your Home Assistant webhook URL whenever a card is scanned. The specific configuration steps vary slightly depending on the reader's firmware, but typically involves setting a "Target Host" and enabling "POST on card scan". The payload should include the card's UID (often as JSON, e.g., `{"uid": "..."}`).
    *   You will get the Home Assistant webhook URL from the component's logs or UI once configured in HA.
    *   Note: The badging requests from the reader to Home Assistant are handled via this Home Assistant-managed webhook. The `ports: 5000/tcp: 5000` entry sometimes seen in `badgereader_addon/config.yaml` is for a different purpose (e.g., local development or direct API access to the addon if implemented) and is **not** used for receiving these badging requests from the reader.
2.  **Set up Google Sheets API:**
    *   Follow the Google Cloud documentation to enable the Google Sheets API and create a service account.
    *   Download the service account JSON key file.
    *   Share your Google Sheet with the email address of the service account.
3.  **Add configuration to `configuration.yaml`:**

