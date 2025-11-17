import os

# Ścieżka do pliku wideo testowego
VIDEO_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "tests", "test.mp4")
VIDEO_PATH = VIDEO_FILE

# Przyciski: "NAZWA": (x, y, szerokość, wysokość)
BUTTONS = {
    "LEWY": (300, 250, 175, 175),
    "SRODKOWY": (530, 250, 175, 175),
    "PRAWY": (775, 250, 175, 175),
}
