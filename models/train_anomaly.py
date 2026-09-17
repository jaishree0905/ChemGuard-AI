import pandas as pd
from sklearn.ensemble import IsolationForest
import joblib
import os

# Load normal TEP data
data = pd.read_csv(
    "data/tep_normal.csv",
    header=None
)

print("Dataset shape:", data.shape)

# Train Isolation Forest
model = IsolationForest(
    n_estimators=100,
    contamination=0.05,
    random_state=42
)

model.fit(data)

# Create models folder if needed
os.makedirs("models", exist_ok=True)

# Save trained model
joblib.dump(model, "models/isolation_forest.pkl")

print("Isolation Forest training completed!")
print("Model saved to: models/isolation_forest.pkl")