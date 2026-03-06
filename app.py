from flask import Flask, request, jsonify, render_template
import joblib
import pandas as pd

app = Flask(__name__)

model = joblib.load("tomato_model.pkl")

labels = {
0:"Fresh Tomato",
1:"Spoiling Tomato",
2:"Spoiled Tomato"
}

@app.route("/")
def dashboard():
    return render_template("dashboard.html")

@app.route("/predict", methods=["POST"])
def predict():

    data = request.json

    temp = data["temp"]
    humidity = data["humidity"]
    gas = data["gas"]

    sample = pd.DataFrame([[temp,humidity,gas]],
    columns=["temp","humidity","gas"])

    prediction = model.predict(sample)[0]

    return jsonify({
        "status": labels[prediction]
    })

if __name__ == "__main__":
    app.run()
