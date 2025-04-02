#include <Mouse.h>

void setup() {
  Serial.begin(9600);
  Mouse.begin();
}

void loop() {
  if (Serial.available()) {
    String data = Serial.readStringUntil('\n');
    int comma = data.indexOf(',');

    if (comma > 0) {
      int x = data.substring(0, comma).toInt();
      int y = data.substring(comma + 1).toInt();

      // Ekran ortasını referans alarak delta hesapla (1920x1080 için)
      int dx = x - 960;
      int dy = y - 540;

      // Mouse'u kaydır
      Mouse.move(dx, dy);

      // Debug
      // Serial.print("Mouse moved: ");
      // Serial.print(dx); Serial.print(", "); Serial.println(dy);
    }
  }
}
