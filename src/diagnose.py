import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from features import normalize_landmarks

df = pd.read_csv("data/landmarks.csv")


def prep(d):
    X = np.array([normalize_landmarks(r)
                  for r in d.drop(columns=["label", "batch"]).values])
    return X, d["label"].values


def run(train_df, test_df, name):
    X_train, y_train = prep(train_df)
    X_test, y_test = prep(test_df)

    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    pred = model.predict(X_test)

    print(f"\n=== {name} ===")
    print(f"overall: {(pred == y_test).mean():.1%}")
    for letter in sorted(set(y_test)):
        mask = y_test == letter
        acc = (pred[mask] == letter).mean()
        wrong = pred[mask][pred[mask] != letter]
        top = pd.Series(wrong).value_counts()
        confused = f"-> {top.index[0]}" if len(top) else ""
        print(f"  {letter}: {acc:>5.0%}  {confused}")


b1 = df[df["batch"] == 1]
b2 = df[df["batch"] == 2]

tr, te = train_test_split(b1, test_size=0.2, random_state=42,
                          stratify=b1["label"])
run(tr, te, "WITHIN session 1")

tr, te = train_test_split(b2, test_size=0.2, random_state=42,
                          stratify=b2["label"])
run(tr, te, "WITHIN session 2")

run(b1, b2, "session 1 -> session 2")
run(b2, b1, "session 2 -> session 1")