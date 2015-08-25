// Color roller for hardware test purposes. 
// Generates some psychedelic colors and rolls them across the strand.
// Landon, 2015, Beerware license

#include <FastLED.h>
#define PIN            6

#define NUM_LEDS 1190
#define FB_SIZE (NUM_LEDS * sizeof(CRGB))

CRGB frame_buffer[NUM_LEDS * 2];
float cmeander (float x) {
  return (sin(2*x)*cos(x)-0.3)*100;
}

void setup() {
    while (!Serial);
    Serial.begin(9600);
    SerialUSB.begin(9600);
    memset(frame_buffer, 0, FB_SIZE);
    FastLED.addLeds<WS2812B, PIN, RGB>(frame_buffer, NUM_LEDS);
    for (int i = 0; i < NUM_LEDS; i++) {
      float t = 16 * PI * i / NUM_LEDS;
      frame_buffer[i].r = (char)cmeander(t);
      frame_buffer[i].g = (char)cmeander(t + (PI / 3));
      frame_buffer[i].b = (char)cmeander(t + (2 * PI / 3));
    }
}
float t = 0;
void loop() {
    CRGB zero = frame_buffer[0];
    for (int i = 0; i < NUM_LEDS-1; i++) {
      frame_buffer[i] = frame_buffer[i + 1];
    }
    frame_buffer[NUM_LEDS-1] = zero;
    FastLED.show(); 
}
