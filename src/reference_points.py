import cv2
import mediapipe as mp

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.5
)

KEY_POINTS = [0, 4, 8, 12]

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open camera")
    exit()

print("Hold your hand still. Press 'p' to print, 'q' to quit.")

while True:
    success, frame = cap.read()
    if not success:
        break

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)

    landmarks = None
    if results.multi_hand_landmarks:
        landmarks = results.multi_hand_landmarks[0]
        mp_draw.draw_landmarks(frame, landmarks, mp_hands.HAND_CONNECTIONS)

        h, w = frame.shape[:2]
        for i in KEY_POINTS:
            lm = landmarks.landmark[i]
            px, py = int(lm.x * w), int(lm.y * h)
            cv2.putText(frame, str(i), (px + 8, py),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

        cv2.putText(frame, "Press 'p' to print", (10, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
    else:
        cv2.putText(frame, "No hand", (10, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

    cv2.imshow("Reference Points", frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key == ord('p') and landmarks is not None:
        print("")
        for i in KEY_POINTS:
            lm = landmarks.landmark[i]
            print(f"point {i:2d}:  x={lm.x:.4f}  y={lm.y:.4f}  z={lm.z:.4f}")
        print("-" * 42)

cap.release()
cv2.destroyAllWindows()