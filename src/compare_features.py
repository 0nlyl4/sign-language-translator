import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, confusion_matrix
from features import normalize_landmarks

df = pd.read_csv("data/landmarks.csv")

train_df = df[df["batch"] == 1]
test_df = df[df["batch"] == 2]

X_train_raw = train_df.drop(columns=["label", "batch"]).values
y_train = train_df["label"]
X_test_raw = test_df.drop(columns=["label", "batch"]).values
y_test = test_df["label"]

X_train_norm = np.array([normalize_landmarks(r) for r in X_train_raw])
X_test_norm = np.array([normalize_landmarks(r) for r in X_test_raw])

labels = sorted(y_train.unique())
baseline = 1 / len(labels)


def run(name, X_tr, X_te):
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_tr, y_train)
    pred = model.predict(X_te)
    acc = accuracy_score(y_test, pred)

    print(f"\n{'=' * 45}")
    print(f"{name}:  {acc:.2%}   (baseline {baseline:.0%})")
    print("=" * 45)
    print("      " + "   ".join(labels))
    cm = confusion_matrix(y_test, pred, labels=labels)
    for i, r in enumerate(cm):
        print(f"{labels[i]}  " + "  ".join(f"{v:3d}" for v in r))
    return acc


run("RAW coordinates", X_train_raw, X_test_raw)
run("NORMALIZED", X_train_norm, X_test_norm)
