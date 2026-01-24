"""
    Utility functions for hand gesture recognition.
"""
import os
import cv2
import mediapipe as mp
from collections import deque
from .config import BUTTONS, CLICK_MECHANICS, RESULT_PATH

mp_hands = mp.solutions.hands

def draw_buttons(frame):
    """
        Drawing buttons on the frame (CIRCLES for round buttons).
    """
    from .state import button_states
    
    for name, (x, y, w, h) in BUTTONS.items():
        # Calculate center and radius based on bounding box
        center_x = x + w // 2
        center_y = y + h // 2
        radius = min(w, h) // 2
        
        if button_states[name] == "pressed":
            color = (0, 255, 255)  # yellow for active
            thickness = -1         # fill
        else:
            color = (0, 255, 0)    # green for inactive
            thickness = 2
        
        # Draw Circle instead of Rectangle
        cv2.circle(frame, (center_x, center_y), radius, color, thickness)
        
        # Text positioning
        cv2.putText(frame, name, (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

def save_sequence(sequence, filename="sequence.txt"):
    try:
        os.makedirs(RESULT_PATH, exist_ok=True)

        file_path = os.path.join(RESULT_PATH, filename)
        with open(file_path, "w", encoding="utf-8") as f:
            for click in sequence:
                f.write(f"{click}\n")
        print(f"Sequence saved to file: {file_path}")
    except Exception as e:
        print(f"An error occurred while saving to file: {e}")

class FingerTracker:
    def __init__(self, buffer_size=5):
        self.positions = deque(maxlen=buffer_size)
    
    def update(self, x, y):
        self.positions.append((x, y))
        if len(self.positions) == 0:
            return x, y
        avg_x = int(sum(p[0] for p in self.positions) / len(self.positions))
        avg_y = int(sum(p[1] for p in self.positions) / len(self.positions))
        return avg_x, avg_y
    
    def reset(self):
        self.positions.clear()


def is_finger_pointing(hand_landmarks):
    index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
    index_pip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_PIP]
    return index_tip.y < index_pip.y


def is_finger_clicking_z(hand_landmarks):
    wrist = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST]
    index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
    
    relative_depth = index_tip.z - wrist.z
    is_clicking = relative_depth < CLICK_MECHANICS["click_depth_threshold"]
    
    return is_clicking, relative_depth

def enhance_frame(frame, alpha=1.1, beta=10):
    return cv2.convertScaleAbs(frame, alpha=alpha, beta=beta)