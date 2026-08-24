import cv2
import mediapipe as mp
import joblib
import numpy as np

from collections import deque, Counter
from features import normalize_landmarks


MODEL_PATH = "models/model.pkl"
CAMERA_INDEX = 0
CONFIDENCE_THRESHOLD = 0.80
SMOOTHING_WINDOW = 10

GREEN = (0, 255, 0)
RED = (0, 0, 255)


model = joblib.load(MODEL_PATH)
print(f"Model loaded. Knows: {list(model.classes_)}")
print(f"Confidence threshold: {CONFIDENCE_THRESHOLD:.0%}")
print(f"Smoothing window: {SMOOTHING_WINDOW} frames")


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

print("Running. Press 'q' to quit.")

history = deque(maxlen=SMOOTHING_WINDOW)


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

        prediction = model.predict(features)[0]
        confidence = model.predict_proba(features).max()

        if confidence >= CONFIDENCE_THRESHOLD:
            history.append(prediction)
        else:
            history.append(None)

        stable_letter, votes = Counter(history).most_common(1)[0]

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
        cv2.putText(frame, f"{votes}/{len(history)}", (250, 210),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
    else:
        history.clear()
        cv2.putText(frame, "No hand", (10, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, RED, 2)

    cv2.imshow("Sign Language Translator", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


cap.release()
cv2.destroyAllWindows()