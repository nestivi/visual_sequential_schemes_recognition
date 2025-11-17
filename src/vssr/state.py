from config import BUTTONS

# Sekwencja kliknięć
click_sequence = []

# Stan przycisków
button_states = {name: "podniesiony" for name in BUTTONS}

def register_click(button_name):
    """Rejestruje kliknięcie, jeśli przycisk jest w stanie 'podniesiony'."""
    global click_sequence, button_states
    if button_states[button_name] == "podniesiony":
        click_sequence.append(button_name)
        button_states[button_name] = "wcisniety"
        print(f"WYKRYTO KLIKNIĘCIE: {button_name}")

def reset_button(button_name):
    """Resetuje stan przycisku, gdy palec nie jest nad nim."""
    button_states[button_name] = "podniesiony"
