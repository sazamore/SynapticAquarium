#include <Adafruit_NeoPixel.h>

#include <Ethernet.h>
#include <EthernetUdp.h>
#include <SPI.h>

//#define DEBUG // Uncomment for debug()
#ifdef DEBUG
#define debug(x) Serial.print(x)
#else
#define debug(x)
#endif

#define LED_PIN 22

#define NUM_LEDS 1000  // TODO: Get final number of LEDs
#define PACKETS_PER_FRAME 3  // TODO: Update once we have the final number of LEDs
                             /* Should be a small integer that evenly divides NUM_LEDs (when
                                rounded up) */
#define MAX_PACKET_SIZE (NUM_LEDS * 3 / PACKETS_PER_FRAME) + 1  // 1001 bytes

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
byte mac[] = { 0xDE, 0xAD, 0xBE, 0xEF, 0x00, 0x00};
IPAddress ip(10, 10, 32, 1);
unsigned int port = 9999;
EthernetUDP udp;

char packet_buffer[MAX_PACKET_SIZE];
char frame_buffer[NUM_LEDS * 3];

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
    memcpy(frame_buffer + i, color, 3);
  }
  update_leds();
}

void setup() {
  byte test_color[3];
  
  debug("Starting test\n");
  
  /* Initialize frame buffer and test LEDs */
  test_color = { 0xFF, 0x00, 0x00 };
  set_frame_solid_color(test_color);
  delay(1000);
  test_color = { 0x00, 0xFF, 0x00 };
  set_frame_solid_color(test_color);
  delay(1000);
  test_color = { 0x00, 0x00, 0xFF };
  set_frame_solid_color(test_color);
  delay(1000);

  debug("Test Complete\n");
  debug("Listening for packets\n");

  /* Start listening for packets */
  Ethernet.begin(mac, ip);
  udp.begin(port);
}

void loop() {
  int packet_size = 0;
  int packet_frame_section = 0;

  /* Update the frame buffer */
  packet_size = udp.parsePacket();
  if (packet_size > 0) {
    /* If there's a packet available at all, read it out of the receive buffer into the packet
       buffer */
    udp.read(packet_buffer, MAX_PACKET_SIZE);
    debug("Received a packet of size ");
    debug(packet_size);
    debug("\n");
    if (packet_size == MAX_PACKET_SIZE) {
      // If the packet is complete, its first byte is which section of the frame to update
      packet_frame_section = packet_buffer[0];
      // Make sure the frame section is valid so we don't segfault
      if (packet_frame_section < PACKETS_PER_FRAME) {
        debug("Updating frame_section ");
        debug(packet_frame_section);
        debug("\n");
        memcpy(frame_buffer + (MAX_PACKET_SIZE * packet_frame_section),
            packet_buffer + 1, packet_size);
      } else {
        // Drop invalid packet
        debug("Dropping invalid packet, packet_frame_section = ");
        debug(packet_frame_section);
        debug(", PACKETS_PER_FRAME = ");
        debug(PACKETS_PER_FRAME);
        debug("\n");
      }
    } else {
      // Drop incomplete packet
      debug("Dropping incomplete packet, packet_size = ");
      debug(packet_size);
      debug(", MAX_PACKET_SIZE = ");
      debug(MAX_PACKET_SIZE);
      debug("\n");
    }
  }
  
  update_leds();
}
