import sys

import joblib
import numpy as np

from features import normalize_landmarks

MODEL_PATH = "models/model.pkl"

model = joblib.load(MODEL_PATH)

print("Paste the copied text from the browser, then press Enter twice.")
print("(paste all three lines)\n")

lines = []
while True:
    line = sys.stdin.readline()
    if line.strip() == "":
        break
    lines.append(line.strip())

raw = None
norm = None
header = ""

for line in lines:
    if line.startswith("letter="):
        header = line
    elif line.startswith("RAW "):
        raw = [float(v) for v in line[4:].split(",")]
    elif line.startswith("NORM "):
        norm = [float(v) for v in line[5:].split(",")]

if raw is None or norm is None:
    print("Could not find RAW and NORM lines.")
    sys.exit()

print(f"\n{header}")
print(f"raw values: {len(raw)}   norm values: {len(norm)}")

py_norm = normalize_landmarks(raw)
diff = np.abs(py_norm - np.array(norm)).max()
print(f"normalize max diff (py vs js): {diff:.10f}")


def report(name, features):
    probs = model.predict_proba(np.array(features).reshape(1, -1))[0]
    order = probs.argsort()[::-1][:3]
    top = "   ".join(f"{model.classes_[i]} {probs[i]*100:.0f}%" for i in order)
    print(f"{name:<22} {top}")


print()
report("python on js NORM:", norm)
report("python on py NORM:", py_norm)

flipped = py_norm.copy().reshape(21, 3)
flipped[:, 0] = -flipped[:, 0]
report("python on x-flipped:", flipped.flatten())