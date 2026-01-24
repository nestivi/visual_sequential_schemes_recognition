import os

"""
    Configuration settings for hand recognition and buttons.
"""

# Path to file
VIDEO_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "tests", "test4.mp4")
VIDEO_PATH = VIDEO_FILE
RESULT_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "results")

# Button definitions (x, y, width, height)
BUTTONS = {
    "LEWY": (300, 200, 175, 175),
    "SRODKOWY": (550, 200, 175, 175),
    "PRAWY": (800, 200, 175, 175),
}

# Hand recognition tuning parameters
HAND_RECOGNITION = {
    # MediaPipe Hands parameters
    "min_detection_confidence": 0.7,
    "min_tracking_confidence": 0.7,
    "model_complexity": 1,
    
    # Feature toggles
    "use_smoothing": True,
    "use_gesture_check": False,
    "use_depth_click": True,    # Główna metoda: oś Z
    
    # Smoothing parameters
    "smoothing_buffer_size": 5,
}

# Mechanika kliknięć
CLICK_MECHANICS = {
    # Progi dla osi Z (głębia). 
    # Wartość np. -0.05 oznacza próg wciśnięcia względem nadgarstka.
    "click_depth_threshold": -0.05, 
    "click_cooldown": 0.5
}

# Visual settings
VISUAL = {
    "finger_color": (0, 0, 255),       # BGR: Czerwony (brak kliknięcia)
    "finger_radius": 10,
    "click_color": (0, 255, 255),      # BGR: Żółty (kliknięcie)
    "click_radius": 15,                # Zastąpiło pinch_radius
}