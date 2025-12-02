import cv2
import mediapipe as mp
from collections import deque
from .config import BUTTONS, HAND_RECOGNITION, VISUAL
from .state import register_click, reset_button
from .utils import FingerTracker, is_finger_pointing, get_pinch_distance

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

# Global finger tracker instance
finger_tracker = FingerTracker(
    buffer_size=HAND_RECOGNITION["smoothing_buffer_size"]
)


def initialize_hands():
    """
    Initialize MediaPipe Hands with parameters from config.
    
    Returns:
        mp.solutions.hands.Hands: Configured Hands object
    """
    return mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=1,
        min_detection_confidence=HAND_RECOGNITION["min_detection_confidence"],
        min_tracking_confidence=HAND_RECOGNITION["min_tracking_confidence"],
        model_complexity=HAND_RECOGNITION["model_complexity"]
    )


def process_frame(frame, hands):
    """
    Process a single frame, detect hand and register clicks.
    
    Args:
        frame: Input frame from camera
        hands: MediaPipe Hands object
        
    Returns:
        tuple: (processed_frame, active_button)
            - processed_frame: Frame with overlays
            - active_button: True if any button is active
    """
    h_frame, w_frame, _ = frame.shape
    
    # Convert to RGB for MediaPipe
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(frame_rgb)
    
    active_button = False
    
    if results.multi_hand_landmarks:
        hand_landmarks = results.multi_hand_landmarks[0]
        
        # Draw hand landmarks
        mp_drawing.draw_landmarks(
            frame, 
            hand_landmarks, 
            mp_hands.HAND_CONNECTIONS
        )
        
        # Check gesture if enabled
        if HAND_RECOGNITION["use_gesture_check"]:
            if not is_finger_pointing(hand_landmarks):
                finger_tracker.reset()
                _reset_all_buttons()
                return frame, active_button
        
        # Get finger position
        fingertip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
        cx = int(fingertip.x * w_frame)
        cy = int(fingertip.y * h_frame)
        
        # Apply smoothing if enabled
        if HAND_RECOGNITION["use_smoothing"]:
            cx, cy = finger_tracker.update(cx, cy)
        
        # Check for click condition
        should_click = True
        
        if HAND_RECOGNITION["use_pinch"]:
            pinch_distance = get_pinch_distance(hand_landmarks)
            should_click = pinch_distance < HAND_RECOGNITION["pinch_threshold"]
            
            # Draw visual feedback
            if should_click:
                cv2.circle(
                    frame, 
                    (cx, cy), 
                    VISUAL["pinch_radius"], 
                    VISUAL["pinch_color"], 
                    2
                )
        
        # Draw finger position
        cv2.circle(
            frame, 
            (cx, cy), 
            VISUAL["finger_radius"], 
            VISUAL["finger_color"], 
            -1
        )
        
        # Process button interactions
        if should_click:
            active_button = _check_button_clicks(cx, cy)
        else:
            _reset_all_buttons()
            
    else:
        # No hand detected
        finger_tracker.reset()
        _reset_all_buttons()
    
    return frame, active_button


def _check_button_clicks(cx, cy):
    """
    Check if finger position is over any button.
    
    Args:
        cx: X coordinate of finger
        cy: Y coordinate of finger
        
    Returns:
        bool: True if any button is active
    """
    active_button = False
    
    for name, (x, y, w, h) in BUTTONS.items():
        if (x < cx < x + w) and (y < cy < y + h):
            active_button = True
            register_click(name)
        else:
            reset_button(name)
    
    return active_button


def _reset_all_buttons():
    """Reset all buttons to inactive state."""
    for name in BUTTONS.keys():
        reset_button(name)