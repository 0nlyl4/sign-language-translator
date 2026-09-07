import json
import os
import time
import urllib.parse
import urllib.request

# ---------- Settings ----------
LETTERS = "ABCDEFGHIKLMNOPQRSTUVWXY"
OUTPUT_DIR = "web/letters"
API_URL = "https://commons.wikimedia.org/w/api.php"
DELAY = 8.0
MAX_FAILS_IN_A_ROW = 3
MIN_BYTES = 1000
# ------------------------------

os.makedirs(OUTPUT_DIR, exist_ok=True)

headers = {"User-Agent": "sign-language-translator/1.0 (student project)"}


def get(url):
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read()


def have(letter):
    path = os.path.join(OUTPUT_DIR, f"{letter}.svg")
    return os.path.exists(path) and os.path.getsize(path) >= MIN_BYTES


todo = [c for c in LETTERS if not have(c)]

print(f"Already have {len(LETTERS) - len(todo)} letters")

if not todo:
    print("Nothing to download.")
    raise SystemExit

print(f"Need: {' '.join(todo)}")
print(f"This will take about {len(todo) * DELAY / 60:.1f} minutes\n")

titles = "|".join(f"File:Sign language {c}.svg" for c in todo)

params = urllib.parse.urlencode({
    "action": "query",
    "format": "json",
    "titles": titles,
    "prop": "imageinfo",
    "iiprop": "url"
})

payload = json.loads(get(f"{API_URL}?{params}"))

urls = {}
for page in payload["query"]["pages"].values():
    title = page["title"].replace("File:Sign language ", "").replace(".svg", "")
    if "imageinfo" in page:
        urls[title] = page["imageinfo"][0]["url"]

time.sleep(DELAY)

fails_in_a_row = 0
stopped = False

for letter in todo:
    if letter not in urls:
        print(f"{letter}: no such file on Commons")
        continue

    try:
        data = get(urls[letter])
        with open(os.path.join(OUTPUT_DIR, f"{letter}.svg"), "wb") as out:
            out.write(data)
        print(f"{letter}: {len(data) / 1024:.1f} KB")
        fails_in_a_row = 0

    except Exception as error:
        print(f"{letter}: failed")
        fails_in_a_row += 1

        if fails_in_a_row >= MAX_FAILS_IN_A_ROW:
            print(f"\nStopping - {MAX_FAILS_IN_A_ROW} failures in a row.")
            print("The server is rate limiting. Wait an hour, then run again.")
            stopped = True
            break

    time.sleep(DELAY)

total = sum(1 for c in LETTERS if have(c))
print(f"\nHave {total} / {len(LETTERS)} in {OUTPUT_DIR}")

if total < len(LETTERS):
    still = " ".join(c for c in LETTERS if not have(c))
    print(f"Missing: {still}")
    if not stopped:
        print("Run again in a few minutes to get the rest.")
else:
    print("All letters downloaded.")