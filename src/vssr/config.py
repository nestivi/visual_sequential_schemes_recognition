"""
Configuration module for the VSSR application.

This module contains constant definitions, file paths, and tuning parameters
used throughout the Visual Sequential Schemes Recognition system.
"""

import os
from typing import Dict, Tuple, Any

# --- PATH CONFIGURATION ---
BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
VIDEO_PATH: str = os.path.join(BASE_DIR, "tests", "test4.mp4")
RESULT_PATH: str = os.path.join(BASE_DIR, "results")


# --- BUTTON CONFIGURATION ---
# Note: These values might be overwritten by the calibration process.
BUTTONS: Dict[str, Tuple[int, int, int, int]] = {
    "LEWY": (300, 200, 175, 175),
    "SRODKOWY": (550, 200, 175, 175),
    "PRAWY": (800, 200, 175, 175),
}


# --- DETECTION TUNING ---
HAND_RECOGNITION: Dict[str, Any] = {
    # MediaPipe confidence thresholds (0.0 - 1.0)
    "min_detection_confidence": 0.7,
    "min_tracking_confidence": 0.7,
    "model_complexity": 1,  # 0 or 1 (1 is more accurate but slower)
    
    # Feature toggles
    "use_smoothing": True,      # Enable cursor movement smoothing
    "use_gesture_check": False, # Enable gesture validation (e.g., pointing finger)
    "use_depth_click": True,    # Use Z-axis depth for click detection
    
    # Smoothing parameters
    "smoothing_buffer_size": 5, # Number of frames for moving average
}


# --- INTERACTION MECHANICS ---
CLICK_MECHANICS: Dict[str, Any] = {
    # Z-axis threshold relative to the wrist.
    "click_threshold_z": -0.05, 
    
    # Number of frames to wait before registering another click on the same button.
    "cooldown_frames": 15 
}


# --- VISUAL SETTINGS ---
# Colors (BGR format) and dimensions for UI elements.
VISUAL: Dict[str, Any] = {
    "finger_color": (0, 0, 255),    # Red (Idle state)
    "finger_radius": 10,
    "click_color": (0, 255, 255),   # Yellow (Active click)
    "click_radius": 15,
    "text_color": (255, 255, 255),  # White
    "bbox_color_normal": (0, 255, 0), # Green
    "bbox_color_active": (0, 0, 255), # Red
}