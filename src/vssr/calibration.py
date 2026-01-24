"""
Calibration and Pre-processing Module.

This module is responsible for analyzing the video input to prepare the system
for detection. It includes functionality to:
1. Generate a clean background image by removing moving objects.
2. Automatically detect interactive buttons based on their geometric shape.
"""

import cv2
import numpy as np
from typing import List, Dict, Tuple, Optional

def get_clean_background(video_path: str, sample_frames: int = 25) -> Optional[np.ndarray]:
    """
    Generates a static background image by calculating the temporal median 
    of video frames. This effectively filters out moving objects like hands.

    Args:
        video_path (str): Path to the input video file.
        sample_frames (int): Number of frames to sample for the median calculation.

    Returns:
        Optional[np.ndarray]: The generated background image (uint8), or None if failed.
    """
    cap = cv2.VideoCapture(video_path)
    frames: List[np.ndarray] = []
    
    print(f"Info: Generating clean background from {video_path}...")
    
    try:
        # We multiply by 5 to sample frames over a longer period of time,
        # ensuring we capture the background behind the moving hand.
        max_iterations = sample_frames * 5
        
        for i in range(max_iterations):
            ret, frame = cap.read()
            if not ret:
                break
            
            # Take every 5th frame to get a variety of hand positions
            if i % 5 == 0:
                frames.append(frame)
                if len(frames) >= sample_frames:
                    break
    finally:
        cap.release()
    
    if not frames:
        print("Error: Could not read frames for background generation.")
        return None

    # Calculate the median along the time axis (axis 0).
    # Moving objects are statistical outliers, so the median removes them.
    print(f"Info: Calculating median from {len(frames)} frames...")
    median_frame = np.median(frames, axis=0).astype(dtype=np.uint8)
    
    return median_frame


def detect_buttons_visual(frame: np.ndarray) -> Dict[str, Tuple[int, int, int, int]]:
    """
    Detects circular buttons in the provided image using Computer Vision techniques.

    Pipeline:
    1. Grayscale Conversion
    2. Gaussian Blur (noise reduction)
    3. Canny Edge Detection
    4. Morphological Dilation (closing gaps in edges)
    5. Contour Detection & Geometric Filtering (Area, Circularity, Aspect Ratio)

    Args:
        frame (np.ndarray): The input image (typically the clean background).

    Returns:
        Dict[str, Tuple[int, int, int, int]]: A dictionary of detected buttons.
            Format: {'BTN_1': (x, y, w, h), ...} sorted left-to-right.
    """

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (9, 9), 2)
    edges = cv2.Canny(blurred, 30, 150)
    kernel = np.ones((3, 3), np.uint8)
    edges = cv2.dilate(edges, kernel, iterations=1)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    detected_list: List[Tuple[int, int, int, int]] = []
    height, width = frame.shape[:2]
    
    # Dynamic area thresholds based on image size
    min_area = (width * height) * 0.005
    max_area = (width * height) * 0.90

    for cnt in contours:
        area = cv2.contourArea(cnt)
        perimeter = cv2.arcLength(cnt, True)
        
        if perimeter == 0:
            continue
            
        if min_area < area < max_area:
            circularity = 4 * np.pi * (area / (perimeter * perimeter))
            
            # Threshold 0.7 allows for slightly imperfect circles
            if circularity > 0.7:
                x, y, w, h = cv2.boundingRect(cnt)
                aspect_ratio = float(w) / h
                
                # Check aspect ratio (Square bounding box implies circle)
                if 0.8 < aspect_ratio < 1.2:
                    detected_list.append((x, y, w, h))

    # Sort buttons by X coordinate (Left -> Right)
    detected_list.sort(key=lambda b: b[0])
    
    # Generate dictionary with names
    buttons_dict: Dict[str, Tuple[int, int, int, int]] = {}
    for i, rect in enumerate(detected_list):
        name = f"BTN_{i+1}"
        buttons_dict[name] = rect
        
    return buttons_dict