from flask import Flask, jsonify
from flask_cors import CORS
import pandas as pd
import os

app = Flask(__name__)
CORS(app)

# Load TEP Fault 1 dataset
DATA_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "data",
    "tep_fault1.csv"
)

data = pd.read_csv(DATA_PATH, header=None)

# Start from first sample
current_index = 0


@app.route("/")
def home():
    return "CHEM-GUARD AI Backend Running Successfully"


@app.route("/metrics")
def metrics():
    global current_index

    row = data.iloc[current_index]

    # TEP variables
    temperature = round(float(row[8]), 2)   # XMEAS(9)
    pressure = round(float(row[6]), 2)      # XMEAS(7)
    flow = round(float(row[5]), 2)          # XMEAS(6)
    level = round(float(row[7]), 2)         # XMEAS(8)

    sample_number = current_index + 1

    current_index += 1

    if current_index >= len(data):
        current_index = 0

    return jsonify({
        "temperature": temperature,
        "pressure": pressure,
        "flow": flow,
        "level": level,
        "sample": sample_number,
        "status": "Fault 1"
    })


if __name__ == "__main__":
    app.run(debug=True)