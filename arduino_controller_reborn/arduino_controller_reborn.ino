#include <Adafruit_NeoPixel.h>
#define W5200
#include <Ethernet.h>
#include <EthernetUdp.h>
#include <SPI.h>

//#define DEBUG // Uncomment for debug()
#ifdef DEBUG
#define debug(x) Serial.print(x)
#else
#define debug(x)
#endif

//#define SUPER_DEBUG // Uncomment for debug()
#ifdef SUPER_DEBUG
#define super_debug(x) Serial.print(x)
#else
#define super_debug(x)
#endif

#define LED_PIN 22

/* packet size and the number of LEDs are set by the model */
#define NUM_LEDS 1233  // TODO: Get final number of LEDs
#define MAX_PACKET_SIZE 512

/*
 * Setup the one LED strip:
 *   Parameter 1 = number of pixels in strip
 *   Parameter 2 = Arduino pin number (most are valid)
 *   Parameter 3 = pixel type flags, add together as needed:
 *     NEO_KHZ800  800 KHz bitstream (most NeoPixel products w/WS2812 LEDs)
 *     NEO_KHZ400  400 KHz (classic 'v1' (not v2) FLORA pixels, WS2811 drivers)
 *     NEO_GRB     Pixels are wired for GRB bitstream (most NeoPixel products)
 *     NEO_RGB     Pixels are wired for RGB bitstream (v1 FLORA pixels, not v2)
 */
/* Other permutations of flags don't seem to work on the LEDs we have */
Adafruit_NeoPixel strip = Adafruit_NeoPixel(NUM_LEDS, LED_PIN, NEO_RGB + NEO_KHZ800);

/* Network setup */
byte mac[] = { 0xDE, 0xAD, 0xBE, 0xEF, 0xFE, 0xEF};
byte ip[] = {10, 10, 32, 1};
byte subnet[] = {255, 255, 255, 0};
byte gateway[] = {10, 10, 32, 0};
unsigned int port = 9999;
EthernetServer server(port);

char packet_buffer[MAX_PACKET_SIZE];
char frame_buffer[4096];

/* Output the frame_buffer to the LEDs and refresh the LEDs */
void update_leds() {
  for (int i = 0; i < NUM_LEDS; i++) {
    strip.setPixelColor(i, strip.Color(frame_buffer[(i * 3)],
                                       frame_buffer[(i * 3) + 1],
                                       frame_buffer[(i * 3) + 2]));
  }
  strip.show();
}

/* Set every LED to a single color */
void set_frame_solid_color(byte color[]) {
  for (int i = 0; i < NUM_LEDS; i++) {
    memcpy(frame_buffer + (i * 3), color, 3);
  }
  update_leds();
}

void setup() {
  byte test_color[3];
   
  Serial.begin(9600);

  debug("Starting test\n");

  /* Initialize frame buffer and test LEDs */
  strip.begin(); 
  test_color = { 0x44, 0x00, 0x00 };
  set_frame_solid_color(test_color);
  delay(1000);
  test_color = { 0x00, 0x44, 0x00 };
  set_frame_solid_color(test_color);
  delay(1000);
  test_color = { 0x00, 0x00, 0x44 };
  set_frame_solid_color(test_color);
  delay(3000);
  test_color = { 0x00, 0x00, 0x00 };
  set_frame_solid_color(test_color);

  debug("Test Complete\n");
  debug("Listening for packets\n");

  /* Start listening for packets */
  Ethernet.begin(mac, ip);
  server.begin();
}

void loop() {
  int packet_size = 0;
  int packet_frame_section = 0;

  // Create a client TCP connection
  EthernetClient client = server.available();
  if (client && client.connected() and client.available()) {
    packet_frame_section = client.read();
    //unsigned long pre_read_millis = millis();
    packet_size = client.read((uint8_t *)packet_buffer, MAX_PACKET_SIZE);
    //Serial. print("Read time = ");
    //Serial.print(millis() - pre_read_millis);
    packet_frame_section = packet_buffer[0];
    debug("Received a packet of size ");
    debug(packet_size);
    super_debug(".\n");
    super_debug("\tFirst eight bytes of packet = [");
    for (int i = 0; i < 8; i++) {
      super_debug(packet_buffer[i]);
      super_debug(", ");
    }
    debug("]\n");
    debug("Updating frame_section ");
    debug(packet_frame_section);
    debug(" at frame_buffer offset = ");
    debug(MAX_PACKET_SIZE * packet_frame_section);
    debug("\n");
    memcpy(frame_buffer + (MAX_PACKET_SIZE * packet_frame_section),
      packet_buffer, packet_size);
    super_debug("\tFirst eight bytes of updated part = [");
    for (int i = 0; i < 8; i++) {
      super_debug(frame_buffer[(MAX_PACKET_SIZE * packet_frame_section) + i]);
      super_debug(", ");
    }
    super_debug("]\n");
    update_leds();
  }
}
