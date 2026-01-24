"""
Utility functions for the VSSR application.

This module contains helper functions for visualization (drawing buttons),
file operations (saving results), and mathematical calculations for
finger tracking and gesture recognition.
"""

import os
import cv2
import numpy as np
import mediapipe as mp
from collections import deque
from typing import List, Tuple, Any, Optional
from .config import BUTTONS, CLICK_MECHANICS, VISUAL, RESULT_PATH
from .state import button_states, STATE_PRESSED

mp_hands = mp.solutions.hands


# --- VISUALIZATION ---

def draw_buttons(frame: np.ndarray) -> None:
    """
    Draws interactive buttons on the provided video frame.
    
    Buttons are drawn as circles. Their color changes based on the
    current state defined in `state.button_states`.

    Args:
        frame (np.ndarray): The video frame to draw on (modified in-place).
    """
    for name, (x, y, w, h) in BUTTONS.items():
        # Calculate center and radius for circular buttons
        center_x = x + w // 2
        center_y = y + h // 2
        radius = min(w, h) // 2
        
        # Determine visual style based on state
        if button_states.get(name) == STATE_PRESSED:
            color = VISUAL["click_color"]
            thickness = -1
        else:
            color = VISUAL["bbox_color_normal"]
            thickness = 2
        
        # Draw the button body
        cv2.circle(frame, (center_x, center_y), radius, color, thickness)
        
        # Draw the label above the button
        text_pos = (x, y - 10)
        cv2.putText(frame, name, text_pos,
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, VISUAL["text_color"], 2)


def enhance_frame(frame: np.ndarray, alpha: float = 1.1, beta: int = 10) -> np.ndarray:
    """
    Adjusts the brightness and contrast of the frame.
    
    Formula: output = alpha * input + beta

    Args:
        frame (np.ndarray): Input image.
        alpha (float): Contrast control (1.0-3.0). Default 1.1.
        beta (int): Brightness control (0-100). Default 10.

    Returns:
        np.ndarray: The enhanced image.
    """
    return cv2.convertScaleAbs(frame, alpha=alpha, beta=beta)


# --- FILE OPERATIONS ---

def save_sequence(sequence: List[Tuple[str, float]], filename: str = "sequence.txt") -> None:
    """
    Saves the recorded click sequence to a text file.

    Args:
        sequence (List[Tuple[str, float]]): List of (Button Name, Duration) tuples.
        filename (str): Name of the output file. Default is "sequence.txt".
    """
    try:
        os.makedirs(RESULT_PATH, exist_ok=True)
        file_path = os.path.join(RESULT_PATH, filename)
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("Button Name, Duration (s)\n")
            f.write("-" * 30 + "\n")
            
            for name, duration in sequence:
                f.write(f"{name}, {duration:.4f}\n")
                
        print(f"Sequence saved successfully to: {file_path}")
        
    except OSError as e:
        print(f"Error saving sequence file: {e}")


# --- TRACKING LOGIC ---

class FingerTracker:
    """
    Implements a moving average filter to smooth finger movements.
    This reduces jitter in the detection.
    """

    def __init__(self, buffer_size: int = 5):
        """
        Args:
            buffer_size (int): Number of frames to keep in history for averaging.
        """
        self.positions: deque = deque(maxlen=buffer_size)
    
    def update(self, x: int, y: int) -> Tuple[int, int]:
        """
        Adds a new position and returns the smoothed average.

        Args:
            x (int): Raw X coordinate.
            y (int): Raw Y coordinate.

        Returns:
            Tuple[int, int]: Smoothed (X, Y) coordinates.
        """
        self.positions.append((x, y))
        
        if not self.positions:
            return x, y
            
        avg_x = int(sum(p[0] for p in self.positions) / len(self.positions))
        avg_y = int(sum(p[1] for p in self.positions) / len(self.positions))
        
        return avg_x, avg_y
    
    def reset(self) -> None:
        """Clears the tracking history."""
        self.positions.clear()


def is_finger_pointing(hand_landmarks: Any) -> bool:
    """
    Heuristic check if the index finger is pointing up.
    
    Checks if the Index Finger Tip (8) is higher (lower Y value) 
    than the Index Finger PIP joint (6).

    Args:
        hand_landmarks: MediaPipe NormalizedLandmarkList.

    Returns:
        bool: True if pointing, False otherwise.
    """
    index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
    index_pip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_PIP]
    
    # In image coordinates, Y increases downwards.
    return index_tip.y < index_pip.y


def is_finger_clicking_z(hand_landmarks: Any) -> Tuple[bool, float]:
    """
    Determines if a click occurred based on the Z-depth of the index finger.
    
    Calculates depth relative to the wrist to account for hand distance 
    from the camera.

    Args:
        hand_landmarks: MediaPipe NormalizedLandmarkList.

    Returns:
        Tuple[bool, float]: 
            - bool: True if the depth threshold is breached (click).
            - float: The calculated relative depth value.
    """
    wrist = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST]
    index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
    
    # Calculate depth of finger tip relative to wrist
    # Negative Z usually means "closer to camera" in MediaPipe
    relative_depth = index_tip.z - wrist.z
    
    # Updated key name from 'config.py' refactor
    threshold = CLICK_MECHANICS["click_threshold_z"]
    
    is_clicking = relative_depth < threshold
    
    return is_clicking, relative_depth