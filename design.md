# **NFC Badge Reader & Time Keeping System \- Design Document**

Version: 1.7  
Date: May 30, 2025

## **1\. Introduction & Overview**

This document outlines the product and technical design for a system that transforms a µFR Nano Online NFC reader into a badge reader for tracking housekeeper working hours. The system will leverage the **µFR Nano Online's HTTP REST API** for communication. Specifically, the reader will be configured to **POST scanned card data to a Home Assistant endpoint**. This allows a housekeeper to clock in and out using an NFC card. These times will be automatically logged, used to update a shared Google Sheet (including a running hours balance), and optionally trigger email notifications. The system will integrate with Home Assistant as a custom component installable via HACS, exposing the housekeeper's status and relevant time information, and will include functionality for generating end-of-month summary reports.

## **2\. Product Design**

### **2.1. Goals**

* Enable easy and reliable clock-in/clock-out functionality for the housekeeper using an NFC card, understanding the reader may not be continuously powered.  
* Automate the recording of work hours.  
* Provide a transparent and shared record of hours worked via Google Sheets, including a running tally of hours balance against target hours.  
* Offer optional email notifications to the homeowner and housekeeper upon shift completion, including the current hours balance.  
* Integrate seamlessly with Home Assistant to display the housekeeper's current status, recent activity, and current hours balance.  
* Provide an end-of-month PDF summary of hours worked, target hours, special additions, and the overall hours balance, suitable for archiving.  
* Utilize the µFR Nano Online's HTTP REST API for all reader interactions, with the reader actively POSTing card data to Home Assistant, to simplify deployment and avoid native library dependencies.

### **2.2. User Stories**

#### **2.2.1. As a Housekeeper, I want to:**

