import json

import numpy as np

# ---------- Settings ----------
SHAPES_PATH = "web/shapes.json"
ANCHOR = (0, 9)
PASS_AT = 0.20
# ------------------------------

with open(SHAPES_PATH) as f:
    data = json.load(f)

connections = data["connections"]
shapes = data["shapes"]
letters = sorted(shapes.keys())

bones_3d = {}
bones_2d = {}

for letter in letters:
    points = np.array(shapes[letter], dtype=float)

    palm_3d = np.linalg.norm(points[ANCHOR[1]] - points[ANCHOR[0]])
    palm_2d = np.linalg.norm(points[ANCHOR[1]][:2] - points[ANCHOR[0]][:2])

    bones_3d[letter] = np.array([
        np.linalg.norm(points[a] - points[b]) / palm_3d
        for a, b in connections
    ])

    bones_2d[letter] = np.array([
        np.linalg.norm(points[a][:2] - points[b][:2]) / palm_2d
        for a, b in connections
    ])

reference_3d = np.median(np.array([bones_3d[c] for c in letters]), axis=0)
reference_2d = np.median(np.array([bones_2d[c] for c in letters]), axis=0)

report = []

for letter in letters:
    dev_3d = np.abs(bones_3d[letter] - reference_3d) / reference_3d
    dev_2d = np.abs(bones_2d[letter] - reference_2d) / reference_2d

    raw_3d = np.array([
        np.linalg.norm(np.array(shapes[letter][a]) - np.array(shapes[letter][b]))
        for a, b in connections
    ])
    raw_2d = np.array([
        np.linalg.norm(np.array(shapes[letter][a][:2]) - np.array(shapes[letter][b][:2]))
        for a, b in connections
    ])
    stretch = raw_3d / np.maximum(raw_2d, 1e-9)

    worst = int(dev_2d.argmax())

    report.append({
        "label": letter,
        "worst_3d": float(dev_3d.max()),
        "worst_2d": float(dev_2d.max()),
        "worst_bone_2d": connections[worst],
        "mean_2d": float(dev_2d.mean()),
        "stretch": float(stretch.max())
    })

report.sort(key=lambda r: r["worst_3d"], reverse=True)

print("Bone lengths compared against the median hand")
print(f"{len(connections)} bones, {len(letters)} letters\n")
print("Letter   worst 3D   worst 2D   mean 2D   worst bone 2D   max z stretch")
print("-" * 72)

for r in report:
    a, b = r["worst_bone_2d"]
    print(f"  {r['label']:<6} {r['worst_3d'] * 100:>8.1f}% {r['worst_2d'] * 100:>10.1f}%"
          f" {r['mean_2d'] * 100:>9.1f}%   {a:>6} - {b:<6} {r['stretch']:>11.1f}x")

worst_2d = max(r["worst_2d"] for r in report)
worst_3d = max(r["worst_3d"] for r in report)
worst_stretch = max(r["stretch"] for r in report)

print("-" * 72)
print(f"Largest deviation with z:    {worst_3d * 100:.1f}%")
print(f"Largest deviation without z: {worst_2d * 100:.1f}%")
print(f"Largest z stretch:           {worst_stretch:.1f}x")

print()
if worst_2d < PASS_AT:
    print("SHAPES ARE VALID IN X AND Y")
    print("The hands are real. The z axis is what breaks them.")
    print("Fix belongs in the renderer, not in the data.")
else:
    print("SHAPES ARE WRONG IN X AND Y TOO")
    print("z is not the only problem. Do not blame the renderer yet.")