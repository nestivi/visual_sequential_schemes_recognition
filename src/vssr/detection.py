import cv2
import mediapipe as mp
from collections import deque
from .config import BUTTONS, HAND_RECOGNITION, VISUAL, CLICK_MECHANICS
from .state import register_click, reset_button
from .utils import FingerTracker, is_finger_pointing, is_finger_clicking_z

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

# Global finger tracker instance
finger_tracker = FingerTracker(
    buffer_size=HAND_RECOGNITION["smoothing_buffer_size"]
)

def initialize_hands():
    return mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=1,
        min_detection_confidence=HAND_RECOGNITION["min_detection_confidence"],
        min_tracking_confidence=HAND_RECOGNITION["min_tracking_confidence"],
        model_complexity=HAND_RECOGNITION["model_complexity"]
    )

def process_frame(frame, hands):
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
        
        # Get finger position (XY)
        fingertip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
        cx = int(fingertip.x * w_frame)
        cy = int(fingertip.y * h_frame)
        
        # Apply smoothing
        if HAND_RECOGNITION["use_smoothing"]:
            cx, cy = finger_tracker.update(cx, cy)
        
        # --- CLICK DETECTION (Z-AXIS ONLY) ---
        should_click = False
        debug_info = ""
        
        if HAND_RECOGNITION["use_depth_click"]:
            is_clicking_z, current_depth = is_finger_clicking_z(hand_landmarks)
            should_click = is_clicking_z
            debug_info = f"Z-Depth: {current_depth:.3f}"
        else:
            # Fallback - always click if hand is present (for testing only)
            should_click = True

        # Draw visual feedback
        current_color = VISUAL["click_color"] if should_click else VISUAL["finger_color"]
        current_radius = VISUAL["click_radius"] if should_click else VISUAL["finger_radius"]
        
        cv2.circle(frame, (cx, cy), current_radius, current_color, -1)
        
        # Display debug info
        cv2.putText(frame, debug_info, (cx + 20, cy), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # Process button interactions
        if should_click:
            active_button = _check_button_clicks(cx, cy)
        else:
            _reset_all_buttons()
            
    else:
        finger_tracker.reset()
        _reset_all_buttons()
    
    return frame, active_button


def _check_button_clicks(cx, cy):
    active_button = False
    
    for name, (x, y, w, h) in BUTTONS.items():
        if (x < cx < x + w) and (y < cy < y + h):
            active_button = True
            register_click(name)
        else:
            reset_button(name)
    
    return active_button


def _reset_all_buttons():
    for name in BUTTONS.keys():
        reset_button(name)