from .config import BUTTONS
import time

# click sequence
click_sequence = []
button_press_times = {}

# button states
button_states = {name: "raised" for name in BUTTONS}
def register_click(button_name):
    """Registers a click if the button is in the 'raised' state."""
    global click_sequence, button_states
    if button_states[button_name] == "raised":
        button_press_times[button_name] = time.time()
        button_states[button_name] = "pressed"
        print(f"CLICK DETECTED: {button_name}")

def reset_button(button_name):
    """Resets the button state when the finger is not over it."""
    if button_states[button_name] == "pressed":
        duration = time.time() - button_press_times[button_name]
        click_sequence.append((button_name, duration))
    button_states[button_name] = "raised"