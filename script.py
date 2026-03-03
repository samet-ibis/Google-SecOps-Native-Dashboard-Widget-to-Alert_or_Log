import requests
import json
from datetime import datetime, timedelta, timezone
from google.oauth2 import service_account
import google.auth.transport.requests as google_auth_requests

# --- SETTINGS (SENSITIVE VALUES) ---
CHART_ID = "YOUR_CHART_ID_HERE" #described on https://github.com/samet-ibis how to retrieve this
PROJECT_ID = "YOUR_PROJECT_ID_HERE"
INSTANCE_ID = "YOUR_INSTANCE_ID_HERE"
REGION = "YOUR_REGION_HERE"
CREDENTIALS_FILE = "/path/to/your/service_account.json" #
OUTPUT_FILE = "/path/to/your/output_log_file.txt"

class SecOpsAutomation:
    def __init__(self):
        self.base_url = f"https://{REGION}-chronicle.googleapis.com/v1alpha"
        self.creds = service_account.Credentials.from_service_account_file(
            CREDENTIALS_FILE, scopes=['https://www.googleapis.com/auth/cloud-platform']
        )

    def get_token(self):
        auth_req = google_auth_requests.Request()
        self.creds.refresh(auth_req)
        return self.creds.token

    def run(self):
        token = self.get_token()
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

        # 1. Fetch Dashboard and Query Information
        chart_url = f"{self.base_url}/projects/{PROJECT_ID}/locations/{REGION}/instances/{INSTANCE_ID}/dashboardCharts/{CHART_ID}"
        chart_data = requests.get(chart_url, headers=headers).json()
        
        query_path = chart_data.get("chartDatasource", {}).get("dashboardQuery")
        query_data = requests.get(f"{self.base_url}/{query_path}", headers=headers).json()
        actual_query = query_data.get("query")
        
        print(f"🔎 Query retrieved, scanning the last 24 hours...")

        # 2. Execute the Query
        execute_url = f"{self.base_url}/projects/{PROJECT_ID}/locations/{REGION}/instances/{INSTANCE_ID}/dashboardQueries:execute"
        now = datetime.now(timezone.utc)
        start = now - timedelta(days=1)
        
        payload = {
            "query": {"query": actual_query},
            "input": {
                "timeWindow": {
                    "startTime": start.strftime('%Y-%m-%dT%H:%M:%SZ'),
                    "endTime": now.strftime('%Y-%m-%dT%H:%M:%SZ')
                }
            }
        }

        response = requests.post(execute_url, headers=headers, json=payload)
        results_data = response.json()
        stats = results_data.get("results") or results_data.get("stats", {}).get("results", [])

        if not stats:
            print("⚠ No data found or API returned an empty result.")
            return

        device_names, array_col_data = [], []

        # 3. Data Parsing (Template Logic)
        for col in stats:
            col_name = col.get("column")
            values = col.get("values", [])

            # Mapping the 'device_name' column from your dashboard
            if col_name == "device_name":
                device_names = [v.get("value", {}).get("stringVal", "") for v in values]
            
            # Mapping the array column that contains 2 values that triggers our detection
            elif col_name == "your_array_column_name_that_contains_2_values":
                for v in values:
                    # Chronicle returns nested lists in a specific structure
                    inner_data = v.get("list", {}) if "list" in v else v.get("value", {}).get("list", {})
                    inner_vals = inner_data.get("values", [])
                    extracted_values = [item.get("stringVal") for item in inner_vals if item.get("stringVal")]
                    array_col_data.append(extracted_values)

        # 4. Local File Control and Logging
        existing_entries = set()
        try:
            with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
                for line in f:
                    parts = line.split(",")
                    if len(parts) >= 2:
                        existing_entries.add(parts[1].strip())
        except FileNotFoundError:
            pass

        match_count = 0
        new_added_count = 0
        current_ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
            for i in range(len(device_names)):
                d_name = device_names[i]
                d_array = array_col_data[i] if i < len(array_col_data) else []

                # APPLY BUSINESS LOGIC: Change "TRIGGER_VALUE" to your target value (e.g., "triggervalue1")
                if len(d_array) == 1 and d_array[0] == "TRIGGER_VALUE":
                    match_count += 1
                    if d_name not in existing_entries:
                        f.write(f"{current_ts}, {d_name}, action_triggered\n")
                        new_added_count += 1
                        existing_entries.add(d_name)

        print(f"📊 Scan Summary:")
        print(f"  - Total Matches Found: {match_count}")
        print(f"  - Newly Added to Local File: {new_added_count}")
        
        if new_added_count == 0:
            print("  - Your local list is already up to date.")

if __name__ == "__main__":
    SecOpsAutomation().run()
