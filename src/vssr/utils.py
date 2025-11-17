import cv2
from config import BUTTONS

def draw_buttons(frame):
    """Rysuje wszystkie przyciski z odpowiednimi kolorami."""
    from state import button_states
    for name, (x, y, w, h) in BUTTONS.items():
        if button_states[name] == "wcisniety":
            color = (0, 255, 255)  # żółty dla aktywnego
        else:
            color = (0, 255, 0)    # zielony dla nieaktywnego
        cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
        cv2.putText(frame, name, (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

def save_sequence(sequence, filename="sekwencja.txt"):
    """Zapisuje sekwencję kliknięć do pliku."""
    try:
        with open(filename, "w", encoding="utf-8") as f:
            for click in sequence:
                f.write(f"{click}\n")
        print(f"Zapisano sekwencję do pliku: {filename}")
    except Exception as e:
        print(f"Wystąpił błąd podczas zapisu do pliku: {e}")
