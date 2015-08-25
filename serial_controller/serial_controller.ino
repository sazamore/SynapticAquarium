// Synaptic Aquarium hardware bridge
// Eat data over native USB UART and make lights blink
// Landon, 2015, Beerware license
//#define FASTLED_ALLOW_INTERRUPTS 0
#include <FastLED.h>
#define PIN 6

#define NUM_LEDS 1190
#define FB_SIZE (NUM_LEDS * sizeof(CRGB))

CRGB frame_buffer[NUM_LEDS];
char input_buffer[NUM_LEDS * 3];

void setup() {
    while (!Serial);
    Serial.begin(9600);
    SerialUSB.begin(9600);
    memset(frame_buffer, 0, FB_SIZE);
    SerialUSB.readBytes((char*)frame_buffer, FB_SIZE);
    FastLED.addLeds<WS2812B, PIN, RGB>(frame_buffer, NUM_LEDS);
}

void loop() {
    while (!SerialUSB.available());
    int bytes_read = SerialUSB.readBytes((char*)input_buffer, FB_SIZE);
    if (bytes_read != FB_SIZE) {
        Serial.println("Incomplete read:");
        Serial.println(bytes_read);
    }
    int32_t fnv = 0x811c9dc5;
    for (int i = 0; i < bytes_read; i++) {
        fnv = fnv ^ input_buffer[i];
        fnv *= 0x01000193;
    }
    memcpy(frame_buffer, input_buffer, NUM_LEDS * 3);
    
    FastLED.show();
    memset(frame_buffer, 0, FB_SIZE);
    memset(input_buffer, 0, FB_SIZE);
    SerialUSB.write((char*)&fnv, sizeof(fnv));
}
