import json
import os

import numpy as np
import pandas as pd

from features import normalize_landmarks

# ---------- Settings ----------
CSV_PATH = "data/landmarks.csv"
OUTPUT_PATH = "web/shapes.json"
DECIMALS = 4
# ------------------------------

CONNECTIONS = [
    [0, 1], [1, 2], [2, 3], [3, 4],
    [0, 5], [5, 6], [6, 7], [7, 8],
    [5, 9], [9, 10], [10, 11], [11, 12],
    [9, 13], [13, 14], [14, 15], [15, 16],
    [13, 17], [17, 18], [18, 19], [19, 20],
    [0, 17]
]

df = pd.read_csv(CSV_PATH)

shapes = {}
z_spans = []

for label in sorted(df["label"].unique()):
    rows = df[df["label"] == label].drop(columns=["label", "batch"]).values
    median_row = np.median(rows, axis=0)
    points = normalize_landmarks(median_row).reshape(21, 3)

    shapes[str(label)] = [
        [round(float(p[0]), DECIMALS),
         round(float(p[1]), DECIMALS),
         round(float(p[2]), DECIMALS)]
        for p in points
    ]

    z_span = points[:, 2].max() - points[:, 2].min()
    xy_span = max(points[:, 0].max() - points[:, 0].min(),
                  points[:, 1].max() - points[:, 1].min())
    z_spans.append(z_span / xy_span)

    print(f"{label}: z span {z_span:.3f}   ratio to xy {z_span / xy_span:.2f}")

data = {"connections": CONNECTIONS, "shapes": shapes}

os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

with open(OUTPUT_PATH, "w") as out:
    json.dump(data, out, separators=(",", ":"))

print(f"\nWrote {OUTPUT_PATH}")
print(f"Letters: {len(shapes)}")
print(f"Size: {os.path.getsize(OUTPUT_PATH) / 1024:.1f} KB")
print(f"\nMean z/xy ratio: {np.mean(z_spans):.2f}")