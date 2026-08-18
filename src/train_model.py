import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

# ---------- Settings ----------
CSV_PATH = "data/landmarks.csv"
MODEL_PATH = "models/model_batch1.pkl"
BATCHES = [1]
# ------------------------------

df = pd.read_csv(CSV_PATH)
df = df[df["batch"].isin(BATCHES)]

print(f"Total samples: {len(df)}")
print(f"Letters: {sorted(df['label'].unique())}")
print("\nSamples per letter:")
print(df["label"].value_counts().sort_index())

X = df.drop(columns=["label", "batch"])
y = df["label"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

print(f"\nTraining on {len(X_train)} samples, testing on {len(X_test)}")

model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)

n_classes = len(y.unique())
baseline = 1 / n_classes

print("\n" + "=" * 40)
print(f"Accuracy:  {accuracy:.2%}")
print(f"Baseline:  {baseline:.2%}  (random guess)")
print("=" * 40)

print("\nPer-letter report:")
print(classification_report(y_test, y_pred))

print("Confusion matrix:")
labels = sorted(y.unique())
print("     " + "  ".join(labels))
cm = confusion_matrix(y_test, y_pred, labels=labels)
for i, row in enumerate(cm):
    print(f"{labels[i]}  " + "  ".join(f"{v:2d}" for v in row))

joblib.dump(model, MODEL_PATH)
print(f"\nModel saved to {MODEL_PATH}")