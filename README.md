# Google-SecOps-Native-Dashboard-Widget-to-Alert_or_Log
<img width="900" height="443" alt="image" src="https://github.com/user-attachments/assets/89bddb9e-14e2-4ade-962d-bda4c49a441f" />

This repository provides a Python-based automation script to transform static **Google SecOps (Chronicle)** Native Dashboard widgets into actionable security alerts or logs. By programmatically "scraping" the data/statics behind your visuals, you can move from passive monitoring to automated, stateful detection.

## 🚀 The Problem & Solution

Monitoring security metrics through a UI is a great start, but human eyes cannot be on every widget 24/7. This script allows you to monitor a specific column within a Native Dashboard widget for two predefined values. If the column contains only **one** of those values (the target trigger), the script automatically writes the entire row to a local file.

By pulling data locally, you can:

* **Generate Alerts:** Send log entries to SecOps via BindPlane or Ingestion scripts.
* **Custom Scheduling:** Create email reports that fit your team's specific SLA requirements.

---

## 📖 Overview & Workflow

1. **Authenticate:** Connect to the Google Chronicle API creating/using a Service Account.
2. **Metadata Fetch:** Retrieve the specific Chart ID for the widget you created on the Native Dashboard. We will use the query defined on this widget.
3. **Execute:** Run that query locally within a defined time window (e.g., last 24 hours).
4. **Parse & Filter:** Analyze array-based columns to find assets with specific logging gaps or insecure configurations.
5. **Deduplicate:** Only log newly discovered matches to prevent alert fatigue.

---

## 🛠️ Example - Technical Use Cases

* **Endpoint Coverage Audit:** Identify "Unprotected Assets" by scanning for devices sending network traffic that are missing from the "EDR/Antivirus Agent Installed" column.
* **Shadow Service Discovery:** Detect "Insecure Exposure" by filtering network scan dashboards for devices where an array column (like open ports) contains unauthorized values like `Telnet`, `RDP`, or `FTP`.
* **Logging Compliance:** Monitor for devices that appear in asset lists but lack critical log types in their metadata arrays.

---

## ⚙️ Configuration

Replace the placeholders in the `# --- SETTINGS ---` section:

| Variable | Description |
| --- | --- |
| `CHART_ID` | The unique ID of the dashboard widget (find it in the browser URL or API). |
| `PROJECT_ID` | Your Google Cloud Project ID. |
| `INSTANCE_ID` | Your Google Chronicle Instance ID. |
| `REGION` | The region of your Chronicle instance (e.g., `us`, `europe`). |
| `CREDENTIALS_FILE` | Path to your Service Account JSON key. Service Account with access to Native Dashboards|
| `OUTPUT_FILE` | Local path for the `.txt` or `.log` file output. |

🛠️ How to Find the Chart ID

To retrieve the specific Chart ID required for the script, follow these steps:
- Navigate to Dashboards -> Native Dashboards in your Google SecOps console.
- Click Edit on the dashboard containing your target widget.
- Click the Edit icon on the specific widget (chart).
- Copy the chartId value directly from your browser's URL address bar.
Example URL:
https://yourinstance-region.backstory.chronicle.security/dashboards-v2/customerid/edit?chartId=1234567-aa9d-4cf9-86cb-945983123123

---
