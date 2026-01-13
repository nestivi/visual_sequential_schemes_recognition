"""
    Utility functions for hand gesture recognition.
"""

import cv2
import mediapipe as mp
from collections import deque
from .config import BUTTONS, CLICK_MECHANICS

mp_hands = mp.solutions.hands

def draw_buttons(frame):
    """
        Drawing buttons on the frame with visual feedback.
    """
    from .state import button_states
    for name, (x, y, w, h) in BUTTONS.items():
        if button_states[name] == "pressed":
            color = (0, 255, 255)  # yellow for active
            thickness = -1         # fill button when pressed
        else:
            color = (0, 255, 0)    # green for inactive
            thickness = 2
            
        cv2.rectangle(frame, (x, y), (x + w, y + h), color, thickness)
        cv2.putText(frame, name, (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

def save_sequence(sequence, filename="sequence.txt"):
    try:
        with open(filename, "w", encoding="utf-8") as f:
            for click in sequence:
                f.write(f"{click}\n")
        print(f"Sequence saved to file: {filename}")
    except Exception as e:
        print(f"An error occurred while saving to file: {e}")

class FingerTracker:
    """Smooths finger position to reduce jitter."""
    
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
    index_extended = index_tip.y < index_pip.y
    return index_extended


def is_finger_clicking_z(hand_landmarks):
    """
    Check if the finger is pressing down using Z-axis depth.
    Compares Index Finger Tip Z vs Wrist Z.
    """
    wrist = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST]
    index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
    
    relative_depth = index_tip.z - wrist.z
    is_clicking = relative_depth < CLICK_MECHANICS["click_depth_threshold"]
    
    return is_clicking, relative_depth

def enhance_frame(frame, alpha=1.1, beta=10):
    return cv2.convertScaleAbs(frame, alpha=alpha, beta=beta)