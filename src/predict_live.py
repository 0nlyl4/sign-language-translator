import cv2
import mediapipe as mp
import joblib
import numpy as np

from collections import deque, Counter
from features import normalize_landmarks


MODEL_PATH = "models/model.pkl"
CAMERA_INDEX = 0
CONFIDENCE_THRESHOLD = 0.55
SMOOTHING_WINDOW = 7
HOLD_FRAMES = 15

GREEN = (0, 255, 0)
RED = (0, 0, 255)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)


model = joblib.load(MODEL_PATH)
print(f"Model loaded. Knows: {list(model.classes_)}")
print(f"Confidence threshold: {CONFIDENCE_THRESHOLD:.0%}")
print(f"Smoothing window: {SMOOTHING_WINDOW} frames")
print(f"Hold to commit: {HOLD_FRAMES} frames")
print("Keys: [space] space   [backspace] delete   [c] clear   [q] quit")


mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.5
)


cap = cv2.VideoCapture(CAMERA_INDEX)
if not cap.isOpened():
    print("Error: Could not open camera")
    exit()

print("Running.")

history = deque(maxlen=SMOOTHING_WINDOW)
sentence = ""
hold_letter = None
hold_count = 0
committed = False


while True:
    success, frame = cap.read()
    if not success:
        break

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)

    if results.multi_hand_landmarks:
        landmarks = results.multi_hand_landmarks[0]
        mp_draw.draw_landmarks(frame, landmarks, mp_hands.HAND_CONNECTIONS)

        row = []
        for lm in landmarks.landmark:
            row += [lm.x, lm.y, lm.z]

        features = normalize_landmarks(row).reshape(1, -1)

        probs = model.predict_proba(features)[0]
        best = probs.argmax()
        prediction = model.classes_[best]
        confidence = probs[best]

        if confidence >= CONFIDENCE_THRESHOLD:
            history.append(prediction)
        else:
            history.append(None)

        stable_letter, votes = Counter(history).most_common(1)[0]

        if stable_letter == hold_letter:
            hold_count += 1
        else:
            hold_letter = stable_letter
            hold_count = 1
            committed = False

        if stable_letter is not None and not committed and hold_count >= HOLD_FRAMES:
            sentence += stable_letter
            committed = True

        if stable_letter is not None:
            display_text = stable_letter
            color = GREEN
        else:
            display_text = "?"
            color = RED

        cv2.putText(frame, display_text, (250, 120),
                    cv2.FONT_HERSHEY_SIMPLEX, 4, color, 8)
        cv2.putText(frame, f"{confidence:.0%}", (250, 170),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

        if stable_letter is not None:
            progress = min(hold_count / HOLD_FRAMES, 1.0)
            cv2.rectangle(frame, (250, 230), (400, 245), color, 1)
            cv2.rectangle(frame, (250, 230), (250 + int(150 * progress), 245),
                          color, -1)
    else:
        history.clear()
        hold_letter = None
        hold_count = 0
        committed = False
        cv2.putText(frame, "No hand", (10, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, RED, 2)

    h, w = frame.shape[:2]
    cv2.rectangle(frame, (0, h - 60), (w, h), BLACK, -1)
    cv2.putText(frame, sentence[-20:], (10, h - 20),
                cv2.FONT_HERSHEY_SIMPLEX, 1.2, WHITE, 2)

    cv2.imshow("Sign Language Translator", frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key == 32:
        sentence += " "
    elif key == 8:
        sentence = sentence[:-1]
    elif key == ord('c'):
        sentence = ""


cap.release()
cv2.destroyAllWindows()
print(f"Final output: {sentence}")