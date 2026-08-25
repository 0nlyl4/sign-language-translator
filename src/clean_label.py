import sys
import shutil
import pandas as pd

CSV_PATH = "data/landmarks.csv"
BACKUP_PATH = "data/landmarks_backup.csv"

df = pd.read_csv(CSV_PATH)

print(df.groupby(["label", "batch"]).size())

target = input("\nLabel to remove: ").strip().upper()

if target not in df["label"].unique():
    print(f"'{target}' not found. Nothing removed.")
    sys.exit()

batch_input = input("Batch (1, 2, or blank for all): ").strip()

mask = df["label"] == target
scope = f"'{target}' (all batches)"

if batch_input:
    batch = int(batch_input)
    mask = mask & (df["batch"] == batch)
    scope = f"'{target}' batch {batch}"

count = mask.sum()

if count == 0:
    print(f"No rows match {scope}. Nothing removed.")
    sys.exit()

print(f"This will remove {count} rows for {scope}.")

if input("Type the label again to confirm: ").strip().upper() != target:
    print("Cancelled. Nothing removed.")
    sys.exit()

shutil.copy(CSV_PATH, BACKUP_PATH)
print(f"Backup saved to {BACKUP_PATH}")

df = df[~mask]
df.to_csv(CSV_PATH, index=False)

print(f"Removed {count} rows for {scope}")
print(f"Remaining: {len(df)} rows")
print(df.groupby(["label", "batch"]).size())
