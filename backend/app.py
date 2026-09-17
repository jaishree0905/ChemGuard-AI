from flask import Flask, jsonify
from flask_cors import CORS
import pandas as pd
import joblib
import shap
import numpy as np
import os

app = Flask(__name__)
CORS(app)

# ==========================================
# FILE PATHS
# ==========================================

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

DATA_PATH = os.path.join(
    BASE_DIR,
    "data",
    "tep_fault1.csv"
)

FAULT_MODEL_PATH = os.path.join(
    BASE_DIR,
    "models",
    "fault_diagnosis_model.pkl"
)

ANOMALY_MODEL_PATH = os.path.join(
    BASE_DIR,
    "models",
    "isolation_forest.pkl"
)

# ==========================================
# LOAD DATA + AI MODELS
# ==========================================

data = pd.read_csv(DATA_PATH, header=None)

fault_model = joblib.load(FAULT_MODEL_PATH)

anomaly_model = joblib.load(ANOMALY_MODEL_PATH)

# SHAP explainer for Random Forest
shap_explainer = shap.TreeExplainer(fault_model)

current_index = 0


# ==========================================
# HOME
# ==========================================

@app.route("/")
def home():
    return "CHEM-GUARD AI Backend Running Successfully"


# ==========================================
# METRICS + AI ANALYSIS
# ==========================================

@app.route("/metrics")
def metrics():

    global current_index

    # ------------------------------------------
    # Get current TEP sample
    # ------------------------------------------

    row = data.iloc[current_index]

    # ------------------------------------------
    # Important TEP sensor values
    # ------------------------------------------

    temperature = float(row.iloc[8])   # XMEAS(9)
    pressure = float(row.iloc[6])      # XMEAS(7)
    flow = float(row.iloc[5])          # XMEAS(6)
    level = float(row.iloc[7])         # XMEAS(8)

    # ------------------------------------------
    # Prepare all 52 TEP features
    # ------------------------------------------

    features = row.values.reshape(1, -1)

    # ==========================================
    # 1. FAULT DIAGNOSIS
    # ==========================================

    fault_prediction = fault_model.predict(features)[0]

    # ==========================================
    # 2. ANOMALY DETECTION
    # ==========================================

    anomaly_prediction = anomaly_model.predict(features)[0]

    # ==========================================
    # 3. AI CONFIDENCE
    # ==========================================

    fault_probabilities = fault_model.predict_proba(features)[0]

    confidence = max(fault_probabilities) * 100

    # ==========================================
    # 4. RISK LEVEL
    # ==========================================

    if fault_prediction == 1 and anomaly_prediction == -1:

        risk = "HIGH"

    elif fault_prediction == 1 or anomaly_prediction == -1:

        risk = "MEDIUM"

    else:

        risk = "LOW"

    # ==========================================
    # 5. DIAGNOSIS STATUS
    # ==========================================

    if fault_prediction == 1:
        
         diagnosis = "Process Fault Detected"

    else:

          diagnosis = "Normal Process"
    

    # ==========================================
    # 6. ANOMALY STATUS
    # ==========================================

    if anomaly_prediction == -1:

        anomaly_status = "Anomaly Detected"

    else:

        anomaly_status = "Normal Pattern"

    # ==========================================
    # 7. SHAP EXPLAINABILITY
    # ==========================================

    shap_result = shap_explainer(features)

    shap_array = np.asarray(shap_result.values)

    # SHAP classifier output
    if shap_array.ndim == 3:

        shap_values_sample = shap_array[0, :, 1]

    elif shap_array.ndim == 2:

        shap_values_sample = shap_array[0]

    else:

        shap_values_sample = shap_array.flatten()

    shap_values_sample = np.asarray(
        shap_values_sample
    ).flatten()

    # ==========================================
    # 8. FEATURE NAMES
    # ==========================================

    feature_names = [
        f"XMEAS({i})"
        for i in range(1, 53)
    ]

    # ==========================================
    # 9. CREATE ROOT CAUSE DATA
    # ==========================================

    root_cause_data = []

    for i in range(
        min(52, len(shap_values_sample))
    ):

        root_cause_data.append({

            "feature": feature_names[i],

            "value": round(
                float(row.iloc[i]),
                4
            ),

            "impact": round(
                float(shap_values_sample[i]),
                6
            )
        })

    # ==========================================
    # 10. SORT BY IMPORTANCE
    # ==========================================

    root_cause_data.sort(
        key=lambda x: abs(x["impact"]),
        reverse=True
    )

    # Top 5 important signals
    top_root_causes = root_cause_data[:5]

    # ==========================================
    # 11. SAMPLE NUMBER
    # ==========================================

    sample_number = current_index + 1

    # Move to next sample
    current_index += 1

    if current_index >= len(data):

        current_index = 0

    # ==========================================
    # 12. SEND DATA TO DASHBOARD
    # ==========================================

    return jsonify({

        # Sensor values
        "temperature": round(
            temperature,
            2
        ),

        "pressure": round(
            pressure,
            2
        ),

        "flow": round(
            flow,
            2
        ),

        "level": round(
            level,
            2
        ),

        # Sample
        "sample": sample_number,

        # AI diagnosis
        "diagnosis": diagnosis,

        # Anomaly
        "anomaly": anomaly_status,

        # Confidence
        "confidence": round(
            confidence,
            2
        ),

        # Risk
        "risk": risk,

        # SHAP root causes
        "root_causes": top_root_causes
    })


# ==========================================
# START FLASK
# ==========================================

if __name__ == "__main__":

    app.run(
        debug=True
    )