import cv2
import numpy as np
import requests
import time
from picamera2 import Picamera2

# ===================================
# TELEGRAM SETTINGS
# ===================================

BOT_TOKEN = '8501659678:AAHx1IeNKd--QIFSC2WI_A9IU3O8IbdWUdQ'
CHAT_ID = '6041020631'

# ===================================
# CAMERA SETUP
# ===================================

picam2 = Picamera2()

config = picam2.create_preview_configuration(
    main={"size": (1280, 720)}
)

picam2.configure(config)
picam2.start()

time.sleep(2)

# ===================================
# TELEGRAM FUNCTIONS
# ===================================

def send_message(text):

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    data = {
        "chat_id": CHAT_ID,
        "text": text
    }

    requests.post(url, data=data)

def send_photo(image_path, caption=""):

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"

    with open(image_path, "rb") as photo:

        files = {
            "photo": photo
        }

        data = {
            "chat_id": CHAT_ID,
            "caption": caption
        }

        requests.post(url, files=files, data=data)

# ===================================
# FAILURE DETECTION
# ===================================

def detect_failure(frame):

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect edges
    edges = cv2.Canny(gray, 50, 150)

    # Count edge pixels
    edge_pixels = np.sum(edges > 0)

    print("Edge pixels:", edge_pixels)

    # ===================================
    # FAILURE THRESHOLD
    # ===================================

    # Large messy edge count usually means:
    # spaghetti
    # detached print
    # nozzle blob

    if edge_pixels > 50000:
        return True

    return False

# ===================================
# START
# ===================================

send_message("🚀 Raspberry Pi 5 printer monitor started.")

print("Monitoring started...")

start_time = time.time()

failure_detected = False

# ===================================
# MAIN LOOP
# ===================================

while True:

    # Capture frame
    frame = picam2.capture_array()

    # Convert color
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

    # Save image
    cv2.imwrite("current.jpg", frame)

    # Detect failure
    failed = detect_failure(frame)

    # ===================================
    # FAILURE
    # ===================================

    if failed and not failure_detected:

        failure_detected = True

        send_photo(
            "current.jpg",
            "❌ PRINT FAILURE DETECTED"
        )

        print("Failure detected")

        break

    # ===================================
    # SUCCESS
    # ===================================

    # Example:
    # assume print completes after 2 hours
    # Change this later if needed

    elapsed = time.time() - start_time

    if elapsed > 7200 and not failure_detected:

        send_photo(
            "current.jpg",
            "✅ SUCCESSFUL PRINT"
        )

        print("Print successful")

        break

    # Wait before next scan
    time.sleep(20)