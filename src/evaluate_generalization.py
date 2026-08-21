import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

CSV_PATH = "data/landmarks.csv"

df = pd.read_csv(CSV_PATH)

train_df = df[df["batch"] == 1]
test_df = df[df["batch"] == 2]

print(f"Train (session 1): {len(train_df)} samples")
print(f"Test  (session 2): {len(test_df)} samples")

X_train = train_df.drop(columns=["label", "batch"])
y_train = train_df["label"]
X_test = test_df.drop(columns=["label", "batch"])
y_test = test_df["label"]

model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
baseline = 1 / len(y_train.unique())

print("\n" + "=" * 45)
print("CROSS-SESSION EVALUATION")
print(f"Accuracy:  {accuracy:.2%}")
print(f"Baseline:  {baseline:.2%}")
print("=" * 45)

print("\nPer-letter report:")
print(classification_report(y_test, y_pred))

print("Confusion matrix:")
labels = sorted(y_train.unique())
print("      " + "   ".join(labels))
cm = confusion_matrix(y_test, y_pred, labels=labels)
for i, row in enumerate(cm):
    print(f"{labels[i]}  " + "  ".join(f"{v:3d}" for v in row))

