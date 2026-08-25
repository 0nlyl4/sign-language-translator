import sys
import shutil
import pandas as pd

CSV_PATH = "data/landmarks.csv"
BACKUP_PATH = "data/landmarks_backup.csv"

df = pd.read_csv(CSV_PATH)
labels = sorted(df["label"].unique())

print(f"Labels in file: {labels}")

target = input("Label to remove: ").strip().upper()

if target not in labels:
    print(f"'{target}' not found. Nothing removed.")
    sys.exit()

count = (df["label"] == target).sum()
print(f"This will remove {count} rows for '{target}'.")

if input("Type the label again to confirm: ").strip().upper() != target:
    print("Cancelled. Nothing removed.")
    sys.exit()

shutil.copy(CSV_PATH, BACKUP_PATH)
print(f"Backup saved to {BACKUP_PATH}")

df = df[df["label"] != target]
df.to_csv(CSV_PATH, index=False)

print(f"Removed {count} rows for '{target}'")
print(f"Remaining: {len(df)} rows")
print(df.groupby(["label", "batch"]).size())
