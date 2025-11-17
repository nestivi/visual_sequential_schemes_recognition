import cv2
from detection import process_frame
from utils import draw_buttons, save_sequence
from config import VIDEO_PATH
from state import click_sequence
import mediapipe as mp

def run_video():
    hands = mp.solutions.hands.Hands(
        static_image_mode=False,
        max_num_hands=1,
        min_detection_confidence=0.1,
        min_tracking_confidence=0.1
    )

    cap = cv2.VideoCapture(VIDEO_PATH)
    if not cap.isOpened():
        print(f"Błąd: Nie można otworzyć pliku wideo: {VIDEO_PATH}")
        return

    print("Rozpoczynam analizę... Naciśnij 'q', aby przerwać.")

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("Koniec wideo.")
            break

        frame, _ = process_frame(frame, hands)
        draw_buttons(frame)
        cv2.imshow("Analizator Sekwencji", frame)

        if cv2.waitKey(5) & 0xFF == ord('q'):
            print("Przerwano przez użytkownika.")
            break

    save_sequence(click_sequence)
    cap.release()
    cv2.destroyAllWindows()
    hands.close()
