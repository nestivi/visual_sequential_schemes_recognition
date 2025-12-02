# video.py
"""
    Video capture and display functions.
"""

import cv2
from .detection import initialize_hands, process_frame
from .utils import draw_buttons, save_sequence
from .config import VIDEO_PATH
from .state import click_sequence


def run_video():
    """
        Main function to run hand detection on video file.
    """
    # Initialize MediaPipe Hands with tuned parameters from config
    hands = initialize_hands()
    
    # Open video file
    cap = cv2.VideoCapture(VIDEO_PATH)
    
    if not cap.isOpened():
        print(f"Error: could not open video file: {VIDEO_PATH}")
        return
    
    print("Starting analysis... Press 'q' to quit.")
    
    try:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                print("End of video.")
                break
            
            # Process frame with improved detection
            frame, _ = process_frame(frame, hands)
            
            # Draw buttons on frame
            draw_buttons(frame)
            
            # Display frame
            cv2.imshow("Sequence Analyzer", frame)
            
            # Check for quit key (waitKey=5 for smoother video playback)
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