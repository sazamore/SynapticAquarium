
// NeoPixel Ring simple sketch (c) 2013 Shae Erisson
// released under the GPLv3 license to match the rest of the AdaFruit NeoPixel library

#include <Adafruit_NeoPixel.h>

#define PIN            6

#define NUM_LEDS 1190  // TODO: Get final number of LEDs
#define FB_SIZE (NUM_LEDS * 3)

Adafruit_NeoPixel strip = Adafruit_NeoPixel(NUM_LEDS, PIN, NEO_RGB + NEO_KHZ800);
char frame_buffer[FB_SIZE];

void setup() {
    while (!Serial);
    strip.begin(); 
    Serial.begin(9600);
    SerialUSB.begin(40000000);
    memset(frame_buffer, 0, FB_SIZE);
}

void loop() {
    memset(frame_buffer, 0, FB_SIZE);
    while (!SerialUSB.available());
    int bytes_read = SerialUSB.readBytes(frame_buffer, FB_SIZE);
    for(int i = 0; i < NUM_LEDS; i++) {
        strip.setPixelColor(i, strip.Color(frame_buffer[(i * 3)],
                                           frame_buffer[(i * 3) + 1],
                                           frame_buffer[(i * 3) + 2]));
    }
    strip.show(); 
}
