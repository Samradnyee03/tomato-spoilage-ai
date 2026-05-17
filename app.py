from flask import Flask, request, jsonify, render_template
import os
import json
import gspread

from datetime import datetime, timedelta
from oauth2client.service_account import ServiceAccountCredentials

app = Flask(__name__)

# ---------------------------------------
# GOOGLE SHEETS SETUP
# ---------------------------------------

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

# Read credentials from Render environment variable
creds_dict = json.loads(os.environ["GOOGLE_CREDENTIALS"])

creds = ServiceAccountCredentials.from_json_keyfile_dict(
    creds_dict,
    scope
)

client = gspread.authorize(creds)

# IMPORTANT:
# Sheet name must exactly match Google Sheet name
sheet = client.open("Tomato Spoilage Monitoring").sheet1

# ---------------------------------------
# Latest Dashboard Data
# ---------------------------------------

latest_data = {
    "temp": 0,
    "humidity": 0,
    "gas": 0,
    "status": "Waiting",
    "remark": "Waiting for ESP32 data"
}

# ---------------------------------------
# Dashboard Route
# ---------------------------------------

@app.route("/")
def dashboard():
    return render_template("dashboard.html")

# ---------------------------------------
# Prediction Route
# ---------------------------------------

@app.route("/predict", methods=["POST"])
def predict():

    global latest_data

    data = request.json

    temp = data["temp"]
    humidity = data["humidity"]
    gas = data["gas"]

    # -----------------------------------
    # THRESHOLD CLASSIFICATION
    # -----------------------------------

    if gas < 200:

        status = "Fresh Tomato"

    elif gas < 300:

        status = "Spoiling Tomato"

    else:

        status = "Spoiled Tomato"

    # -----------------------------------
    # REMARKS
    # -----------------------------------

    if status == "Fresh Tomato":

        remark = "VOC levels stable under monitored conditions."

    elif status == "Spoiling Tomato":

        remark = "VOC concentration increasing. Early spoilage detected."

    else:

        remark = "High decomposition gases detected. Tomato likely spoiled."

    # -----------------------------------
    # DASHBOARD DATA
    # -----------------------------------

    latest_data = {
        "temp": temp,
        "humidity": humidity,
        "gas": gas,
        "status": status,
        "remark": remark
    }

    # -----------------------------------
    # INDIA TIME
    # -----------------------------------

    timestamp = (
        datetime.utcnow() + timedelta(hours=5, minutes=30)
    ).strftime("%Y-%m-%d %H:%M:%S")

    # -----------------------------------
    # GOOGLE SHEETS LOGGING
    # -----------------------------------

    try:

        sheet.append_row([
            timestamp,
            temp,
            humidity,
            gas,
            status,
            remark
        ])

        print("Data logged to Google Sheets")

    except Exception as e:

        print("Google Sheets Error:", e)

    # -----------------------------------
    # RESPONSE
    # -----------------------------------

    return jsonify(latest_data)

# ---------------------------------------
# LIVE DASHBOARD DATA API
# ---------------------------------------

@app.route("/data")
def data():
    return jsonify(latest_data)

# ---------------------------------------
# RUN FLASK
# ---------------------------------------

if __name__ == "__main__":

    port = int(os.environ.get("PORT", 5000))

    app.run(host="0.0.0.0", port=port)
