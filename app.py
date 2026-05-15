from flask import Flask, request, jsonify, render_template, send_file
import joblib
import pandas as pd
import os
import csv
from datetime import datetime

app = Flask(__name__)

# Load ML model
model = joblib.load("tomato_model.pkl")

# Labels
labels = {
    0: "Fresh Tomato",
    1: "Spoiling Tomato",
    2: "Spoiled Tomato"
}

# Latest dashboard data
latest_data = {
    "temp": 0,
    "humidity": 0,
    "gas": 0,
    "status": "Waiting",
    "remark": "Waiting for ESP32 data"
}

# ---------------------------------------
# Dashboard
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

    # ML prediction
    sample = pd.DataFrame(
        [[temp, humidity, gas]],
        columns=["temp", "humidity", "gas"]
    )

    prediction = model.predict(sample)[0]

    status = labels[prediction]

    # Remarks
    if prediction == 0:
        remark = "Tomatoes stable under summer conditions."

    elif prediction == 1:
        remark = "Early spoilage detected. Monitor storage."

    else:
        remark = "High VOC detected. Tomatoes likely spoiled."

    # Latest live dashboard data
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

        # Write header once
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
            datetime.now(),
            temp,
            humidity,
            gas,
            status,
            remark
        ])

    return jsonify(latest_data)

# ---------------------------------------
# Dashboard Live Data
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
# Run Flask
# ---------------------------------------

if __name__ == "__main__":

    port = int(os.environ.get("PORT", 5000))

    app.run(host="0.0.0.0", port=port)
