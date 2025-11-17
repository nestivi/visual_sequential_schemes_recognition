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
   git clone <repository_url>
   cd visual_sequentional_schemes_recognition
   ```

2. Create and activate a virtual environment

    ```bash
    python -m venv .venv
    .\.venv\Scripts\activate
    ```

3. Update pip and setuptools

    ```bash
    python -m pip install --upgrade pip setuptools wheel
    ```

4. Check that the test video exists

    - The test video should be located in the tests/test.mp4 file.

    - If the file has a different name or path, update the VIDEO_FILE variable in src/vssr/config.py.

##################
Running the program

1. Make sure the virtual environment is activated:
    ```bash
    .\.venv\Scripts\activate
    ```

2. Run the module:
    ```bash
    python -m vssr
    ```
3. Press q in the video window to quit the program.


##################
Project Structure

```bash
visual_sequentional_schemes_recognition/
│
├─ src/
│  └─ vssr/
│     ├─ __main__.py
│     ├─ video.py
│     ├─ detection.py
│     ├─ config.py
│
├─ tests/
│  └─ test.mp4
│
├─ .venv/           # virtual environment
├─ requirements.txt
└─ README.md
```


Notes

The project works best with Python 3.10 on Windows.

If you encounter DLL errors with mediapipe, make sure Visual C++ Build Tools v14 or newer are installed.

You can change button coordinates and video paths in config.py.