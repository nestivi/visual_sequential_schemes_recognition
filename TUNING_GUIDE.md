# Hand Recognition Tuning Guide 🎛️

## Quick Start

All tuning is done in `src/vssr/config.py` - no need to modify other files!

This system uses **Z-Axis Depth** detection (moving finger towards the camera) instead of pinch gestures.

---

## Common Issues and Solutions

### 1. Hand Not Detected / Missing Often
**Problem**: Camera doesn't see your hand reliably, or loses tracking.

**Solution** in `HAND_RECOGNITION`:
```python
HAND_RECOGNITION = {
    "min_detection_confidence": 0.5,  # Lower this (default 0.7)
    "min_tracking_confidence": 0.5,   # Lower this (default 0.7)
    # ... rest stays same
}
```

**Also try**:

    - Improve lighting in your room.
    - Ensure plain background behind hand.

### 2. Double Clicking / Bouncing

**Problem**: One physical click registers as two or three rapid clicks.

**Solution** in CLICK_MECHANICS:
```Python

CLICK_MECHANICS = {
    "cooldown_frames": 20,       # Increase this (default 15)
    # ... rest stays same
}
```

**Note**: 15 frames is approx. 0.5 seconds at 30 FPS. Increasing to 30 gives a full second of pause.

### 3. Too Sensitive (Ghost Clicks)

**Problem**: Buttons activate when you are just hovering over them, without pushing forward.

**Solution** in CLICK_MECHANICS:
```Python

CLICK_MECHANICS = {
    "click_threshold_z": -0.08,  # Make more negative (default -0.05)
    # ... rest stays same
}
```

**Logic**: Lower value (more negative) requires the finger to be closer to the camera to trigger.
### 4. Hard to Click (Unresponsive)

**Problem**: You have to push your finger very far forward to register a click.

**Solution** in CLICK_MECHANICS:
```Python

CLICK_MECHANICS = {
    "click_threshold_z": -0.03,  # Make less negative/closer to 0 (default -0.05)
    # ... rest stays same
}
```

### 5. Jittery / Shaky Cursor

**Problem**: Finger position jumps around even when holding still.

**Solution** in HAND_RECOGNITION:
```Python

HAND_RECOGNITION = {
    "use_smoothing": True,            # Ensure enabled
    "smoothing_buffer_size": 8,       # Increase (default 5)
    # ... rest stays same
}
```

### 6. Laggy / Slow Response

**Problem**: Cursor lags behind hand movement.

**Solution** in HAND_RECOGNITION:
```Python

HAND_RECOGNITION = {
    "smoothing_buffer_size": 3,       # Decrease (default 5)
    "model_complexity": 0,            # Use fastest model (default 1)
    # ... rest stays same
}
```

---

## Parameter Reference
### 1. Detection Parameters (HAND_RECOGNITION)

    min_detection_confidence: 0.5 - 0.9

        Lower = detects hand easier (but more false positives)

        Higher = strict detection (may miss hand)

        Default: 0.7

    min_tracking_confidence: 0.5 - 0.9

        Lower = faster updates (but jumpier)

        Higher = smoother tracking (but slower)

        Default: 0.7

    model_complexity: 0 or 1

        0 = Fastest, least accurate

        1 = Balanced / Accurate (default)

    use_smoothing: True / False

        Smooths finger movement using a moving average.

        Recommended: True

    smoothing_buffer_size: 3 - 10

        Higher = smoother but slower (laggy).

        Lower = faster but jumpier.

        Default: 5

    use_gesture_check: True / False

        Only allows interaction if the index finger is pointing up.

        Useful if the system detects fists or open palms as clicks.

### 2. Interaction Mechanics (CLICK_MECHANICS)

    click_threshold_z: -0.02 to -0.10

        Defines how "deep" the press must be.

        Values are relative to the wrist depth.

        -0.03: Very sensitive (light press).

        -0.08: Hard press (requires significant motion towards camera).

        Default: -0.05

    cooldown_frames: 5 - 60

        Number of frames to wait before allowing the same button to be clicked again.

        Prevents accidental double-clicks.

        Default: 15 (~0.5s)

### Recommended Presets
**Preset 1**: Default (Balanced)
```bash

HAND_RECOGNITION = {
    "min_detection_confidence": 0.7,
    "min_tracking_confidence": 0.7,
    "model_complexity": 1,
    "use_smoothing": True,
    "use_gesture_check": False,
    "use_depth_click": True,
    "smoothing_buffer_size": 5,
}
CLICK_MECHANICS = {
    "click_threshold_z": -0.05,
    "cooldown_frames": 15
}
```
**Preset 2**: High Accuracy (Prevent False Clicks)
```bash

HAND_RECOGNITION = {
    "min_detection_confidence": 0.8,
    "min_tracking_confidence": 0.8,
    "model_complexity": 1,
    "use_smoothing": True,
    "use_gesture_check": True,  # Strict gesture check
    "use_depth_click": True,
    "smoothing_buffer_size": 7,
}
CLICK_MECHANICS = {
    "click_threshold_z": -0.07, # Requires deeper press
    "cooldown_frames": 30       # Long cooldown (1s)
}
```

**Preset 3**: Fast Response (Gaming/Spamming)
```bash
HAND_RECOGNITION = {
    "min_detection_confidence": 0.6,
    "min_tracking_confidence": 0.6,
    "model_complexity": 0,      # Faster model
    "use_smoothing": True,
    "use_gesture_check": False,
    "use_depth_click": True,
    "smoothing_buffer_size": 3, # Minimal lag
}
CLICK_MECHANICS = {
    "click_threshold_z": -0.04, # Sensitive
    "cooldown_frames": 5        # Short cooldown
}
```

---

## Testing Your Changes

    - Edit src/vssr/config.py.

    - Run Desktop Mode for quick feedback: python -m vssr.

    - Check if the "Z-Depth" value on screen drops below your threshold when you press.

    - Adjust parameters if needed.