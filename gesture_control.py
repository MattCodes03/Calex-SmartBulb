import cv2
import mediapipe as mp

from mediapipe.tasks import python
from mediapipe.tasks.python import vision

from calex import CalexBulb


bulb = CalexBulb()
base_options = python.BaseOptions(model_asset_path="hand_landmarker.task")
options = vision.HandLandmarkerOptions(base_options=base_options, num_hands=1)
detector = vision.HandLandmarker.create_from_options(options)


def hand_is_open(hand_landmarks):
    fingers = [
        (8, 6),    # Index finger
        (12, 10),  # Middle finger
        (16, 14),  # Ring finger
        (20, 18),  # Pinky
    ]
    extended = 0
    for tip, pip in fingers:
        if hand_landmarks[tip].y < hand_landmarks[pip].y:
            extended += 1

    # Consider the hand open if at least
    # three of the four fingers are extended.
    return extended >= 3


cap = cv2.VideoCapture(0)

if not cap.isOpened():
    raise RuntimeError("Could not open webcam")


last_state = None
candidate_state = None
candidate_frames = 0

# Number of consecutive frames required
# before accepting a new gesture.
STABLE_FRAMES = 8

while cap.isOpened():

    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)

    # OpenCV uses BGR.
    # MediaPipe expects RGB.
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

    result = detector.detect(mp_image)

    if result.hand_landmarks:

        hand_landmarks = result.hand_landmarks[0]
        is_open = hand_is_open(hand_landmarks)

        if is_open:
            state = "on"
        else:
            state = "off"

        if state == candidate_state:
            candidate_frames += 1
        else:
            candidate_state = state
            candidate_frames = 1

        if (candidate_frames >= STABLE_FRAMES and state != last_state):
            if state == "on":
                print("Open hand -> BULB ON")
                bulb.on()
            else:
                print("Closed hand -> BULB OFF")
                bulb.off()

            last_state = state

        for landmark in hand_landmarks:
            x = int(landmark.x * frame.shape[1])
            y = int(landmark.y * frame.shape[0])
            cv2.circle(frame, (x, y), 5, (0, 255, 0), -1)

        connections = [
            (0, 1),
            (1, 2),
            (2, 3),
            (3, 4),

            (0, 5),
            (5, 6),
            (6, 7),
            (7, 8),

            (0, 9),
            (9, 10),
            (10, 11),
            (11, 12),

            (0, 13),
            (13, 14),
            (14, 15),
            (15, 16),

            (0, 17),
            (17, 18),
            (18, 19),
            (19, 20),

            (5, 9),
            (9, 13),
            (13, 17),
        ]

        for start, end in connections:
            x1 = int(hand_landmarks[start].x * frame.shape[1])
            y1 = int(hand_landmarks[start].y * frame.shape[0])

            x2 = int(hand_landmarks[end].x * frame.shape[1])
            y2 = int(hand_landmarks[end].y * frame.shape[0])

            cv2.line(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

        if state == "on":
            text = "OPEN HAND - ON"
            colour = (0, 255, 0)

        else:
            text = "CLOSED HAND - OFF"
            colour = (0, 0, 255)

        cv2.putText(frame, text, (20, 45),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, colour, 2)
    else:

        cv2.putText(frame, "NO HAND DETECTED", (20, 45),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        # Reset candidate gesture.
        candidate_state = None
        candidate_frames = 0

    cv2.imshow("CALEX Gesture Control", frame)
    # Press Q to quit.
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
detector.close()