* Tap my NFC card to the reader (when it's powered on) to clock in when I arrive.  
* Receive clear visual and audible feedback (e.g., green light, short beep) confirming successful clock-in.  
* Tap my NFC card to the reader to clock out when I depart.  
* Receive clear visual and audible feedback confirming successful clock-out.  
* Receive a copy of the end-of-shift email notification to confirm my hours were tracked correctly, including my current hours balance.  
* Be confident that my hours and hours balance are accurately recorded and accessible.  
* Have access to an end-of-month summary of my hours, including the hours balance.

#### **2.2.2. As a Homeowner, I want to:**

* Easily set up the system with a designated NFC card for the housekeeper.  
* Have the housekeeper's clock-in and clock-out times automatically and reliably logged when the reader is operational.  
* View the logged hours, calculated durations, special hour additions (e.g., sick days, vacation), and a running hours balance in a Google Sheet shared with the housekeeper.  
* Optionally receive an email notification (and have the housekeeper receive one) summarizing the hours worked and the current hours balance when the housekeeper clocks out.  
* See the housekeeper's current status (e.g., "Checked In," "Checked Out," "Away," "Reader Offline"), last check-in/out times, and current hours balance within my Home Assistant dashboard.  
* Ensure the system is robust and requires minimal maintenance, handling periods when the NFC reader might be powered off.  
* Generate an end-of-month PDF report summarizing total hours worked, comparing against target hours, including any specially logged hours, and showing the hours balance evolution for the month, for archival purposes.  
* Install and manage the integration easily via HACS.

### **2.3. Core Features**

* **NFC Card Reading (via HTTP API \- Reader POST):** The µFR Nano Online reader will be configured to send an HTTP POST request containing the scanned card's UID to an endpoint exposed by the Home Assistant custom component.  
* **Visual/Audible Feedback (via HTTP API):**  
  * Visual feedback (LEDs) will be controlled by the Home Assistant component sending HTTP POST requests to the reader's /setled endpoint.  
  * Audible feedback (buzzer) will be attempted. If not directly controllable via a dedicated REST call alongside /setled, the component may attempt to send specific low-level uFR commands (for ReaderUISignal) as a HEX string via the reader's /uart1 HTTP endpoint (if this endpoint can target the internal NFC module for such commands). If this is not feasible, feedback might be primarily visual.  
* **Time Logging:** Securely log precise timestamps for all check-in and check-out events.  
* **Google Sheets Integration:**  
  * Upon check-out, calculate the total duration of the work shift.  
  * Automatically append a new row to a specified Google Sheet. Columns to include:  
    * Date  
    * Check-in Time  
    * Check-out Time  
    * Shift Duration (Calculated)  
    * Special Hours Added/Subtracted (Manual Entry): For sick leave, vacation, agreed extra/fewer hours.  
    * Target Hours for Day (Calculated/Configurable): Derived from weekly target and usual work days.  
    * Net Change for Day (Calculated): Shift Duration \+ Special Hours \- Target Hours for Day.  
    * Running Hours Balance (Calculated): Previous Balance \+ Net Change for Day.  
* **Email Notification (Optional):**  
  * Upon check-out, send an email to configured recipient addresses.  
  * Email content: Date, Check-in Time, Check-out Time, Calculated Duration, and current Running Hours Balance.  
* **Home Assistant Integration (Custom Component for HACS):**  
  * The core logic will be packaged as a Home Assistant custom component, installable via HACS.  
  * Entities exposed:  
    * sensor.housekeeper\_status (States: "Checked In", "Checked Out", "Away", "Reader Offline")  
    * sensor.housekeeper\_last\_check\_in  
    * sensor.housekeeper\_last\_check\_out  
    * sensor.housekeeper\_last\_shift\_duration  
    * sensor.housekeeper\_hours\_balance (Reflects the latest Running Hours Balance from Google Sheet)  
    * binary\_sensor.housekeeper\_present  
    * binary\_sensor.nfc\_reader\_status (Online/Offline)  
  * Configuration will be managed via Home Assistant's configuration.yaml or through a Config Flow UI if developed.  
  * Service call to trigger end-of-month summary report (e.g., badgereader.generate\_monthly\_report).  
* **End-of-Month PDF Summary Report:**  
  * Manually triggerable via a Home Assistant service.  
  * Report for a specified month.  
  * **Content:**  
    * Report Period.  
    * Hours Balance at Start of Month.  
    * Total Hours Logged (from shifts in the month).  
    * Total Special Hours Added/Subtracted (in the month).  
    * Overall Actual Hours for Month.  
    * Target Hours for Month.  
    * Variance for Month.  
    * Hours Balance at End of Month.  
    * Brief overview/list of workdays and any special hour entries.  
  * **Output:** PDF file, saved to a configurable location accessible by Home Assistant (e.g., /config/www/badgereports/ or /share/) and/or emailed.

### **2.4. Assumptions**

* Home Assistant (Supervised, OS, or Core in Docker) installation capable of running custom components.  
* µFR Nano Online connected to Wi-Fi **when in use**.  
* Home Assistant host on the same network.  
* User can set up Google Cloud credentials.  
* Single NFC card for the housekeeper.  
* µFR Nano Online powered via Micro USB **during expected usage times**.  
* A baseline "Hours Balance" will be established.  
* User is familiar with installing custom components via HACS.  
* The µFR Nano Online reader can be reliably configured to:  
  * Automatically send an HTTP POST request containing at least the card UID to a specified URL (the Home Assistant webhook endpoint) upon successful card scan.  
  * The format of this POST request is known or discoverable (e.g., JSON with a 'uid' field).  
* The Home Assistant instance can receive incoming HTTP requests from the µFR Nano Online reader on its local network.

## **3\. Technical Design**

### **3.1. System Architecture**

graph TD  
    A\[NFC Card\] \-- Tap \--\> B(µFR Nano Online NFC Reader \- \*May be offline\*);  
    B \-- Wi-Fi (HTTP POSTs Card Data to HA) \--\> N\[Local Network\];  
    N \-- Wi-Fi/Ethernet \--\> C{Home Assistant Host};  
    C \-- Runs \--\> D\[HA Custom Component (Python)\];  
    D \-- HTTP Requests (e.g., to /setled) \--\> B;  
    B \-- HTTP POST (Card Data) \--\> D;  
    D \-- Interacts with \--\> E\[Home Assistant Core (Entities, Services)\];  
    E \-- Displays \--\> F\[HA Dashboard/Entities\];  
    D \-- Uses Google Sheets API \--\> G\[Google Sheet \- \*Tracks Running Balance\*\];  
    D \-- Uses SMTP/Email API \--\> H\[Email Service\];  
    H \-- Sends \--\> I\[Homeowner & Housekeeper Email \- \*Includes Balance\*\];  
    D \-- Uses PDF Lib \--\> J\[PDF Summary Report \- \*Includes Balance\*\];  
    E \-- Service Call Triggers \--\> D;

### **3.2. Hardware Components**

* **NFC Reader:** µFR Nano Online  
  * **Connectivity:** Wi-Fi (connected to the home's local area network).  
  * **Power:** Standard Micro USB power adapter (e.g., 5V/1A phone charger). **The reader will only be powered on when clock-in/out functionality is needed and may be unplugged at other times.**  
  * **IP Address:** Requires a static IP address (recommended via DHCP reservation on the router) or a reliable mDNS hostname for consistent communication with the Home Assistant component when online.  
* **NFC Card/Tag:** One compatible NFC card (e.g., NTAG213, NTAG215, NTAG216, or Mifare Ultralight). Only the card's UID is required.  
* **Home Assistant Host:** A device (e.g., Raspberry Pi, NUC, virtual machine) running Home Assistant OS or Home Assistant Supervised, connected to the same local network.

### **3.3. Software Components \- Home Assistant Custom Component (Python)**

* **Structure:** Standard Home Assistant custom component layout (e.g., custom\_components/badgereader/\_\_init\_\_.py, sensor.py, binary\_sensor.py, services.yaml, manifest.json).  
* **Main Python Logic (\_\_init\_\_.py, sensor.py, etc.):**  
  * **NFC Reader Interaction (µFR Nano Online via HTTP REST API):**  
    * **HTTP Client (for LED control):** Use Python's aiohttp library to send asynchronous HTTP POST requests to http://\<reader\_ip\>/setled with appropriate HEX color string payload and Basic Authentication.  
    * **Card UID Retrieval (Reader Pushes Data via HTTP POST):**  
      1. The HA custom component will register a **webhook endpoint** within Home Assistant (e.g., using async\_register\_webhook from homeassistant.components.webhook). This provides a unique, secure URL.  
      2. The µFR Nano Online reader must be configured (likely via its web interface or specific REST configuration calls like /changehost and /togglepost during a one-time setup phase) to send an HTTP POST request to this Home Assistant webhook URL whenever a card is scanned. The payload of this POST should contain the card's UID (e.g., as a JSON field {"uid": "ACTUAL\_UID"} or a simple form-encoded parameter).  
      3. The HA component's webhook handler will receive and process these incoming POST requests to extract the card UID.  
    * **Buzzer Control:** If the /setled endpoint does not also control the buzzer, and if direct buzzer control via a separate REST call is not available, the component will attempt to send the raw uFR ReaderUISignal command (as a HEX string) via the reader's /uart1 HTTP endpoint. This requires:  
      * Knowing the exact binary format of the ReaderUISignal command.  
      * Verification that the /uart1 endpoint can indeed relay commands to the internal NFC module in this manner.  
      * If this is not feasible or reliable, audible feedback might be omitted or rely on a different mechanism if available.  
    * **Connection Management & Error Handling (for LED control):**  
      * Handle HTTP request errors (timeouts, connection refused if reader is offline for LED control, authentication errors, non-200 responses).  
      * Update binary\_sensor.nfc\_reader\_status based on the ability to successfully send commands like /setled or based on a periodic health check if the reader offers a status endpoint. The primary indication of the reader being "online" for card scans will be the successful receipt of POSTs from it.  
  * **Configuration Handling:**  
    * Via configuration.yaml initially, with potential for Config Flow UI for easier setup.  
    * Parameters: Housekeeper's NFC card UID, reader IP/port, reader REST API username/password, Google Sheet ID, "Special Hours" column name, "Target Hours for Day" column name, "Net Change for Day" column name, "Running Hours Balance" column name, Google API credentials path, email settings, target weekly hours, usual work days, PDF output path.  
  * **Google Sheets API Integration (gspread library):**  
    * On "Check-out": Calculate and append all relevant data including the new Running Hours Balance.  
    * For monthly summary: Read data for the month.  
  * **Email Notification (Optional):**  
    * Include New Running Hours Balance.  
  * **Home Assistant Entity & Service Registration:**  
    * Define sensors (sensor.py), binary sensors (binary\_sensor.py).  
    * Register the badgereader.generate\_monthly\_report service.  
  * **Monthly Report Generation:**  
    * Logic as previously described. PDF generation using ReportLab or similar.

### **3.4. Data Flow (Check-in/Check-out Example \- HTTP API, Reader Pushes Data)**

1. **HA Component** is running and has registered a webhook endpoint (e.g., http://\<ha\_ip\>:\<port\>/api/webhook/unique\_webhook\_id).  
2. **µFR Nano Online Reader** is configured to POST to this HA webhook URL upon card scan.  
3. **Housekeeper taps NFC card.**  
4. **µFR Nano Online Reader** reads the card, then sends an HTTP POST request to the HA component's webhook URL. The payload contains the card data (e.g., {"uid": "CARD\_UID\_HERE"}).  
5. **HA Component's Webhook Handler:**  
   * Receives the POST request.  
   * Authenticates/validates the request if necessary (HA webhooks can be secured).  
   * Extracts the UID from the payload.  
   * Compares the UID with the configured housekeeper\_card\_UID.  
6. **If UID matches:**  
   * **Logic & HA Update:** As detailed in Version 1.2 (determine check-in/out, update HA entities via MQTT or state updates).  
   * **Feedback:** HA Component sends an HTTP POST to http://\<reader\_ip\>/setled for green light. Attempts buzzer control as described in 3.3.  
   * **If "Checked Out":** Update Google Sheets, send email (including hours balance).  
7. **If UID does NOT match:**  
   * HA Component sends an HTTP POST to http://\<reader\_ip\>/setled for red light. Attempts error buzzer.  
   * Log the unrecognized card UID.

### **3.5. Key REST API Endpoints Used (from µFR Nano Online)**

* **Reader \-\> Home Assistant:**  
  * (Assumed) Reader makes HTTP POST to HA-provided webhook URL (e.g., http://\<ha\_ip\>:\<port\>/api/webhook/some\_id) with card data (e.g., {"uid": "..."}). This is configured on the reader using its /togglepost and /changehost (or similar) REST endpoints or web UI.  
* **Home Assistant \-\> Reader:**  
  * POST http://\<reader\_ip\>/setled (Payload: HEX colors string; Auth: Basic) \- For LED feedback.  
  * POST http://\<reader\_ip\>/uart1 (Payload: HEX command string for ReaderUISignal; Auth: None) \- *Potentially* for buzzer control if /setled is insufficient and this method is viable.

### **3.6. Security Considerations**

* **NFC Card UID:** Sufficient for this application's convenience.  
* **Network Security:** Secure Wi-Fi (WPA2/WPA3). Firewall reader if no external access needed.  
* **API Credentials:** Store Google API credentials, email credentials, and reader HTTP API credentials securely (e.g., Home Assistant secrets).  
* **Webhook Security:** Home Assistant webhooks can be secured. For local network, risk is lower but good practice.

### **3.7. µFR Nano Online Specifics**

* **Initial Wi-Fi Configuration:** Done via Digital Logic tools/web UI.  
* **Static** IP / **Hostname:** Strongly recommended for the reader.  
* **Power:** Requires power during expected usage. Add-on must handle offline states.  
* **POST Configuration:** Critically important to configure the reader to POST card data to the HA webhook URL.

## **4\. Reporting**

### **4.1. End-of-Month PDF Summary**

* **Trigger:** Manual HA service call (e.g., badgereader.generate\_report with year, month).  
* **Data Source:** Primary Google Sheet.  
* **Process:**  
  1. Add-on receives service call.  
  2. Connects to Google Sheets.  
  3. Retrieves Running Hours Balance from the last entry *before* the start of the report month (this is "Balance at Start of Month"). If no prior entries, use an initial configured balance.  
  4. Retrieves all entries for the specified report month.  
  5. Sums Shift Duration for all shifts in the month ("Total Hours Logged").  
  6. Sums Special Hours Added/Subtracted for all entries in the month.  
  7. Calculates Overall Actual Hours for Month \= Total Hours Logged \+ Total Special Hours.  
  8. Sums Target Hours for Day for all relevant entries in the month to get "Target Hours for Month".  
  9. Calculates Variance for Month \= Overall Actual Hours for Month \- Target Hours for Month.  
  10. Retrieves Running Hours Balance from the last entry *of* the report month (this is "Balance at End of Month").  
  11. Generates PDF.  
  12. **PDF Content:**  
      * Report Period (e.g., "May 2025").  
      * Summary Table:  
        * Hours Balance at Start of Month: \+/- AA.AA hrs  
        * Total Hours Logged (from shifts): XX.XX hrs  
        * Total Special Hours Added/Subtracted: \+/- YY.YY hrs  
        * **Overall Actual Hours for Month:** ZZ.ZZ hrs  
        * Target Hours for Month: TT.TT hrs  
        * Variance for Month: \+/- VV.VV hrs  
        * **Hours Balance at End of Month:** \+/- BB.BB hrs  
      * Detailed Log (Optional): Date | Check-in | Check-out | Duration | Special Hours | Target for Day | Net Change | Running Balance  
  13. Saves PDF and optionally emails it.  
* **Configuration:**  
  * Target weekly hours & usual work days per week (for calculating Target Hours for Day).  
  * Names of relevant Google Sheet columns.  
  * Initial hours balance (if sheet is new).  
  * Output path for PDFs.

## **5\. Development & Deployment Considerations**

### **5.1. Implementation Language**

* Python 3, using aiohttp for asynchronous HTTP requests from Home Assistant (for controlling LEDs) and for handling incoming webhook requests.

### **5.2. Home Assistant Environment**

* Home Assistant Supervised (e.g., running in a VM on a Synology NAS). Also compatible with HA OS and HA Core where custom components are supported.

### **5.3. Distribution**

* Custom component via a **Git repository**, installable through the **Home Assistant Community Store (HACS)**.  
* Adherence to HACS repository structure and guidelines (e.g., hacs.json, versioning).

### **5.4. Unit Testing**

* **Comprehensive unit test coverage** using a Python testing framework like pytest.  
* Tests should cover:  
  * Core check-in/check-out logic.  
  * Hours balance calculations.  
  * Google Sheets data formatting and interaction (mocking gspread).  
  * Email content generation (mocking smtplib).  
  * PDF report data aggregation and generation (mocking PDF library outputs).  
  * Mocking HTTP responses for calls *to* the reader (e.g., /setled) using libraries like aioresponses or unittest.mock.patch.  
  * Testing the HA component's webhook handler for incoming POST requests *from* the reader.

### **5.5. Code Repository**

* The code will be maintained in a Git repository (e.g., on GitHub, GitLab), structured for HACS compatibility.

## **6\. Alternatives Considered**

### **6.1. Implementation Language for Home Assistant Component**

* **Python (Chosen):**  
  * **Pros:** Native for HA custom components, seamless integration, extensive libraries, simplifies HACS distribution.  
  * **Cons:** Potential performance concerns for very high-frequency tasks (not an issue here); GIL (component is I/O bound).  
* **Go (Golang):**  
  * **Pros:** Excellent performance, strong concurrency, static linking (more for Add-ons).  
  * **Cons for HA Custom Component:** Not native, complex integration with HA Python internals, steeper learning curve for HA context, HACS primarily Python. Better suited for HA Add-on model.  
* **Node.js / JavaScript:**  
  * **Pros:** Strong async I/O, large ecosystem.  
  * **Cons for HA Custom Component:** Similar to Go; not native, integration workarounds needed, likely separate process.  
* **Conclusion:** Python is the most practical and efficient choice for this HA custom component.

### **6.2. NFC Reader Communication Method**

Several methods for communication between the Home Assistant component and the µFR Nano Online reader were considered:

* **uFCoder Shared Library with ctypes (Considered then Discarded):**  
  * **Description:** This approach involved using the native libuFCoder.so shared library provided by Digital Logic, interfaced from Python using the ctypes module. Communication would occur over TCP/IP to the reader's IP address.  
  * **Pros:**  
    * Provides direct access to the full, comprehensive API of the uFR series readers.  
    * Potentially offers the most control over all reader features and diagnostics.  
  * **Cons:**  
    * **Complexity for HACS Distribution:** Requiring users to manually download and place the correct architecture-specific .so file (libuFCoder.so) for their Home Assistant host is a significant barrier to entry and makes HACS installation less straightforward. Managing different binaries for various platforms (amd64, aarch64, armv7l) within a HACS component is not standard practice.  
    * **Maintenance:** The Python ctypes wrapper would need to be maintained and kept in sync with the C library's header definitions.  
  * **Reason for Discarding:** The availability of an HTTP REST API on the µFR Nano Online, particularly the ability for the reader to POST card data to Home Assistant, presented a much simpler deployment path for a HACS custom component by **eliminating native library dependencies and the associated complexities**.  
* **HTTP REST API \- Reader POSTs Data (Chosen):**  
  * **Description:** The µFR Nano Online reader is configured to send an HTTP POST request containing the scanned card's UID directly to a webhook endpoint exposed by the Home Assistant custom component. Home Assistant then sends commands to the reader (e.g., for LED control) via separate HTTP POST requests to the reader's REST API.  
  * **Pros:**  
    * **Eliminates Native Library Dependencies:** No need for libuFCoder.so or ctypes, greatly simplifying installation via HACS and avoiding architecture-specific binary issues.  
    * **Event-Driven:** The reader pushes data to Home Assistant upon card scan, which is efficient.  
    * **Standard Protocols:** Uses HTTP, which is well-understood and easily implemented in Python using aiohttp.  
  * **Cons:**  
    * Dependent on the reader's HTTP API capabilities and reliable configuration for POSTing data.  
    * Buzzer control might be less direct if not explicitly supported by a simple REST call (potentially requiring use of the /uart1 passthrough).  
    * Less direct control over nuanced reader features compared to the full SDK, though not critical for this project's core requirements.  
* **HTTP REST API \- HA Polls Reader (Considered as Fallback):**  
  * **Description:** The Home Assistant component would periodically send HTTP requests to the reader to check for a card.  
  * **Pros:** Still avoids native libraries.  
  * **Cons:**  
    * Less efficient than the reader-push model (polling overhead).  
    * The provided µFR Nano Online REST API list did not show a direct "get card UID" polling endpoint. This would likely necessitate using the /uart1 endpoint to send raw uFR serial commands as HEX strings, which reintroduces some complexity of knowing the binary protocol (though still avoiding the .so file).  
  * **Reason for Not Choosing as Primary:** The reader-POSTs-data approach is more efficient and event-driven if the reader supports it reliably.

## **7\. Future Enhancements**

* Provide a clear, step-by-step setup guide for configuring the µFR Nano Online reader to POST data to the Home Assistant webhook, including screenshots from the reader's web UI if possible.  
* Implement a "test reader connection" service or button in HA that attempts to send a /setled command to verify IP and credentials for the reader.  
* Mechanism for manually adjusting the baseline "Running Hours Balance" in the Google Sheet if discrepancies arise or if a manual reset/correction is needed.  
* Option to automatically generate and email the monthly report on the 1st of the following month.  
* More detailed configuration for "workday" definition if needed for target hour calculations (e.g., specific days of the week).