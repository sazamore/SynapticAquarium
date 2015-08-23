// Synaptic Aquarium hardware bridge
// Eat data over native USB UART and make lights blink
// Landon, 2015, Beerware license

#include <FastLED.h>
#define PIN            6

#define NUM_LEDS 1190
#define FB_SIZE (NUM_LEDS * sizeof(CRGB))

CRGB frame_buffer[NUM_LEDS];

void setup() {
    while (!Serial);
    Serial.begin(9600);
    SerialUSB.begin(9600);
    memset(frame_buffer, 0, FB_SIZE);
    SerialUSB.readBytes((char*)frame_buffer, FB_SIZE);
    FastLED.addLeds<WS2812B, PIN, RGB>(frame_buffer, NUM_LEDS);
}

void loop() {
    memset(frame_buffer, 0, FB_SIZE);
    while (!SerialUSB.available());
    int bytes_read = SerialUSB.readBytes((char*)frame_buffer, FB_SIZE);
    while (bytes_read < FB_SIZE) {
        bytes_read += SerialUSB.readBytes(((char*)frame_buffer) + bytes_read, (FB_SIZE - bytes_read));
    }
    FastLED.show(); 
}
