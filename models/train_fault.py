import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import joblib
import os

# Load combined dataset
data = pd.read_csv("data/tep_training.csv", header=None)

# 52 sensor features
X = data.iloc[:, :-1]

# Last column = label
y = data.iloc[:, -1]

print("Dataset shape:", data.shape)
print("Features:", X.shape)
print("Labels:", y.shape)

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

# Train Random Forest
model = RandomForestClassifier(
    n_estimators=100,
    random_state=42
)

model.fit(X_train, y_train)

# Test
predictions = model.predict(X_test)

accuracy = accuracy_score(y_test, predictions)

print("Accuracy:", round(accuracy * 100, 2), "%")
print("\nClassification Report:")
print(classification_report(y_test, predictions))

# Save model
os.makedirs("models", exist_ok=True)

joblib.dump(
    model,
    "models/fault_diagnosis_model.pkl"
)

print("\nFault Diagnosis model saved!")
print("File: models/fault_diagnosis_model.pkl")