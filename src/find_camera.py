import cv2

print("Scanning for cameras...\n")

for i in range(5):
    cap = cv2.VideoCapture(i)
    if cap.isOpened():
        success, frame = cap.read()
        if success:
            h, w = frame.shape[:2]
            print(f"Camera FOUND at index {i}  -  resolution {w}x{h}")
        else:
            print(f"Index {i}: opened but no frame")
        cap.release()
    else:
        print(f"Index {i}: nothing")

print("\nScan complete.")