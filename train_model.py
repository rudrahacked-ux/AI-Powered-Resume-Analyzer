import pandas as pd
import numpy as np
import joblib

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report

# -----------------------------
# 1. Load Dataset
# -----------------------------
print("Loading dataset...")
data = pd.read_csv("placement_dataset.csv")

print("Dataset shape:", data.shape)
print(data.head())

# -----------------------------
# 2. Define Features & Target
# -----------------------------
X = data.drop("placed", axis=1)
y = data["placed"]


# -----------------------------
# 3. Train-Test Split
# -----------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

print("Training size:", X_train.shape)
print("Testing size:", X_test.shape)

# -----------------------------
# 4. Feature Scaling
# -----------------------------
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# -----------------------------
# 5. Logistic Regression
# -----------------------------
print("\nTraining Logistic Regression...")
log_model = LogisticRegression()
log_model.fit(X_train_scaled, y_train)

log_preds = log_model.predict(X_test_scaled)
log_acc = accuracy_score(y_test, log_preds)

print("Logistic Regression Accuracy:", log_acc)
print(classification_report(y_test, log_preds))

# -----------------------------
# 6. Random Forest
# -----------------------------
print("\nTraining Random Forest...")
rf_model = RandomForestClassifier(
    n_estimators=200,
    random_state=42
)
rf_model.fit(X_train, y_train)

rf_preds = rf_model.predict(X_test)
rf_acc = accuracy_score(y_test, rf_preds)

print("Random Forest Accuracy:", rf_acc)
print(classification_report(y_test, rf_preds))

# -----------------------------
# 7. Compare Models
# -----------------------------
if rf_acc > log_acc:
    print("\n✅ Random Forest Selected as Best Model")
    best_model = rf_model
    model_name = "random_forest"
else:
    print("\n✅ Logistic Regression Selected as Best Model")
    best_model = log_model
    model_name = "logistic_regression"

# -----------------------------
# 8. Save Model & Scaler
# -----------------------------
joblib.dump(best_model, "placement_model.pkl")
joblib.dump(scaler, "scaler.pkl")

print(f"\nModel saved as placement_model.pkl")
print("Scaler saved as scaler.pkl")
print("Training complete ✅")
