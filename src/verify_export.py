import json
import time

import joblib
import numpy as np
import pandas as pd

from features import normalize_landmarks

# ---------- Settings ----------
MODEL_JSON = "web/model.json"
MODEL_PKL = "models/model.pkl"
CSV_PATH = "data/landmarks.csv"
SAMPLE_COUNT = 2000
RANDOM_SEED = 42
# ------------------------------


def walk_tree(tree, x):
    node = 0
    while tree["f"][node] != -1:
        if x[tree["f"][node]] <= tree["t"][node]:
            node = tree["l"][node]
        else:
            node = tree["r"][node]
    return tree["v"][node]


def predict_proba_json(forest, x):
    votes = [0] * len(forest["classes"])
    for tree in forest["trees"]:
        votes[walk_tree(tree, x)] += 1
    n_trees = len(forest["trees"])
    return [v / n_trees for v in votes]


with open(MODEL_JSON) as f:
    forest = json.load(f)

model = joblib.load(MODEL_PKL)

sk_classes = [str(c) for c in model.classes_]
same_order = sk_classes == forest["classes"]

print(f"Classes match and same order: {same_order}")
if not same_order:
    print("STOP: class order differs.")
    raise SystemExit

df = pd.read_csv(CSV_PATH)
sample = df.sample(n=min(SAMPLE_COUNT, len(df)), random_state=RANDOM_SEED)

X = np.array([normalize_landmarks(r)
              for r in sample.drop(columns=["label", "batch"]).values])

sk_proba = model.predict_proba(X)

print(f"Comparing {len(X)} samples...")

start = time.time()
label_mismatch = 0
max_diff = 0.0

for i in range(len(X)):
    js_proba = np.array(predict_proba_json(forest, X[i]))
    max_diff = max(max_diff, np.abs(js_proba - sk_proba[i]).max())
    if js_proba.argmax() != sk_proba[i].argmax():
        label_mismatch += 1

elapsed = time.time() - start

print(f"\nDone in {elapsed:.1f}s")
print(f"Label mismatches:     {label_mismatch} / {len(X)}")
print(f"Max probability diff: {max_diff:.12f}")

print("\n" + "=" * 45)
if label_mismatch == 0 and max_diff < 1e-9:
    print("EXPORT IS EXACT - safe to continue to 9.3")
else:
    print("EXPORT DOES NOT MATCH - do not continue")
print("=" * 45)