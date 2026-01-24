"""
Main GUI Application Module.

This module provides a web-based interface for the VSSR system using Streamlit.
It orchestrates the entire workflow:
1. Video file upload.
2. Automatic calibration (background generation and button detection).
3. Real-time analysis and sequence recording.
"""

import streamlit as st
import cv2
import tempfile
import time
from typing import Optional, List, Tuple
from vssr.calibration import get_clean_background, detect_buttons_visual
from vssr.detection import initialize_hands, process_frame
from vssr.utils import draw_buttons, save_sequence
from vssr import config
from vssr import state


st.set_page_config(
    page_title="Visual Sequential Sequence Recognition",
    layout="wide"
)

def save_uploaded_file(uploaded_file) -> Optional[str]:
    """
    Saves a Streamlit UploadedFile to a temporary file on disk.
    Required because OpenCV VideoCapture needs a file path, not a memory buffer.

    Args:
        uploaded_file: The file object returned by st.file_uploader.

    Returns:
        Optional[str]: The absolute path to the saved temporary file, or None on error.
    """
    try:
        tfile = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
        tfile.write(uploaded_file.read())
        return tfile.name
    except OSError as e:
        st.error(f"Error saving uploaded file: {e}")
        return None


def format_sequence_log(sequence: List[Tuple[str, float]]) -> str:
    """
    Formats the raw sequence data into a readable string for the UI.

    Args:
        sequence (List[Tuple[str, float]]): List of (Button Name, Duration).

    Returns:
        str: Formatted string ("1. BTN_1 [0.45s]\n").
    """
    if not sequence:
        return "Waiting for interaction..."
    
    log_lines = [
        f"{i+1}. {name} ({duration:.2f}s)" 
        for i, (name, duration) in enumerate(sequence)
    ]
    return "\n".join(log_lines)


# --- MAIN APPLICATION LOGIC ---

def main() -> None:
    """
    Main entry point for the Streamlit application.
    Manages session state and renders UI components based on the processing stage.
    """
    st.title("Visual Sequential Schemes Recognition")
    st.markdown("---")

    # --- SESSION STATE INITIALIZATION ---
    if 'processing_stage' not in st.session_state:
        # Stages: "upload" -> "calibration_ready" -> "calibration_review" -> "analysis"
        st.session_state.processing_stage = "upload"
    if 'video_path' not in st.session_state:
        st.session_state.video_path = None
    if 'detected_buttons' not in st.session_state:
        st.session_state.detected_buttons = {}
    if 'clean_bg_image' not in st.session_state:
        st.session_state.clean_bg_image = None

    # --- STEP 1: INPUT HANDLING (SIDEBAR) ---
    
    with st.sidebar:
        st.header("1. Input Wideo")
        uploaded_file = st.file_uploader("Choose video file", type=['mp4', 'avi', 'mov'])

        if uploaded_file is not None:
            # Check if this is a new file or the same one
            # Note: simplistic check; allows re-uploading the same file to reset
            current_path = st.session_state.video_path
            
            # If no path yet, or we want to overwrite
            if current_path is None:
                path = save_uploaded_file(uploaded_file)
                if path:
                    st.session_state.video_path = path
                    st.success(f"Loaded: {uploaded_file.name}")
                    st.session_state.processing_stage = "calibration_ready"
                    
                    # Reset calibration state for new file
                    st.session_state.clean_bg_image = None
                    st.session_state.detected_buttons = {}

    # --- STEP 2: CALIBRATION WORKFLOW ---
    
    if st.session_state.video_path and st.session_state.processing_stage in ["calibration_ready", "calibration_review"]:
        st.header("2. Automatic Calibration")
        
        col1, col2 = st.columns([3, 1])
        
        # Right Column: Controls
        with col2:
            st.info(
                "System will analyze the first frames of the video to remove "
                "moving objects (hand) and detect buttons on a static background."
            )
            
            if st.button("Run Calibration", type="primary"):
                with st.spinner('Generating clean background and detecting objects...'):
                    clean_bg = get_clean_background(st.session_state.video_path)
                    
                    if clean_bg is not None:
                        detected_btns = detect_buttons_visual(clean_bg)
                        
                        # Update State
                        st.session_state.clean_bg_image = clean_bg
                        st.session_state.detected_buttons = detected_btns
                        st.session_state.processing_stage = "calibration_review"
                    else:
                        st.error("Error: Failed to generate background from video.")

        # Left Column: Visualization & Confirmation
        with col1:
            if st.session_state.processing_stage == "calibration_review":
                # Create a copy for visualization to avoid modifying the original background
                preview = st.session_state.clean_bg_image.copy()
                
                # --- SYNC CONFIGURATION ---
                config.BUTTONS.clear()
                config.BUTTONS.update(st.session_state.detected_buttons)
                state.sync_button_states()

                draw_buttons(preview)
                
                preview_rgb = cv2.cvtColor(preview, cv2.COLOR_BGR2RGB)
                st.image(preview_rgb, caption="Calibration Preview", use_container_width=True)

                st.success(f"Detected objects: {len(st.session_state.detected_buttons)}")

                # Decision Buttons
                c1, c2 = st.columns(2)
                if c1.button("✅ Confirm and Proceed"):
                    st.session_state.processing_stage = "analysis"
                    st.rerun()
                
                if c2.button("❌ Reject and Restart"):
                    st.session_state.processing_stage = "calibration_ready"
                    st.rerun()

    # --- STEP 3: ANALYSIS LOOP ---

    if st.session_state.processing_stage == "analysis":
        st.header("3.Video Analysis")
        
        # UI Layout
        col_video, col_data = st.columns([2, 1])
        
        with col_data:
            st.subheader("Detected Sequence")
            sequence_placeholder = st.empty()
            status_placeholder = st.empty()
            
            st.divider()
            stop_btn = st.button("Stop Analysis")

        with col_video:
            video_placeholder = st.empty()
            progress_bar = st.progress(0)
            
            hands = initialize_hands()
            cap = cv2.VideoCapture(st.session_state.video_path)
            
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            frame_idx = 0

            # state.click_sequence.clear() 

            # Main Loop
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                
                if stop_btn:
                    status_placeholder.warning("Analysis stopped by user.")
                    break

                # --- CORE DETECTION LOGIC ---
                frame, active_btn = process_frame(frame, hands)
                
                draw_buttons(frame)
                
                # --- UI UPDATES ---
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                video_placeholder.image(frame_rgb, channels="RGB", use_container_width=True)
                
                log_text = format_sequence_log(state.click_sequence)
                sequence_placeholder.code(log_text, language="text")

                frame_idx += 1
                if total_frames > 0:
                    progress_bar.progress(min(frame_idx / total_frames, 1.0))
                
                # time.sleep(0.01)

            cap.release()
            hands.close()
            
            # Final Actions
            if not stop_btn:
                status_placeholder.success("Analysis completed successfully")
                st.balloons()
            
            st.success(f"Length of sequence: {len(state.click_sequence)}")
            

            save_sequence(state.click_sequence)
            st.info(f"Results saved to: {config.RESULT_PATH}")

            # Restart Option
            if st.button("Restart"):
                st.session_state.processing_stage = "upload"
                st.session_state.video_path = None
                state.click_sequence.clear()
                st.rerun()

if __name__ == "__main__":
    main()