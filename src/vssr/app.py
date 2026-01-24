import streamlit as st
import cv2
import tempfile
import os
import time
from vssr.calibration import get_clean_background, detect_buttons_visual
from vssr.detection import initialize_hands, process_frame
from vssr.utils import draw_buttons
from vssr import config
from vssr import state

# Konfiguracja strony
st.set_page_config(
    page_title="Detekcja Sekwencji",
    layout="wide"
)

# --- FUNKCJE POMOCNICZE ---

def save_uploaded_file(uploaded_file):
    """Zapisuje wgrany plik do folderu tymczasowego, aby OpenCV mógł go otworzyć."""
    try:
        tfile = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
        tfile.write(uploaded_file.read())
        return tfile.name
    except Exception as e:
        st.error(f"Błąd zapisu pliku: {e}")
        return None

# --- GŁÓWNA APLIKACJA ---

def main():
    st.title("Visual Sequential Schemes Recognition")
    st.markdown("---")

    # Inicjalizacja stanu (Session State)
    if 'processing_stage' not in st.session_state:
        st.session_state.processing_stage = "upload" # upload -> calibration -> analysis -> done
    if 'video_path' not in st.session_state:
        st.session_state.video_path = None
    if 'detected_buttons' not in st.session_state:
        st.session_state.detected_buttons = {}
    if 'clean_bg_image' not in st.session_state:
        st.session_state.clean_bg_image = None

    # --- KROK 1: WGRYWANIE PLIKU ---
    
    with st.sidebar:
        st.header("1. Dane wejściowe")
        uploaded_file = st.file_uploader("Wybierz plik wideo", type=['mp4', 'avi', 'mov'])

        if uploaded_file is not None:
            # Zapisz plik tylko jeśli jeszcze tego nie zrobiono lub zmieniono plik
            if st.session_state.video_path is None:
                path = save_uploaded_file(uploaded_file)
                st.session_state.video_path = path
                st.success(f"Wczytano: {uploaded_file.name}")
                st.session_state.processing_stage = "calibration_ready"

    # --- KROK 2: KALIBRACJA (Ukrywanie ręki i detekcja przycisków) ---
    
    if st.session_state.video_path and st.session_state.processing_stage in ["calibration_ready", "calibration_review"]:
        st.header("2. Kalibracja Automatyczna")
        
        col1, col2 = st.columns([3, 1])
        
        with col2:
            st.info("System przeanalizuje pierwsze klatki, aby usunąć rękę i wykryć przyciski.")
            if st.button("Uruchom Kalibrację", type="primary"):
                with st.spinner('Generowanie czystego tła i detekcja...'):
                    # 1. Twoja funkcja usuwania ręki
                    clean_bg = get_clean_background(st.session_state.video_path)
                    
                    if clean_bg is not None:
                        # 2. Twoja funkcja detekcji przycisków
                        detected_btns = detect_buttons_visual(clean_bg)
                        
                        st.session_state.clean_bg_image = clean_bg
                        st.session_state.detected_buttons = detected_btns
                        st.session_state.processing_stage = "calibration_review"
                    else:
                        st.error("Nie udało się wygenerować tła.")

        with col1:
            # Wyświetlanie podglądu kalibracji
            if st.session_state.processing_stage == "calibration_review":
                # Kopia obrazu do rysowania podglądu
                preview = st.session_state.clean_bg_image.copy()
                
                # Aktualizujemy globalny config (ważne, bo utils.draw_buttons korzysta z config.BUTTONS)
                config.BUTTONS.clear()
                config.BUTTONS.update(st.session_state.detected_buttons)
                state.sync_button_states()
                
                # Rysujemy przyciski używając Twojej funkcji
                draw_buttons(preview)
                
                # Konwersja BGR -> RGB dla Streamlit
                preview_rgb = cv2.cvtColor(preview, cv2.COLOR_BGR2RGB)
                st.image(preview_rgb, caption="Wykryte przyciski na czystym tle", use_container_width=True)
                
                st.write(f"Wykryto przycisków: {len(st.session_state.detected_buttons)}")
                
                # Przyciski akceptacji
                c1, c2 = st.columns(2)
                if c1.button("✅ Zatwierdź i Analizuj"):
                    st.session_state.processing_stage = "analysis"
                    st.rerun()
                if c2.button("❌ Odrzuć i Spróbuj Ponownie"):
                    st.session_state.processing_stage = "calibration_ready"
                    st.rerun()

    # --- KROK 3: ANALIZA SEKWENCJI ---

    if st.session_state.processing_stage == "analysis":
        st.header("3. Analiza Wideo")
        
        # Resetujemy stan sekwencji przed analizą
        state.click_sequence.clear()
        
        col_video, col_data = st.columns([2, 1])
        
        with col_data:
            st.subheader("Wykryta Sekwencja")
            # Placeholder na listę sekwencji
            sequence_container = st.empty()
            # Placeholder na status
            status_container = st.empty()
            
            stop_btn = st.button("Zatrzymaj Analizę")

        with col_video:
            video_placeholder = st.empty()
            
            # Inicjalizacja Twoich rąk MediaPipe
            hands = initialize_hands()
            cap = cv2.VideoCapture(st.session_state.video_path)
            
            progress_bar = st.progress(0)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            frame_idx = 0
            
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                
                if stop_btn:
                    status_container.warning("Zatrzymano przez użytkownika.")
                    break

                # --- TWOJA LOGIKA DETEKCJI ---
                # Przetwarzanie klatki
                frame, active_btn = process_frame(frame, hands)
                
                # Rysowanie przycisków
                draw_buttons(frame)
                
                # --- WIZUALIZACJA W STREAMLIT ---
                # Streamlit używa RGB, OpenCV używa BGR
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                video_placeholder.image(frame_rgb, channels="RGB", use_container_width=True)
                
                # Aktualizacja paska bocznego z wynikami
                sequence_container.code(str(state.click_sequence))
                
                # Pasek postępu
                frame_idx += 1
                if total_frames > 0:
                    progress_bar.progress(min(frame_idx / total_frames, 1.0))
                
                # Opcjonalne spowolnienie, żeby nie działało za szybko dla oka (opcjonalne)
                # time.sleep(0.01)

            cap.release()
            hands.close()
            
            status_container.success("Analiza zakończona!")
            st.balloons()
            
            # Wyniki końcowe
            st.success(f"Finalna sekwencja: {state.click_sequence}")
            
            # Przycisk restartu
            if st.button("Rozpocznij od nowa"):
                st.session_state.processing_stage = "upload"
                st.session_state.video_path = None
                st.rerun()

if __name__ == "__main__":
    main()