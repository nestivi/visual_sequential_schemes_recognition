"""
    Utility functions for hand gesture recognition.
"""

import cv2
import mediapipe as mp
from collections import deque
from .config import BUTTONS

def draw_buttons(frame):
    """
        Drawing buttons on the frame with visual feedback.
    """
    from .state import button_states
    for name, (x, y, w, h) in BUTTONS.items():
        if button_states[name] == "pressed":
            color = (0, 255, 255)  # yellow for active
        else:
            color = (0, 255, 0)    # green for inactive
        cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
        cv2.putText(frame, name, (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

def save_sequence(sequence, filename="sequence.txt"):
    """
        Saves the sequence of clicks to a file.
    """
    try:
        with open(filename, "w", encoding="utf-8") as f:
            for click in sequence:
                f.write(f"{click}\n")
        print(f"Sequence saved to file: {filename}")
    except Exception as e:
        print(f"An error occurred while saving to file: {e}")

mp_hands = mp.solutions.hands

class FingerTracker:
    """Smooths finger position to reduce jitter."""
    
    def __init__(self, buffer_size=5):
        self.positions = deque(maxlen=buffer_size)
    
    def update(self, x, y):
        """Add new position and return smoothed average."""
        self.positions.append((x, y))
        if len(self.positions) == 0:
            return x, y
        avg_x = int(sum(p[0] for p in self.positions) / len(self.positions))
        avg_y = int(sum(p[1] for p in self.positions) / len(self.positions))
        return avg_x, avg_y
    
    def reset(self):
        """Clear all stored positions."""
        self.positions.clear()


def is_finger_pointing(hand_landmarks):
    """
    Check if index finger is extended (pointing gesture).
    
    Args:
        hand_landmarks: MediaPipe hand landmarks
        
    Returns:
        bool: True if index finger is pointing
    """
    index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
    index_pip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_PIP]
    
    # Index finger should be extended (tip above PIP joint)
    index_extended = index_tip.y < index_pip.y
    
    return index_extended


def get_pinch_distance(hand_landmarks):
    """
    Calculate distance between thumb and index finger.
    
    Args:
        hand_landmarks: MediaPipe hand landmarks
        
    Returns:
        float: Euclidean distance between thumb and index finger tips
    """
    thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
    index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
    
    distance = ((thumb_tip.x - index_tip.x)**2 + 
                (thumb_tip.y - index_tip.y)**2)**0.5
    return distance


def enhance_frame(frame, alpha=1.1, beta=10):
    """
    Improve frame quality for better hand detection.
    
    Args:
        frame: Input frame
        alpha: Contrast control (1.0-3.0)
        beta: Brightness control (0-100)
        
    Returns:
        Enhanced frame
    """
    return cv2.convertScaleAbs(frame, alpha=alpha, beta=beta)