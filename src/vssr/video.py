"""
Standalone Video Execution Module.

This module allows running the VSSR application without the Streamlit GUI,
using standard OpenCV windows for display. Useful for debugging or
headless execution.
"""

import cv2
import sys
from typing import NoReturn

# Local imports
from vssr.detection import initialize_hands, process_frame
from vssr.utils import draw_buttons, save_sequence
from vssr import config
from vssr import state
from vssr.calibration import detect_buttons_visual, get_clean_background

def run_video() -> None:
    """
    Main execution loop for the desktop (OpenCV-only) version of the app.
    
    Workflow:
    1. Generates clean background and detects buttons (Calibration).
    2. Asks user for confirmation via keyboard input.
    3. Runs the main analysis loop with real-time visualization.
    4. Saves the results to a file upon exit.
    """
    video_path = config.VIDEO_PATH
    print(f"Opening video: {video_path}")
    
    # --- STEP 1: HYBRID CALIBRATION ---
    
    # 1. Generate Clean Plate (Median Background)
    clean_bg = get_clean_background(video_path)
    
    if clean_bg is not None:
        # 2. Detect buttons on the clean image
        detected_buttons = detect_buttons_visual(clean_bg)
        
        # 3. Update Configuration & State
        config.BUTTONS.clear()
        config.BUTTONS.update(detected_buttons)
        state.sync_button_states() 
        
        # 4. Draw preview for the user
        preview_frame = clean_bg.copy()
        draw_buttons(preview_frame)
        
        # Add instructions text
        cv2.putText(preview_frame, "PRESS 'y' TO ACCEPT, 'q' TO QUIT", (50, 50), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        
        # 5. Manual Confirmation Loop
        print("Waiting for user confirmation (Check the popup window)...")
        accepted = False
        
        while True:
            cv2.imshow("VSSR - Calibration Check", preview_frame)
            key = cv2.waitKey(0) & 0xFF
            
            if key == ord('y'):
                accepted = True
                print("Calibration accepted.")
                cv2.destroyWindow("VSSR - Calibration Check")
                break
            elif key == ord('q'):
                print("Calibration rejected. Exiting.")
                cv2.destroyAllWindows()
                return
        
        if not accepted:
            return
    else:
        print("Warning: Failed to generate background. Using hardcoded buttons from config.")

    # --- STEP 2: MAIN VIDEO LOOP ---
    
    hands = initialize_hands()
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        print(f"Error: Could not open video file {video_path}")
        return
    
    print("Starting analysis... Press 'q' to quit.")
    
    try:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                print("End of video stream.")
                break
            
            # --- CRITICAL UPDATE: Handle Cooldowns ---
            # This was missing in your old file!
            state.decrement_cooldowns() 
            # -----------------------------------------
            
            frame, _ = process_frame(frame, hands)
            draw_buttons(frame)
            
            cv2.imshow("VSSR - Sequence Analyzer", frame)
            
            # Exit on 'q'
            if cv2.waitKey(5) & 0xFF == ord('q'):
                print("Interrupted by user.")
                break
    
    except KeyboardInterrupt:
        print("Interrupted by keyboard.")
        
    finally:
        # --- CLEANUP ---
        save_sequence(state.click_sequence)
        cap.release()
        cv2.destroyAllWindows()
        hands.close()
        print("Analysis completed.")

if __name__ == "__main__":
    run_video()