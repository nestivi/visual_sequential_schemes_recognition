import cv2
import mediapipe as mp
from .config import BUTTONS
from .state import register_click, reset_button

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

def process_frame(frame, hands):
    """Przetwarza pojedynczą klatkę, wykrywa dłoń i kliknięcia."""
    h_frame, w_frame, _ = frame.shape
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(frame_rgb)
    active_button = False

    if results.multi_hand_landmarks:
        hand_landmarks = results.multi_hand_landmarks[0]
        mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

        fingertip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
        cx = int(fingertip.x * w_frame)
        cy = int(fingertip.y * h_frame)
        cv2.circle(frame, (cx, cy), 10, (0, 0, 255), -1)

        for name, (x, y, w, h) in BUTTONS.items():
            if (x < cx < x + w) and (y < cy < y + h):
                active_button = True
                register_click(name)
            else:
                reset_button(name)

    return frame, active_button
