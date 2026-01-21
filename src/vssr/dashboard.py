import streamlit as st
import cv2
import tempfile
import time
import os
import sys

# Dodajemy ścieżkę src do systemu
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Importy z Twojego projektu
try:
    from vssr.detection import initialize_hands, process_frame
    from vssr.calibration import detect_buttons_visual
    import vssr.config as cfg
    # POPRAWKA: Usunięto _reset_all_buttons z importu poniżej
    from vssr.state import sync_button_states, click_sequence, button_states
    from vssr.utils import draw_buttons
except ImportError as e:
    st.error(f"Błąd importu: {e}. Upewnij się, że plik dashboard.py jest w folderze głównym projektu.")
    st.stop()

# --- KONFIGURACJA STRONY ---
st.set_page_config(page_title="VSSR Control Panel", layout="wide")

st.title("🖐️ VSSR: Panel Sterowania")
st.markdown("Interfejs do testowania detekcji przycisków i mechaniki kliknięć.")

# --- SIDEBAR: KONFIGURACJA ---
st.sidebar.header("⚙️ Ustawienia")

# 1. Ustawienia Głębi (Kliknięcia)
st.sidebar.subheader("1. Czułość Kliknięcia")
click_thresh = st.sidebar.slider(
    "Próg głębi (Click Threshold)", 
    min_value=-0.15, 
    max_value=0.05, 
    value=cfg.CLICK_MECHANICS["click_depth_threshold"],
    step=0.01,
    help="Im bliżej zera lub wartości dodatnich, tym lżejsze dotknięcie jest wymagane."
)
hitbox_scale = st.sidebar.slider(
    "Rozmiar Hitboxa", 
    min_value=1.0, 
    max_value=2.5, 
    value=cfg.CLICK_MECHANICS.get("hitbox_scale_factor", 1.4),
    step=0.1,
    help="Jak duży jest obszar aktywny przycisku (1.0 = rozmiar kółka)."
)

# 2. Ustawienia AI
st.sidebar.subheader("2. Parametry AI")
min_conf = st.sidebar.slider(
    "Min. Pewność Detekcji", 
    0.1, 1.0, 
    cfg.HAND_RECOGNITION["min_detection_confidence"]
)

# 3. Kalibracja
st.sidebar.subheader("3. Kalibracja")
auto_calib = st.sidebar.checkbox("Automatyczne wykrywanie przycisków", value=True)

# --- AKTUALIZACJA KONFIGURACJI NA ŻYWO ---
cfg.CLICK_MECHANICS["click_depth_threshold"] = click_thresh
cfg.CLICK_MECHANICS["hitbox_scale_factor"] = hitbox_scale
cfg.HAND_RECOGNITION["min_detection_confidence"] = min_conf

# --- GŁÓWNY WIDOK ---

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Wideo")
    video_file = st.file_uploader("Wgraj plik wideo (MP4)", type=['mp4', 'mov', 'avi'])
    st_frame = st.empty()

with col2:
    st.subheader("Status")
    status_text = st.empty()
    st.markdown("---")
    st.subheader("Wykryta Sekwencja")
    sequence_container = st.container()
    
    st.markdown("---")
    run_btn = st.button("▶️ URUCHOM ANALIZĘ", type="primary", use_container_width=True)

# --- LOGIKA APLIKACJI ---

if run_btn and video_file is not None:
    tfile = tempfile.NamedTemporaryFile(delete=False) 
    tfile.write(video_file.read())
    
    cap = cv2.VideoCapture(tfile.name)
    hands = initialize_hands()
    
    # Reset stanów
    cfg.BUTTONS.clear()
    click_sequence.clear()
    
    # --- KALIBRACJA ---
    if auto_calib:
        status_text.info("⏳ Kalibracja...")
        ret, first_frame = cap.read()
        if ret:
            detected = detect_buttons_visual(first_frame)
            if detected:
                cfg.BUTTONS.update(detected)
                sync_button_states()
                st.toast(f"✅ Skalibrowano: {len(detected)} przycisków")
            else:
                st.error("❌ Nie wykryto przycisków!")
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
    else:
        sync_button_states()

    status_text.success("🚀 Analiza w toku...")
    
    # --- PĘTLA GŁÓWNA ---
    stop_btn = st.button("Stop")
    
    frame_placeholder = st.empty()
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
            
        try:
            results = process_frame(frame, hands)
            processed_frame = results[0] 
            
        except Exception as e:
            st.error(f"Błąd przetwarzania: {e}")
            break

        draw_buttons(processed_frame)
        
        frame_rgb = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)
        st_frame.image(frame_rgb, channels="RGB", use_container_width=True)
        
        with sequence_container:
            if click_sequence:
                st.info(" -> ".join([item[0] for item in click_sequence]))
            else:
                st.text("Czekam na kliknięcia...")

    cap.release()
    hands.close()
    status_text.info("🏁 Koniec nagrania.")
    st.balloons()

elif run_btn and video_file is None:
    st.warning("⚠️ Najpierw wgraj plik wideo powyżej!")