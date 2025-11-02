from flask import Flask, request, jsonify
import requests
from datetime import datetime
import os
from dotenv import load_dotenv

# ======================
# Load Configurations
# ======================
load_dotenv()

TENANT_ID = os.getenv("TENANT_ID")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
GROUP_ID = os.getenv("GROUP_ID")          # Power BI Workspace ID
DATASET_ID = os.getenv("DATASET_ID")      # Power BI Dataset ID
TABLE_NAME = os.getenv("TABLE_NAME", "VacationData")  # Power BI Table Name

# ======================
# Initialize Flask App
# ======================
app = Flask(__name__)

@app.route("/")
def home():
    return "🌴 Vacation Planner Power BI API is live!"

# ======================
# Vacation Planner Endpoint
# ======================
@app.route("/vacation-data", methods=["POST"])
def push_vacation_data():
    """
    Receives structured vacation itinerary data from the GPT Action,
    validates it, and pushes it to Power BI via the REST API.
    """
    try:
        itinerary = request.get_json()

        # 1️⃣ Validate input format
        if not isinstance(itinerary, list):
            return jsonify({"error": "Expected a list of itinerary objects"}), 400

        required_fields = {"day", "location", "activity", "cost"}
        for entry in itinerary:
            if not required_fields.issubset(entry.keys()):
                return jsonify({
                    "error": f"Missing one of {required_fields} in entry: {entry}"
                }), 400

        # 2️⃣ Add optional metadata (timestamp)
        for entry in itinerary:
            entry["timestamp"] = datetime.utcnow().isoformat()

        # 3️⃣ Authenticate with Power BI
        token = get_access_token()

        # 4️⃣ Push to Power BI
        status = push_to_powerbi(itinerary, token)

        return jsonify({
            "status": "success",
            "message": "Vacation data sent to Power BI successfully.",
            "rows_pushed": len(itinerary),
            "powerbi_status": status
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ======================
# Authentication Helper
# ======================
def get_access_token():
    """Obtain an OAuth2 token from Azure AD for Power BI API access."""
    url = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "scope": "https://analysis.windows.net/powerbi/api/.default"
    }

    response = requests.post(url, headers=headers, data=data)
    response.raise_for_status()
    return response.json()["access_token"]

# ======================
# Power BI Push Helper
# ======================
def push_to_powerbi(data, access_token):
    """Push itinerary data into the Power BI Streaming Dataset."""
    url = f"https://api.powerbi.com/v1.0/myorg/groups/{GROUP_ID}/datasets/{DATASET_ID}/tables/{TABLE_NAME}/rows"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }

    response = requests.post(url, headers=headers, json={"rows": data})
    response.raise_for_status()
    return response.status_code

# ======================
# Run Flask
# ======================
if __name__ == "__main__":
    app.run(debug=True, port=5000)
