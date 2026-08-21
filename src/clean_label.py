import pandas as pd

CSV_PATH = "data/landmarks.csv"
LABEL_TO_REMOVE = "C"

df = pd.read_csv(CSV_PATH)
before = len(df)

df = df[df["label"] != LABEL_TO_REMOVE]
df.to_csv(CSV_PATH, index=False)

print(f"Removed {before - len(df)} rows for '{LABEL_TO_REMOVE}'")
print(f"Remaining: {len(df)} rows")
print(df.groupby(['label', 'batch']).size())