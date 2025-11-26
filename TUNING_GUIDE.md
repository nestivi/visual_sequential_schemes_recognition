# Hand Recognition Tuning Guide

## Quick Start

All tuning is done in `config.py` - no need to modify other files!

## Common Issues and Solutions

### 1. Hand Not Detected / Missing Often
**Problem**: Camera doesn't see your hand reliably

**Solution** in `config.py`:
```python
HAND_RECOGNITION = {
    "min_detection_confidence": 0.5,  # Lower this (was 0.7)
    "min_tracking_confidence": 0.5,   # Lower this (was 0.6)
    # ... rest stays same
}
```

**Also try**:
- Improve lighting in your room
- Move hand closer to camera
- Ensure plain background behind hand

---

### 2. Too Many False Clicks / Too Sensitive
**Problem**: Buttons activate when you don't want them to

**Solution** in `config.py`:
```python
HAND_RECOGNITION = {
    "min_detection_confidence": 0.8,  # Increase (was 0.7)
    "use_gesture_check": True,        # Enable (was False)
    "use_pinch": True,                # Enable (was False)
    "pinch_threshold": 0.04,          # Lower = harder to trigger
    # ... rest stays same
}
```

---

### 3. Jittery / Shaky Cursor
**Problem**: Finger position jumps around

**Solution** in `config.py`:
```python
HAND_RECOGNITION = {
    "min_tracking_confidence": 0.8,   # Increase (was 0.6)
    "use_smoothing": True,            # Ensure enabled
    "smoothing_buffer_size": 8,       # Increase (was 5)
    # ... rest stays same
}
```

---

### 4. Too Slow to Respond
**Problem**: Cursor lags behind hand movement

**Solution** in `config.py`:
```python
HAND_RECOGNITION = {
    "smoothing_buffer_size": 3,       # Decrease (was 5)
    "min_tracking_confidence": 0.5,   # Lower (was 0.6)
    "model_complexity": 0,            # Use fastest model
    # ... rest stays same
}
```

---

### 5. Want Click-Like Behavior
**Problem**: Want to "click" buttons instead of just hovering

**Solution** in `config.py`:
```python
HAND_RECOGNITION = {
    "use_pinch": True,                # Enable pinch-to-click
    "pinch_threshold": 0.05,          # Adjust sensitivity
    # ... rest stays same
}
```

Adjust `pinch_threshold`:
- `0.03` - Very tight pinch required
- `0.05` - Normal (default)
- `0.08` - Easy to trigger

---

### 6. Want Pointing Gesture Only
**Problem**: Only want to detect when finger is pointing

**Solution** in `config.py`:
```python
HAND_RECOGNITION = {
    "use_gesture_check": True,        # Enable gesture check
    # ... rest stays same
}
```

Now it only works when index finger is extended (pointing).

---

## Parameter Reference

### Detection Parameters
- **min_detection_confidence**: `0.5` - `0.9`
  - Lower = detects hand easier (but more false positives)
  - Higher = more reliable (but may miss hand)
  - Default: `0.7`

- **min_tracking_confidence**: `0.5` - `0.9`
  - Lower = faster updates (but jumpier)
  - Higher = smoother tracking (but slower)
  - Default: `0.6`

- **model_complexity**: `0`, `1`, or `2`
  - `0` = Fastest, least accurate
  - `1` = Balanced (default)
  - `2` = Most accurate, slowest

### Feature Toggles
- **use_smoothing**: `True` / `False`
  - Smooths finger movement
  - Recommended: `True`

- **use_gesture_check**: `True` / `False`
  - Only detect when finger is pointing
  - Use if getting false detections

- **use_pinch**: `True` / `False`
  - Require pinch gesture to click
  - Good for preventing accidental clicks

### Smoothing
- **smoothing_buffer_size**: `3` - `10`
  - Higher = smoother but slower
  - Lower = faster but jumpier
  - Default: `5`

### Pinch Detection
- **pinch_threshold**: `0.03` - `0.08`
  - Lower = tighter pinch needed
  - Higher = easier to trigger
  - Default: `0.05`

---

## Recommended Presets

### Preset 1: Default (Balanced)
```python
HAND_RECOGNITION = {
    "min_detection_confidence": 0.7,
    "min_tracking_confidence": 0.6,
    "model_complexity": 1,
    "use_smoothing": True,
    "use_gesture_check": False,
    "use_pinch": False,
    "smoothing_buffer_size": 5,
    "pinch_threshold": 0.05,
}
```

### Preset 2: High Accuracy (Prevent False Clicks)
```python
HAND_RECOGNITION = {
    "min_detection_confidence": 0.8,
    "min_tracking_confidence": 0.7,
    "model_complexity": 2,
    "use_smoothing": True,
    "use_gesture_check": True,
    "use_pinch": True,
    "smoothing_buffer_size": 6,
    "pinch_threshold": 0.04,
}
```

### Preset 3: Fast Response (Gaming)
```python
HAND_RECOGNITION = {
    "min_detection_confidence": 0.6,
    "min_tracking_confidence": 0.5,
    "model_complexity": 0,
    "use_smoothing": True,
    "use_gesture_check": False,
    "use_pinch": False,
    "smoothing_buffer_size": 3,
    "pinch_threshold": 0.05,
}
```

### Preset 4: Poor Lighting
```python
HAND_RECOGNITION = {
    "min_detection_confidence": 0.5,
    "min_tracking_confidence": 0.5,
    "model_complexity": 1,
    "use_smoothing": True,
    "use_gesture_check": False,
    "use_pinch": False,
    "smoothing_buffer_size": 7,
    "pinch_threshold": 0.05,
}
```

---

## Testing Your Changes

1. Edit `config.py`
2. Run: `python -m src.vssr`
3. Test hand detection
4. Adjust parameters if needed
5. Repeat until satisfied

**Tip**: Change one parameter at a time to understand its effect!