import cv2
import numpy as np
import mss
import pygetwindow as gw
import keyboard
import serial
import time
import win32api
from ultralytics import YOLO

# ======== AYARLAR ========
HEADSHOT_CLASS_KEYWORD = "headshot"
MODEL_PATH = "my_yolo_model.pt"
SERIAL_PORT = "COM15"
BAUD_RATE = 9600
# ==========================

# Caps Lock açık mı kontrolü
def is_capslock_on():
    return win32api.GetKeyState(0x14) == 1

# YOLO modeli yükleniyor
print("[+] Model yükleniyor...")
model = YOLO(MODEL_PATH)

# Arduino'ya bağlan
print(f"[+] Arduino ({SERIAL_PORT}) portuna bağlanılıyor...")
arduino = serial.Serial(SERIAL_PORT, BAUD_RATE)
time.sleep(2)
arduino.write(b"TEST\n")  # Test mesajı
print("[✓] Arduino'ya test verisi gönderildi.\n")

# Açık pencereleri al ve listele
windows = gw.getWindowsWithTitle("")
print("[!] Açık Pencereler:")
for i, w in enumerate(windows):
    print(f"{i}: {w.title}")

# Kullanıcıdan pencere seçimi
index = int(input("\n[?] İnference yapmak istediğin pencerenin numarasını gir: "))
selected_window = windows[index]

# Pencere boyut bilgisi
left, top = selected_window.left, selected_window.top
width, height = selected_window.width, selected_window.height
print(f"[i] Seçilen Pencere: {selected_window.title}")
print(f"[i] Konum ve Boyut: left={left}, top={top}, width={width}, height={height}\n")

monitor = {"top": top, "left": left, "width": width, "height": height}
sct = mss.mss()

print("[*] Başladı. 'q' tuşuyla çıkabilirsin. Caps Lock açıkken headshot tespiti yapılırsa koordinat gönderilir.\n")

while True:
    if keyboard.is_pressed("q"):
        print("[x] Çıkış yapılıyor.")
        break

    screen_shot = sct.grab(monitor)
    frame = np.array(screen_shot)
    frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

    results = model(frame)[0]

    for box in results.boxes:
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        cls_id = int(box.cls[0])
        confidence = float(box.conf[0])
        label = model.names[cls_id]

        cx = int((x1 + x2) / 2)
        cy = int((y1 + y2) / 2)

        # headshot sınıfı varsa ve caps lock açık ise
        if label.lower().startswith(HEADSHOT_CLASS_KEYWORD) and is_capslock_on():
            abs_x = left + cx
            abs_y = top + cy
            data = f"{abs_x},{abs_y}\n"
            try:
                arduino.write(data.encode())
                print(f"[→] Gönderildi: {data.strip()}")
            except Exception as e:
                print(f"[!] HATA (seri port): {e}")

        # Ekrana çizim
        label_text = f"{label} {confidence:.2f}"
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(frame, label_text, (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        cv2.circle(frame, (cx, cy), 5, (0, 0, 255), -1)

    cv2.imshow("Headshot Detection", frame)

    if cv2.waitKey(1) == 27:  # ESC
        break

cv2.destroyAllWindows()
arduino.close()
print("[✓] Program sonlandı.")
