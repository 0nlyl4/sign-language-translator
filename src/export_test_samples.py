import json
import os

import joblib
import numpy as np
import pandas as pd

from features import normalize_landmarks

# ---------- Settings ----------
MODEL_PATH = "models/model.pkl"
CSV_PATH = "data/landmarks.csv"
OUTPUT_PATH = "web/test_samples.json"
SAMPLE_COUNT = 20
RANDOM_SEED = 7
# ------------------------------

model = joblib.load(MODEL_PATH)
df = pd.read_csv(CSV_PATH)

sample = df.sample(n=SAMPLE_COUNT, random_state=RANDOM_SEED)

samples = []

for _, row in sample.iterrows():
    raw = row.drop(["label", "batch"]).values.astype(float)
    normalized = normalize_landmarks(raw)

    probs = model.predict_proba(normalized.reshape(1, -1))[0]
    best = int(probs.argmax())

    samples.append({
        "label": str(row["label"]),
        "batch": int(row["batch"]),
        "raw": [round(float(v), 8) for v in raw],
        "normalized": [round(float(v), 8) for v in normalized],
        "expected_letter": str(model.classes_[best]),
        "expected_confidence": round(float(probs[best]), 8)
    })

os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

with open(OUTPUT_PATH, "w") as out:
    json.dump(samples, out, indent=1)

correct = sum(1 for s in samples if s["label"] == s["expected_letter"])

print(f"Wrote {OUTPUT_PATH}")
print(f"Samples: {len(samples)}")
print(f"Python got {correct}/{len(samples)} right")
print(f"Size: {os.path.getsize(OUTPUT_PATH) / 1024:.0f} KB")

print("\nFirst 5:")
for s in samples[:5]:
    print(f"  true={s['label']}  pred={s['expected_letter']}  "
          f"conf={s['expected_confidence']:.2f}")