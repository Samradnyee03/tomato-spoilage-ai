from flask import Flask, request, jsonify, render_template, send_file
import pandas as pd
import os
import csv
from datetime import datetime

app = Flask(__name__)

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
    # REAL THRESHOLD-BASED CLASSIFICATION
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
    # Latest Live Dashboard Data
    # -----------------------------------

    latest_data = {
        "temp": temp,
        "humidity": humidity,
        "gas": gas,
        "status": status,
        "remark": remark
    }

    # -----------------------------------
    # CSV DATA LOGGING
    # -----------------------------------

    file_exists = os.path.isfile("tomato_readings.csv")

    with open("tomato_readings.csv", "a", newline="") as f:

        writer = csv.writer(f)

        # Write header only once
        if not file_exists:

            writer.writerow([
                "Timestamp",
                "Temperature",
                "Humidity",
                "Gas",
                "Status",
                "Remark"
            ])

        # Write sensor data
        writer.writerow([
            (datetime.utcnow() + timedelta(hours=5, minutes=30)).strftime("%Y-%m-%d %H:%M:%S"),
            temp,
            humidity,
            gas,
            status,
            remark
        ])

    return jsonify(latest_data)

# ---------------------------------------
# Live Dashboard Data API
# ---------------------------------------

@app.route("/data")
def data():
    return jsonify(latest_data)

# ---------------------------------------
# VIEW CSV LOGS
# ---------------------------------------

@app.route("/logs")
def logs():

    if not os.path.exists("tomato_readings.csv"):
        return "No logs available yet."

    with open("tomato_readings.csv", "r") as f:

        data = f.read()

    return "<pre>" + data + "</pre>"

# ---------------------------------------
# DOWNLOAD CSV FILE
# ---------------------------------------

@app.route("/download")
def download():

    if not os.path.exists("tomato_readings.csv"):
        return "CSV file not found."

    return send_file(
        "tomato_readings.csv",
        as_attachment=True
    )

# ---------------------------------------
# RUN FLASK
# ---------------------------------------

if __name__ == "__main__":

    port = int(os.environ.get("PORT", 5000))

    app.run(host="0.0.0.0", port=port)
