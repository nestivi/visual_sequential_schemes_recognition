import cv2
import numpy as np

def detect_buttons_visual(frame):
    """
    Detects ROUND shapes in the frame to define buttons automatically.
    Sorts them from Left to Right.
    """
    # 1. Convert to Grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # 2. Blur to remove noise
    blurred = cv2.GaussianBlur(gray, (9, 9), 2)
    
    # 3. Use Canny Edge Detection
    # You might need to tweak these numbers (30, 150) depending on lighting
    edges = cv2.Canny(blurred, 30, 150)
    
    # Dilate edges to close gaps in contours
    kernel = np.ones((3,3), np.uint8)
    edges = cv2.dilate(edges, kernel, iterations=1)
    
    # 4. Find Contours
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    detected_list = []
    
    height, width, _ = frame.shape
    min_area = (width * height) * 0.005  # Min 0.5% of screen
    max_area = (width * height) * 0.90   # Max 90% of screen

    for cnt in contours:
        area = cv2.contourArea(cnt)
        perimeter = cv2.arcLength(cnt, True)
        
        if perimeter == 0:
            continue
            
        if min_area < area < max_area:
            # Calculate Circularity
            # 1.0 = perfect circle, 0.78 = square
            circularity = 4 * np.pi * (area / (perimeter * perimeter))
            
            # Threshold: > 0.7 accepts circles and slight ovals/rounded squares
            if circularity > 0.4:
                # Get bounding box for the circle
                x, y, w, h = cv2.boundingRect(cnt)
                
                # Check aspect ratio (should be roughly 1:1 for a circle)
                aspect_ratio = float(w) / h
                if 0.8 < aspect_ratio < 1.2:
                    detected_list.append((x, y, w, h))

    # 5. Sort buttons from Left to Right
    detected_list.sort(key=lambda b: b[0])
    
    buttons_dict = {}
    if not detected_list:
        print("WARNING: No round buttons detected!")
        return {}

    print(f"Calibration successful. Detected {len(detected_list)} round buttons.")
    
    for i, rect in enumerate(detected_list):
        name = f"BTN_{i+1}"
        buttons_dict[name] = rect
        print(f" - {name}: {rect} (Circularity check passed)")
        
    return buttons_dict