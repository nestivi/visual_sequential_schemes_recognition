"""
State management module for the VSSR application.

This module maintains the global state of the application, specifically
tracking button interactions, press durations, and the resulting sequence.
It acts as the 'Memory' of the application.
"""

import time
from typing import List, Dict, Tuple
from .config import BUTTONS, CLICK_MECHANICS

# --- CONSTANTS ---
STATE_RAISED: str = "raised"
STATE_PRESSED: str = "pressed"

# --- GLOBAL STATE VARIABLES ---
click_sequence: List[Tuple[str, float]] = []
button_press_times: Dict[str, float] = {}

button_states: Dict[str, str] = {name: STATE_RAISED for name in BUTTONS}
button_cooldowns: Dict[str, int] = {name: 0 for name in BUTTONS}


# --- STATE MANAGEMENT FUNCTIONS ---

def register_click(button_name: str) -> None:
    """
    Registers the start of a button click (press down).
    
    If the button is currently in 'raised' state, it transitions to 'pressed',
    and the current timestamp is recorded.

    Args:
        button_name (str): The name of the button being interacted with.
    """
    global button_states, button_press_times, button_cooldowns
    
    # Safety check: Initialize state if new button
    if button_name not in button_states:
        button_states[button_name] = STATE_RAISED
        button_cooldowns[button_name] = 0
        
    if button_states[button_name] == STATE_RAISED and button_cooldowns[button_name] == 0:
        button_press_times[button_name] = time.time()
        button_states[button_name] = STATE_PRESSED
        print(f"CLICK STARTED: {button_name}")


def reset_button(button_name: str) -> None:
    """
    Registers the end of a button click (release).
    
    If the button was 'pressed', it transitions back to 'raised'.
    The duration of the press is calculated and appended to the `click_sequence`.

    Args:
        button_name (str): The name of the button being released.
    """
    global click_sequence, button_states, button_cooldowns
    
    if button_name not in button_states:
        return

    # Process release only if it was previously pressed
    if button_states[button_name] == STATE_PRESSED:
        start_time = button_press_times.get(button_name, time.time())
        duration = time.time() - start_time
        
        # Record the completed action
        click_sequence.append((button_name, duration))
        
        button_cooldowns[button_name] = CLICK_MECHANICS["cooldown_frames"]

        print(f"CLICK FINISHED: {button_name} ({duration:.2f}s)")
        
    button_states[button_name] = STATE_RAISED

def decrement_cooldowns() -> None:
    """
    Decreases the cooldown counter for all buttons.
    Should be called once per frame processing loop.
    """
    global button_cooldowns
    for name in button_cooldowns:
        if button_cooldowns[name] > 0:
            button_cooldowns[name] -= 1

def sync_button_states() -> None:
    """
    Synchronizes the state dictionaries with the current configuration.
    """
    global button_states, button_press_times, button_cooldowns
    
    button_states.clear()
    button_press_times.clear()
    button_cooldowns.clear()

    # Initialize all buttons to 'raised'
    for name in BUTTONS:
        button_states[name] = STATE_RAISED
        button_cooldowns[name] = 0
    
    print(f"State synchronized. Active buttons: {list(BUTTONS.keys())}")