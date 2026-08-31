import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier

from features import normalize_landmarks

df = pd.read_csv("data/landmarks.csv")

train_df = df[df["batch"] == 1]
test_df = df[df["batch"] == 2]

X_train = np.array([normalize_landmarks(r)
                    for r in train_df.drop(columns=["label", "batch"]).values])
y_train = train_df["label"]
X_test = np.array([normalize_landmarks(r)
                   for r in test_df.drop(columns=["label", "batch"]).values])
y_test = test_df["label"].values

model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

proba = model.predict_proba(X_test)
pred = model.classes_[proba.argmax(axis=1)]
conf = proba.max(axis=1)
correct = (pred == y_test)

print(f"Classes: {len(model.classes_)}   Baseline: {1/len(model.classes_):.1%}")
print(f"Accuracy (no threshold): {correct.mean():.2%}\n")

print(f"Confidence on CORRECT   predictions: "
      f"mean {conf[correct].mean():.2f}, "
      f"5th percentile {np.percentile(conf[correct], 5):.2f}")

if (~correct).sum() > 0:
    print(f"Confidence on INCORRECT predictions: "
          f"mean {conf[~correct].mean():.2f}, "
          f"95th percentile {np.percentile(conf[~correct], 95):.2f}")
else:
    print("No incorrect predictions in this split.")

print(f"\n{'thresh':>7} {'shown':>8} {'acc_shown':>11} {'rejected':>9}")
print("-" * 40)
for t in [0.3, 0.4, 0.5, 0.55, 0.6, 0.65, 0.7, 0.8, 0.9]:
    keep = conf >= t
    if keep.sum() == 0:
        print(f"{t:>7.2f} {0:>8.1%} {'-':>11} {1:>9.1%}")
        continue
    print(f"{t:>7.2f} {keep.mean():>8.1%} "
          f"{correct[keep].mean():>11.2%} {(~keep).mean():>9.1%}")