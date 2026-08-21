import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, confusion_matrix
from features import normalize_landmarks

df = pd.read_csv("data/landmarks.csv")
labels = sorted(df["label"].unique())


def prep(sub):
    X = np.array([normalize_landmarks(r) for r in
                  sub.drop(columns=["label", "batch"]).values])
    return X, sub["label"]


def report(name, X_tr, y_tr, X_te, y_te):
    m = RandomForestClassifier(n_estimators=100, random_state=42)
    m.fit(X_tr, y_tr)
    pred = m.predict(X_te)
    print(f"\n{'=' * 40}\n{name}:  {accuracy_score(y_te, pred):.2%}")
    print("      " + "   ".join(labels))
    for i, r in enumerate(confusion_matrix(y_te, pred, labels=labels)):
        print(f"{labels[i]}  " + "  ".join(f"{v:3d}" for v in r))


b1 = df[df["batch"] == 1]
b2 = df[df["batch"] == 2]

X1, y1 = prep(b1)
X2, y2 = prep(b2)

# Test 1: reverse direction
report("TRAIN b2 -> TEST b1", X2, y2, X1, y1)

# Test 2: is batch 2 internally consistent?
Xtr, Xte, ytr, yte = train_test_split(X2, y2, test_size=0.2,
                                      random_state=42, stratify=y2)
report("WITHIN batch 2 only", Xtr, ytr, Xte, yte)