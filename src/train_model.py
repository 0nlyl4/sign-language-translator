import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from features import normalize_landmarks

# ---------- Settings ----------
CSV_PATH = "data/landmarks.csv"
MODEL_PATH = "models/model.pkl"
# ------------------------------

df = pd.read_csv(CSV_PATH)

print(f"Total samples: {len(df)}")
print(f"Letters: {sorted(df['label'].unique())}")
print("\nSamples per letter and batch:")
print(df.groupby(["label", "batch"]).size())

X_raw = df.drop(columns=["label", "batch"]).values
y = df["label"]

X = np.array([normalize_landmarks(r) for r in X_raw])

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
baseline = 1 / len(y.unique())

print("\n" + "=" * 45)
print(f"Accuracy:  {accuracy:.2%}   (baseline {baseline:.0%})")
print("NOTE: within-session split - see results.md for the honest number")
print("=" * 45)

print("\nPer-letter report:")
print(classification_report(y_test, y_pred))

joblib.dump(model, MODEL_PATH)
print(f"Model saved to {MODEL_PATH}")