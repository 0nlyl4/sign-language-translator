import cv2
import mediapipe as mp
import csv
import os
import time

# ---------- Settings ----------
SAMPLES_PER_LETTER = 300
COUNTDOWN_SECONDS = 3
CSV_PATH = "data/landmarks.csv"
# ------------------------------

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.5
)


def create_csv_if_needed():
    if not os.path.exists(CSV_PATH):
        header = ["label", "batch"]
        for i in range(21):
            header += [f"x{i}", f"y{i}", f"z{i}"]
        with open(CSV_PATH, "w", newline="") as f:
            csv.writer(f).writerow(header)
        print(f"Created {CSV_PATH}")


def extract_landmarks(hand_landmarks):
    row = []
    for lm in hand_landmarks.landmark:
        row += [lm.x, lm.y, lm.z]
    return row


def collect(label, batch):
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open camera")
        return

    collected = []
    state = "countdown"
    start_time = time.time()

    while True:
        success, frame = cap.read()
        if not success:
            break

        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb)

        hand_found = False
        if results.multi_hand_landmarks:
            hand_found = True
            landmarks = results.multi_hand_landmarks[0]
            mp_draw.draw_landmarks(frame, landmarks, mp_hands.HAND_CONNECTIONS)

        if state == "countdown":
            remaining = COUNTDOWN_SECONDS - int(time.time() - start_time)
            if remaining > 0:
                cv2.putText(frame, str(remaining), (280, 250),
                            cv2.FONT_HERSHEY_SIMPLEX, 4, (0, 255, 255), 6)
                cv2.putText(frame, f"Get ready: {label}", (10, 40),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
            else:
                state = "capturing"

        elif state == "capturing":
            if hand_found:
                collected.append(extract_landmarks(landmarks))

            count = len(collected)
            cv2.putText(frame, f"{label}:  {count}/{SAMPLES_PER_LETTER}", (10, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            bar_width = int((count / SAMPLES_PER_LETTER) * 400)
            cv2.rectangle(frame, (10, 60), (410, 85), (80, 80, 80), -1)
            cv2.rectangle(frame, (10, 60), (10 + bar_width, 85), (0, 255, 0), -1)

            if not hand_found:
                cv2.putText(frame, "NO HAND - paused", (10, 120),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

            if count >= SAMPLES_PER_LETTER:
                break

        cv2.imshow("Collecting Data", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            collected = []
            print("Cancelled.")
            break

    cap.release()
    cv2.destroyAllWindows()

    if collected:
        with open(CSV_PATH, "a", newline="") as f:
            writer = csv.writer(f)
            for row in collected:
                writer.writerow([label, batch] + row)
        print(f"Saved {len(collected)} samples for '{label}' (batch {batch})")


def main():
    create_csv_if_needed()

    batch = input("Batch number: ").strip()

    while True:
        label = input("\nLetter (or 'exit' to quit): ").strip().upper()
        if label == "EXIT":
            break
        if len(label) != 1:
            print("Enter a single letter.")
            continue
        collect(label, batch)

    print("\nDone.")


main()
