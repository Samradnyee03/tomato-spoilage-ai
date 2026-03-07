from flask import Flask, request, jsonify, render_template
import joblib
import pandas as pd
import os

app = Flask(__name__)

model = joblib.load("tomato_model.pkl")

labels = {
0:"Fresh Tomato",
1:"Spoiling Tomato",
2:"Spoiled Tomato"
}

latest_data = {
"temp":0,
"humidity":0,
"gas":0,
"status":"Waiting",
"remark":"Waiting for ESP32 data"
}

@app.route("/")
def dashboard():
    return render_template("dashboard.html")

@app.route("/predict", methods=["POST"])
def predict():

    global latest_data

    data = request.json

    temp = data["temp"]
    humidity = data["humidity"]
    gas = data["gas"]

    sample = pd.DataFrame([[temp,humidity,gas]],
                          columns=["temp","humidity","gas"])

    prediction = model.predict(sample)[0]

    status = labels[prediction]

    if prediction == 0:
        remark = "Tomatoes stable under summer conditions."
    elif prediction == 1:
        remark = "Early spoilage detected. Monitor storage."
    else:
        remark = "High VOC detected. Tomatoes likely spoiled."

    latest_data = {
        "temp": temp,
        "humidity": humidity,
        "gas": gas,
        "status": status,
        "remark": remark
    }

    return jsonify(latest_data)

@app.route("/data")
def data():
    return jsonify(latest_data)

if __name__ == "__main__":
    port = int(os.environ.get("PORT",5000))
    app.run(host="0.0.0.0",port=port)
