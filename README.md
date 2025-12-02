# Visual Sequential Schemes Recognition (VSSR)

This project detects button clicks in a video using MediaPipe and OpenCV.

---

## Requirements

- Python **3.10** (recommended)  
- Windows OS  
- Visual C++ Build Tools (v14 or newer, for Windows)  

---

## Installation

1. **Clone or copy the project to your computer**

   ```bash
   git clone https://github.com/nestivi/visual_sequential_schemes_recognition.git
   ```

2. **Create and activate a virtual environment**

    ```bash
    python -m venv .venv
    .\.venv\Scripts\activate
    ```

3. **Install the project in editable mode**

    ```bash
    pip install -e .
    ```

4. **Check that the test video exists**

    - The test video should be located in the tests/.

    - If the file has a different name or path, update the VIDEO_FILE variable in src/vssr/config.py.

---

## Running the program

1. **Make sure the virtual environment is activated:**
    ```bash
    .\.venv\Scripts\activate
    ```

2. **Run the module:**
    ```bash
    python -m vssr
    ```
3. **Press q in the video window to quit the program.**

---

## Project Structure

```bash
visual_sequentional_schemes_recognition/
│
├─ src/
│  └─ vssr/
│     ├─ __init__.py
│     ├─ __main__.py
│     ├─ config.py
│     ├─ detection.py
│     ├─ state.py
│     ├─ utils.py
│     ├─ video.py
│
├─ tests/
│  └─ test.mp4
│
├─ .gitignore
├─ README.md
├─ main.py
└─ pyproject.toml

```

---

## Notes

The project works best with Python 3.10 on Windows.

If you encounter DLL errors with mediapipe, make sure Visual C++ Build Tools v14 or newer are installed.

You can change button coordinates and video paths in config.py.