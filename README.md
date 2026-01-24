# Visual Sequential Schemes Recognition (VSSR)

This project detects button clicks in a video using MediaPipe and OpenCV. It features a hybrid interface allowing for both a modern Web GUI and a classic Desktop mode.

---

## Requirements

- Python **3.10** (recommended)
- Windows OS
- Visual C++ Build Tools (v14 or newer, for Windows)
- Libraries listed in `pyproject.toml` (opencv, mediapipe, streamlit, numpy)

---

## Installation

1. **Clone or copy the project to your computer**


   ```bash
   git clone https://github.com/nestivi/visual_sequential_schemes_recognition.git
   ```

2. **Create and activate a virtual enviorment**

    ```bash
    python -m venv .venv
    .\.venv\Scripts\activate
    ```

3. **Install the project in editable mode**

    ```bash
    pip install -e .
    ```

4. **Check that the test video exists**

    - The test video should be located in the tests/ directory.
    - If the file has a different name or path, update the VIDEO_PATH variable in src/vssr/config.py.

---

## Running the program
Option 1: Web GUI (Streamlit) - Recommended

Runs the application in your browser. Allows for drag & drop video upload, automatic calibration, and result visualization.

```bash
streamlit run src/vssr/app.py
```

Option 2: Desktop Mode

Runs the analysis in a standard OpenCV window using the default video path configured in config.py.

```bash
python -m vssr
```

Press q in the video window to quit the program.

---

## Project structure

```bash
visual_sequentional_schemes_recognition/
│
├─ src/
│  └─ vssr/
│     ├─ __init__.py
│     ├─ __main__.py       # Entry point for desktop mode
│     ├─ app.py            # Streamlit Web GUI entry point
│     ├─ calibration.py    # Background generation & button detection
│     ├─ config.py         # Configuration settings
│     ├─ detection.py      # Core MediaPipe logic
│     ├─ state.py          # State management (cooldowns, sequences)
│     ├─ utils.py          # Helper functions (drawing, saving)
│     ├─ video.py          # Desktop mode logic
│
├─ tests/
│  └─ test.mp4
│
├─ .gitignore
├─ README.md
├─ TUNING_GUIDE.md
├─ main.py
└─ pyproject.toml
```

---

## Notes

- The project works best with Python 3.10 on Windows.

- If you encounter DLL errors with mediapipe, make sure Visual C++ Build Tools v14 or newer are installed.

- Tuning: If detection is too sensitive or buttons are clicked twice, refer to TUNING_GUIDE.md to adjust cooldown_frames and click_threshold_z in config.py.