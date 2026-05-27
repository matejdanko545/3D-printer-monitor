import requests
import time
from picamera2 import Picamera2
from ultralytics import YOLO
from datetime import datetime

TOKEN = "8907904146:AAGT2HpVk1HBR9BkBzUgpJtB_q__wdmNG5s"
CHAT_ID = "6010108600"

CLASSES = ["bed_not_stick", "leg_broken", "no_bottom", "no_defect", "no_support"]
DEFECT_CLASSES = ["bed_not_stick", "leg_broken", "no_bottom", "no_support"]

CONFIDENCE_THRESHOLD = 0.4
CHECK_INTERVAL = 30          # Kontrola každeho 30 sekund
STATUS_INTERVAL = 1800       # Status foto každeho 30 minut
LAST_DEFECT_SENT = 0
LAST_STATUS_SENT = 0

def send_telegram(message, image_path=None):
    try:
        if image_path:
            url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
            with open(image_path, "rb") as f:
                requests.post(url, data={"chat_id": CHAT_ID, "caption": message}, files={"photo": f})
        else:
            url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
            requests.post(url, data={"chat_id": CHAT_ID, "text": message})
    except Exception as e:
        print(f"Telegram error: {e}")

model = YOLO("/home/raspberrypi/yolo_results/printer_classifier/weights/best.pt")
picam2 = Picamera2()
time.sleep(3)
send_telegram("Bot is live and monitoring the 3D printer!")
picam2.stop()

print("Monitor started!")

while True:
    time.sleep(CHECK_INTERVAL)
    now = time.time()
    
    picam2.start()
    time.sleep(1)
    picam2.capture_file("/tmp/current.jpg")
    picam2.stop()
    
    results = model.predict("/tmp/current.jpg", verbose=False)
    pred = results[0]
    cls = int(pred.probs.top1)
    conf = float(pred.probs.top1conf)
    detected = CLASSES[cls]
    
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {detected} ({conf*100:.1f}%)")
    
    # DEFECT ALERT
    if detected in DEFECT_CLASSES and conf >= CONFIDENCE_THRESHOLD:
        if now - LAST_DEFECT_SENT > 120:
            emoji = "🔥" if detected == "bed_not_stick" else "⚠️"
            message = f"{emoji} DEFECT DETECTED!\nClass: {detected}\nConfidence: {conf*100:.1f}%"
            send_telegram(message, "/tmp/current.jpg")
            LAST_DEFECT_SENT = now
            print(f"ALERT: {detected}")
    
    # STATUS PHOTO každých 30 min
    if now - LAST_STATUS_SENT >= STATUS_INTERVAL:
        status = "OK" if detected == "no_defect" else f"DEFECT: {detected}"
        message = f"Status check - {status}\nConfidence: {conf*100:.1f}%"
        send_telegram(message, "/tmp/current.jpg")
        LAST_STATUS_SENT = now
        print(f"Status sent: {detected}")
