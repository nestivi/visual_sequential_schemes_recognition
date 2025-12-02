import os


"""
    Configuration settings for hand recognition and buttons.
"""

# Path to file
VIDEO_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "tests", "test3.mp4")
VIDEO_PATH = VIDEO_FILE

# Button definitions (x, y, width, height)
BUTTONS = {
    "LEWY": (300, 250, 175, 175),
    "SRODKOWY": (530, 250, 175, 175),
    "PRAWY": (775, 250, 175, 175),
    # Add your buttons here
}

# Hand recognition tuning parameters
HAND_RECOGNITION = {
    # MediaPipe Hands parameters
    "min_detection_confidence": 0.7,  # 0.5-0.9: Higher = more reliable detection
    "min_tracking_confidence": 0.7,   # 0.5-0.9: Higher = smoother tracking
    "model_complexity": 1,             # 0=fast, 1=balanced, 2=accurate
    
    # Feature toggles
    "use_smoothing": True,             # Smooth finger position to reduce jitter
    "use_gesture_check": False,        # Require pointing finger gesture
    "use_pinch": False,                # Require pinch gesture for clicks
    
    # Smoothing parameters
    "smoothing_buffer_size": 5,        # 3-10: Higher = smoother but slower response
    
    # Pinch detection
    "pinch_threshold": 0.05,           # 0.03-0.08: Distance for pinch detection
}

# Visual settings
VISUAL = {
    "finger_color": (0, 0, 255),       # BGR: Red circle for finger
    "finger_radius": 10,
    "pinch_color": (0, 255, 0),        # BGR: Green circle when pinching
    "pinch_radius": 15,
}