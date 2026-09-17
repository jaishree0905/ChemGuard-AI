import pandas as pd
import joblib

# Load TEP normal data
data = pd.read_csv(
    "data/tep_normal.csv",
    header=None
)

# Load trained model
model = joblib.load(
    "models/isolation_forest.pkl"
)

# Predict
predictions = model.predict(data)

# Count results
normal = (predictions == 1).sum()
anomaly = (predictions == -1).sum()

print("Total samples:", len(predictions))
print("Normal samples:", normal)
print("Anomaly samples:", anomaly)