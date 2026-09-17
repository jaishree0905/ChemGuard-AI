import pandas as pd
import joblib
import shap
import numpy as np

# Load data
data = pd.read_csv("data/tep_fault1.csv", header=None)

# Load trained fault model
model = joblib.load("models/fault_diagnosis_model.pkl")

# Take one sample
sample = data.iloc[[0]]

# Create SHAP explainer
explainer = shap.TreeExplainer(model)

# Calculate SHAP values
shap_values = explainer.shap_values(sample)

print("SHAP explanation generated successfully!")
print("SHAP output shape:", np.array(shap_values).shape)

# Feature names
feature_names = [
    f"XMEAS({i})" for i in range(1, 53)
]

# Convert SHAP output to numpy array
values = np.array(shap_values)

# Print shape so we know exactly what SHAP returned
print("Processed shape:", values.shape)

# Extract the values for our single sample
if values.ndim == 3:
    # Shape usually: samples × features × classes
    values = values[0, :, 1]

elif values.ndim == 2:
    # Shape: samples × features
    values = values[0]

elif values.ndim == 1:
    # Already features
    values = values

else:
    raise ValueError(
        f"Unexpected SHAP shape: {values.shape}"
    )

# Make sure we have exactly 52 feature values
values = np.asarray(values).flatten()

print("Number of SHAP features:", len(values))

# Create explanation table
explanation = pd.DataFrame({
    "Feature": feature_names,
    "SHAP Value": values,
    "Sensor Value": sample.iloc[0].values
})

# Calculate importance
sensor_values = sample.iloc[0].to_numpy().flatten()
values = np.asarray(values).flatten()

print("Features:", len(feature_names))
print("SHAP values:", len(values))
print("Sensor values:", len(sensor_values))

explanation = pd.DataFrame(
    list(zip(feature_names, values, sensor_values)),
    columns=["Feature", "SHAP Value", "Sensor Value"]
)
print("\nTop 10 Root Cause Signals:")
print(
    explanation[
        ["Feature", "Sensor Value", "SHAP Value"]
    ].head(10).to_string(index=False)
)