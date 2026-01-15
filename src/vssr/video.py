# video.py
"""
    Video capture and display functions.
"""

import cv2
from .detection import initialize_hands, process_frame
from .utils import draw_buttons, save_sequence
from .config import VIDEO_PATH, BUTTONS
from .state import click_sequence, sync_button_states  # <--- DODANO IMPORT
from .calibration import detect_buttons_visual

def run_video():
    """
        Main function to run hand detection on video file.
    """
    # Initialize MediaPipe Hands
    hands = initialize_hands()
    
    # Open video file
    cap = cv2.VideoCapture(VIDEO_PATH)
    
    if not cap.isOpened():
        print(f"Error: could not open video file: {VIDEO_PATH}")
        return
    
    print("Starting analysis... Press 'q' to quit.")
    
    # --- AUTOMATIC CALIBRATION STEP ---
    ret, first_frame = cap.read()
    if ret:
        print("Running automatic button detection on first frame...")
        detected_buttons = detect_buttons_visual(first_frame)
        
        if detected_buttons:
            # Update the global BUTTONS dictionary
            BUTTONS.clear()
            BUTTONS.update(detected_buttons)
            
            # --- KLUCZOWA ZMIANA: ODŚWIEŻAMY STANY ---
            sync_button_states()
            # -----------------------------------------
            
            # Reset video to the beginning
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        else:
            print("Using default hardcoded buttons (Backup mode).")
            # Również synchronizujemy, na wszelki wypadek
            sync_button_states()
    # ----------------------------------
    
    try:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                print("End of video.")
                break
            
            # Process frame with detection
            frame, _ = process_frame(frame, hands)
            
            # Draw buttons on frame
            draw_buttons(frame)
            
            # Display frame
            cv2.imshow("Sequence Analyzer", frame)
            
            # Check for quit key
            if cv2.waitKey(5) & 0xFF == ord('q'):
                print("Interrupted by user.")
                break
    
    finally:
        # Save sequence and cleanup
        save_sequence(click_sequence)
        cap.release()
        cv2.destroyAllWindows()
        hands.close()
        print("Analysis completed.")