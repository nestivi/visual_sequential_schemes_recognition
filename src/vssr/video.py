# video.py
import cv2
from .detection import initialize_hands, process_frame
from .utils import draw_buttons, save_sequence
from .config import VIDEO_PATH, BUTTONS
from .state import click_sequence, sync_button_states
from .calibration import detect_buttons_visual, get_clean_background # <--- NOWY IMPORT

def run_video():
    """
        Main function to run hand detection on video file.
    """
    # --- STEP 1: HYBRID CALIBRATION ---
    print(f"Opening video: {VIDEO_PATH}")
    
    # 1. Generate Clean Plate (Median Background)
    clean_bg = get_clean_background(VIDEO_PATH)
    
    if clean_bg is not None:
        # 2. Detect buttons on the clean image
        detected_buttons = detect_buttons_visual(clean_bg)
        
        # 3. Temporarily update BUTTONS to draw them on the preview
        BUTTONS.clear()
        BUTTONS.update(detected_buttons)
        sync_button_states() # Reset states for drawing
        
        # 4. Draw preview for the user
        preview_frame = clean_bg.copy()
        draw_buttons(preview_frame)
        
        # Add instructions text
        cv2.putText(preview_frame, "PRESS 'y' TO ACCEPT, 'q' TO QUIT", (50, 50), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        
        # 5. Manual Confirmation Loop
        print("Waiting for user confirmation...")
        accepted = False
        while True:
            cv2.imshow("CALIBRATION CHECK - Clean Background", preview_frame)
            key = cv2.waitKey(0) & 0xFF
            
            if key == ord('y'):
                accepted = True
                print("Calibration accepted by user.")
                cv2.destroyWindow("CALIBRATION CHECK - Clean Background")
                break
            elif key == ord('q'):
                print("Calibration rejected. Exiting.")
                return
        
        if not accepted:
            return
    else:
        print("Failed to generate background. Using hardcoded buttons.")

    # --- STEP 2: MAIN VIDEO LOOP ---
    
    hands = initialize_hands()
    cap = cv2.VideoCapture(VIDEO_PATH)
    
    if not cap.isOpened():
        print("Error opening video.")
        return
    
    print("Starting analysis... Press 'q' to quit.")
    
    try:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                print("End of video.")
                break
            
            frame, _ = process_frame(frame, hands)
            draw_buttons(frame)
            cv2.imshow("Sequence Analyzer", frame)
            
            if cv2.waitKey(5) & 0xFF == ord('q'):
                print("Interrupted by user.")
                break
    
    finally:
        save_sequence(click_sequence)
        cap.release()
        cv2.destroyAllWindows()
        hands.close()
        print("Analysis completed.")