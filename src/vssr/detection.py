"""
Detection and Interaction Module.

This module handles the core logic of the VSSR application using MediaPipe Hands.
It processes video frames to:
1. Detect hand landmarks.
2. Track finger movements (with smoothing).
3. Recognize click gestures based on Z-axis depth.
4. Manage interactions with virtual buttons.
"""

import cv2
import numpy as np
import mediapipe as mp
from typing import Tuple, Any
from .config import BUTTONS, HAND_RECOGNITION, VISUAL
from .state import register_click, reset_button, decrement_cooldowns
from .utils import FingerTracker, is_finger_pointing, is_finger_clicking_z

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

finger_tracker = FingerTracker(
    buffer_size=HAND_RECOGNITION["smoothing_buffer_size"]
)


def initialize_hands() -> mp.solutions.hands.Hands:
    """
    Initializes and configures the MediaPipe Hands solution.

    Returns:
        mp.solutions.hands.Hands: The configured MediaPipe Hands object.
    """
    return mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=1,
        min_detection_confidence=HAND_RECOGNITION["min_detection_confidence"],
        min_tracking_confidence=HAND_RECOGNITION["min_tracking_confidence"],
        model_complexity=HAND_RECOGNITION["model_complexity"]
    )


def process_frame(frame: np.ndarray, hands: mp.solutions.hands.Hands) -> Tuple[np.ndarray, bool]:
    """
    Main processing pipeline for a single video frame.

    Pipeline:
    1. Landmark detection via MediaPipe.
    2. Gesture analysis (pointing check).
    3. Position smoothing.
    4. Click detection (Z-axis depth check).
    5. Button interaction logic.
    6. Visualization rendering.

    Args:
        frame (np.ndarray): Input video frame (BGR format).
        hands (mp.solutions.hands.Hands): Initialized MediaPipe hands object.

    Returns:
        Tuple[np.ndarray, bool]:
            - The processed frame with drawn visualizations.
            - A boolean indicating if any button is currently being interacted with.
    """

    decrement_cooldowns()

    h_frame, w_frame, _ = frame.shape
    
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(frame_rgb)
    
    active_interaction = False
    
    if results.multi_hand_landmarks:
        hand_landmarks = results.multi_hand_landmarks[0]
        
        # Draw the hand skeleton on the frame
        mp_drawing.draw_landmarks(
            frame, 
            hand_landmarks, 
            mp_hands.HAND_CONNECTIONS
        )
        
        # 1. Gesture Check
        if HAND_RECOGNITION["use_gesture_check"]:
            if not is_finger_pointing(hand_landmarks):
                finger_tracker.reset()
                _reset_all_buttons()
                return frame, False
        
        # 2. Get Index Finger Tip position
        fingertip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
        cx = int(fingertip.x * w_frame)
        cy = int(fingertip.y * h_frame)
        
        # 3. Apply smoothing to reduce jitter
        if HAND_RECOGNITION["use_smoothing"]:
            cx, cy = finger_tracker.update(cx, cy)
        
        # 4. Detect Click (Z-Axis Logic)
        should_click = False
        debug_info = ""
        
        if HAND_RECOGNITION["use_depth_click"]:
            is_clicking_z, current_depth = is_finger_clicking_z(hand_landmarks)
            should_click = is_clicking_z
            debug_info = f"Z: {current_depth:.3f}"
        else:
            should_click = True

        # 5. Visual Feedback
        if should_click:
            current_color = VISUAL["click_color"]
            current_radius = VISUAL["click_radius"]
        else:
            current_color = VISUAL["finger_color"]
            current_radius = VISUAL["finger_radius"]
        
        cv2.circle(frame, (cx, cy), current_radius, current_color, -1)
        cv2.putText(frame, debug_info, (cx + 20, cy), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, VISUAL["text_color"], 1)
        
        # 6. Button Interaction
        if should_click:
            active_interaction = _check_button_clicks(cx, cy)
        else:
            _reset_all_buttons()
            
    else:
        finger_tracker.reset()
        _reset_all_buttons()
    
    return frame, active_interaction


def _check_button_clicks(cx: int, cy: int) -> bool:
    """
    Checks if the cursor position falls within any button's bounding box.

    Args:
        cx (int): Cursor X coordinate.
        cy (int): Cursor Y coordinate.

    Returns:
        bool: True if a button was clicked, False otherwise.
    """
    is_active = False
    
    for name, (x, y, w, h) in BUTTONS.items():
        if (x < cx < x + w) and (y < cy < y + h):
            is_active = True
            register_click(name)
        else:
            reset_button(name)
    
    return is_active


def _reset_all_buttons() -> None:
    """Helper function to release all buttons."""
    for name in BUTTONS.keys():
        reset_button(name)