import json
import os

import joblib
import numpy as np

# ---------- Settings ----------
MODEL_PATH = "models/model.pkl"
OUTPUT_PATH = "web/model.json"
THRESHOLD_DECIMALS = 6
# ------------------------------


def check_leaf_purity(forest):
    total_leaves = 0
    impure = 0
    for estimator in forest.estimators_:
        tree = estimator.tree_
        for node in range(tree.node_count):
            if tree.children_left[node] == -1:
                total_leaves += 1
                if np.count_nonzero(tree.value[node][0]) > 1:
                    impure += 1
    return total_leaves, impure


def export_tree(estimator):
    tree = estimator.tree_
    features = []
    thresholds = []
    left = []
    right = []
    values = []

    for node in range(tree.node_count):
        is_leaf = tree.children_left[node] == -1
        if is_leaf:
            features.append(-1)
            thresholds.append(0)
            left.append(-1)
            right.append(-1)
            values.append(int(np.argmax(tree.value[node][0])))
        else:
            features.append(int(tree.feature[node]))
            thresholds.append(round(float(tree.threshold[node]),
                                    THRESHOLD_DECIMALS))
            left.append(int(tree.children_left[node]))
            right.append(int(tree.children_right[node]))
            values.append(-1)

    return {"f": features, "t": thresholds,
            "l": left, "r": right, "v": values}


model = joblib.load(MODEL_PATH)

n_nodes = sum(e.tree_.node_count for e in model.estimators_)

print(f"Trees:    {len(model.estimators_)}")
print(f"Nodes:    {n_nodes}")
print(f"Features: {model.n_features_in_}")
print(f"Classes:  {list(model.classes_)}")

total_leaves, impure = check_leaf_purity(model)
print(f"\nLeaves: {total_leaves}   impure leaves: {impure}")

if impure > 0:
    print("WARNING: impure leaves found.")
    print("Class-index export will NOT be exact. Stop and report this.")

data = {
    "classes": [str(c) for c in model.classes_],
    "n_features": int(model.n_features_in_),
    "trees": [export_tree(e) for e in model.estimators_]
}

os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

with open(OUTPUT_PATH, "w") as out:
    json.dump(data, out, separators=(",", ":"))

pkl_mb = os.path.getsize(MODEL_PATH) / (1024 * 1024)
json_mb = os.path.getsize(OUTPUT_PATH) / (1024 * 1024)

print(f"\nWrote {OUTPUT_PATH}")
print(f"model.pkl :  {pkl_mb:.2f} MB")
print(f"model.json:  {json_mb:.2f} MB")
print(f"Ratio     :  {pkl_mb / json_mb:.1f}x smaller")