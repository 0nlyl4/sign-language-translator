import json
import os

import numpy as np
import pandas as pd

from features import normalize_landmarks

# ---------- Settings ----------
CSV_PATH = "data/landmarks.csv"
OUTPUT_PATH = "web/shapes.json"
DECIMALS = 4
ANCHOR = (0, 9)
# ------------------------------

CONNECTIONS = [
    [0, 1], [1, 2], [2, 3], [3, 4],
    [0, 5], [5, 6], [6, 7], [7, 8],
    [5, 9], [9, 10], [10, 11], [11, 12],
    [9, 13], [13, 14], [14, 15], [15, 16],
    [13, 17], [17, 18], [18, 19], [19, 20],
    [0, 17]
]


def medoid_index(samples):
    squares = (samples ** 2).sum(axis=1)
    gram = samples @ samples.T
    squared = squares[:, None] + squares[None, :] - 2 * gram
    distances = np.sqrt(np.maximum(squared, 0))
    return int(distances.sum(axis=1).argmin())


df = pd.read_csv(CSV_PATH)

shapes = {}
report = []

for label in sorted(df["label"].unique()):
    subset = df[df["label"] == label]
    rows = subset.drop(columns=["label", "batch"]).values
    batches = subset["batch"].values

    normalized = np.array([normalize_landmarks(row) for row in rows])

    chosen = medoid_index(normalized)
    points = normalized[chosen].reshape(21, 3)

    shapes[str(label)] = [
        [round(float(p[0]), DECIMALS),
         round(float(p[1]), DECIMALS),
         round(float(p[2]), DECIMALS)]
        for p in points
    ]

    palm = float(np.linalg.norm(points[ANCHOR[1]] - points[ANCHOR[0]]))
    width = float(points[:, 0].max() - points[:, 0].min())
    height = float(points[:, 1].max() - points[:, 1].min())
    z_span = float(points[:, 2].max() - points[:, 2].min())
    xy_span = max(width, height)

    report.append({
        "label": str(label),
        "samples": len(rows),
        "batch": int(batches[chosen]),
        "extent": xy_span / palm,
        "z_ratio": z_span / xy_span
    })

data = {"connections": CONNECTIONS, "shapes": shapes}

os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

with open(OUTPUT_PATH, "w") as out:
    json.dump(data, out, separators=(",", ":"))

report.sort(key=lambda r: r["extent"], reverse=True)

print("Letter   samples   from batch   extent (xy / palm)   z / xy")
print("-" * 60)
for r in report:
    print(f"  {r['label']:<6} {r['samples']:>7} {r['batch']:>12}   "
          f"{r['extent']:>16.2f}   {r['z_ratio']:>6.2f}")

extents = [r["extent"] for r in report]
z_ratios = [r["z_ratio"] for r in report]
from_batch_1 = sum(1 for r in report if r["batch"] == 1)

print("-" * 60)
print(f"Largest / smallest extent: {max(extents) / min(extents):.2f}x")
print(f"Mean z/xy ratio: {np.mean(z_ratios):.2f}")
print(f"Chosen from batch 1: {from_batch_1} / {len(report)}")

print(f"\nWrote {OUTPUT_PATH}")
print(f"Letters: {len(shapes)}")
print(f"Size: {os.path.getsize(OUTPUT_PATH) / 1024:.1f} KB")