from .config import BUTTONS
import time

# click sequence
click_sequence = []
button_press_times = {}

# button states
# Początkowa inicjalizacja (może być pusta, jeśli BUTTONS jest puste)
button_states = {name: "raised" for name in BUTTONS}

def register_click(button_name):
    """Registers a click if the button is in the 'raised' state."""
    global click_sequence, button_states
    
    # Zabezpieczenie na wypadek braku klucza
    if button_name not in button_states:
        button_states[button_name] = "raised"
        
    if button_states[button_name] == "raised":
        button_press_times[button_name] = time.time()
        button_states[button_name] = "pressed"
        print(f"CLICK DETECTED: {button_name}")

def reset_button(button_name):
    """Resets the button state when the finger is not over it."""
    # Zabezpieczenie na wypadek braku klucza
    if button_name not in button_states:
        return

    if button_states[button_name] == "pressed":
        duration = time.time() - button_press_times.get(button_name, time.time())
        click_sequence.append((button_name, duration))
        
    button_states[button_name] = "raised"

def sync_button_states():
    """
    Re-initializes button states after automatic detection.
    Call this function immediately after updating BUTTONS in config.
    """
    global button_states, button_press_times
    
    # Wyczyść stare stany
    button_states.clear()
    button_press_times.clear()
    
    # Załaduj nowe przyciski z (zaktualizowanego) słownika BUTTONS
    for name in BUTTONS:
        button_states[name] = "raised"
    
    print(f"State synchronized. Active buttons: {list(BUTTONS.keys())}")