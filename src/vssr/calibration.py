import cv2
import numpy as np

def get_clean_background(video_path, sample_frames=25):
    """
    Generates a clean background image by calculating the median of multiple frames.
    This effectively removes moving objects (like hands) from the static background.
    """
    cap = cv2.VideoCapture(video_path)
    frames = []
    
    print("Generating clean background (removing hand)...")
    
    for i in range(sample_frames * 5): # Read enough frames to sample
        ret, frame = cap.read()
        if not ret:
            break
        
        # Take every 5th frame to get variety of hand positions
        if i % 5 == 0:
            frames.append(frame)
            if len(frames) >= sample_frames:
                break
    
    cap.release()
    
    if not frames:
        print("Error: Could not read frames for background generation.")
        return None

    # Calculate the median along the time axis
    # Moving objects (hand) are outliers, so median filters them out.
    median_frame = np.median(frames, axis=0).astype(dtype=np.uint8)
    
    return median_frame

def detect_buttons_visual(frame):
    """
    Detects ROUND shapes in the frame.
    """
    # 1. Convert to Grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # 2. Blur
    blurred = cv2.GaussianBlur(gray, (9, 9), 2)
    
    # 3. Edges
    edges = cv2.Canny(blurred, 30, 150)
    
    # Dilate
    kernel = np.ones((3,3), np.uint8)
    edges = cv2.dilate(edges, kernel, iterations=1)
    
    # 4. Contours
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    detected_list = []
    height, width, _ = frame.shape
    min_area = (width * height) * 0.005
    max_area = (width * height) * 0.90

    for cnt in contours:
        area = cv2.contourArea(cnt)
        perimeter = cv2.arcLength(cnt, True)
        
        if perimeter == 0: continue
            
        if min_area < area < max_area:
            circularity = 4 * np.pi * (area / (perimeter * perimeter))
            
            if circularity > 0.7:
                x, y, w, h = cv2.boundingRect(cnt)
                aspect_ratio = float(w) / h
                if 0.8 < aspect_ratio < 1.2:
                    detected_list.append((x, y, w, h))

    detected_list.sort(key=lambda b: b[0])
    
    buttons_dict = {}
    for i, rect in enumerate(detected_list):
        name = f"BTN_{i+1}"
        buttons_dict[name] = rect
        
    return buttons_dict