
#include <Ethernet.h>
#include <EthernetUdp.h>::w

#include <EthernetServer.h>
#include <Ethernet.h>
#include <Dhcp.h>
#include <EthernetClient.h>
#include <EthernetUdp.h>
#include <Dns.h>

#include <Adafruit_NeoPixel.h>

//#define DEBUG 

#ifdef DEBUG
#define debug(x) Serial.print(x)
#else
#define debug(x) 
#endif

#define UDP_TX_PACKET_MAX_SIZE 1500 //increase UDP size
#include <SPI.h>

#define NUM_LEDS 148
#define LED_PIN 22

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

/* Network setup: MAC, IP, and port */
byte mac[] = {
  0xDE, 0xAD, 0xBE, 0xEF, 0xFE, 0xEF };
IPAddress ip(10, 10, 32, 1);
unsigned int port = 9999;

/* UDP Setup */
EthernetUDP udp;
char packetBuffer[UDP_TX_PACKET_MAX_SIZE];    // Buffer for incoming UDP packets

void setup() {
  // Initialize LED Strip
  // Initialize Serial
  Serial.begin(9600);
  debug("Starting Test.\n");
  strip.begin();
  for (int i = 0; i < NUM_LEDS; i++) {
    strip.setPixelColor(i, 0xFF0000);
  }
  strip.show();
  delay(1000);
  for (int i = 0; i < NUM_LEDS; i++) {
    strip.setPixelColor(i, 0x00FF00);
  }
  strip.show();
  delay(1000);
  for (int i = 0; i < NUM_LEDS; i++) {
    strip.setPixelColor(i, 0x0000FF);
  }
  strip.show();
  delay(1000);
  
  // Initialize Ethernet and UDP
  Ethernet.begin(mac, ip);
  udp.begin(port);
  
  // Initialize Serial
  Serial.begin(9600);
  debug("listening.\n");
}

void loop() {
  // Read a UDP packet if available
  int packetSize = udp.parsePacket();
  int frames = 0;
  int lastPacket = 0;
  if (packetSize > 0) {
     udp.read(packetBuffer, UDP_TX_PACKET_MAX_SIZE);
     lastPacket = frames;
     frames++;
     debug("Received a packet of size: ");
     debug(packetSize);
     /*
     debug("Printing packet contents");
     for (int i = 0; i < packetSize - 1; i++) {
        debug(packetBuffer[i], DEC);
        debug(", ");
     }
     debug(packetBuffer[packetSize - 1], DEC);
     */
     for (int i = 0; i < NUM_LEDS; i++) {
       /*
       debug("Setting Color for Pixel ");
       debug(i);
       debug(" to ");
       debug(packetBuffer[i * 3]);
       debug(",");
       debug(packetBuffer[i * 3 + 1]);
       debug(",");
       debug(packetBuffer[i * 3 + 2]);
       */
       strip.setPixelColor(i, strip.Color(packetBuffer[(i * 3)],
                                          packetBuffer[(i * 3) + 1],
                                          packetBuffer[(i * 3) + 2]));
    }
    strip.show();
  } else {
    if (frames % 1000) {
      debug(".");
    }
  }

  
  /*
  // Below here is the demo soma/axon separation code
  //
  // Part      LEDs
  // ---------------
  // Lead      0-9
  // Axon #1   10-15
  // Soma #1   16-21
  // Axon #2   22-28
  // Soma #2   29-34
  // Axon #3   35-39
  // Tail      40-47
  //
  for (int i = 16; i < 22; i++) {
    strip.setPixelColor(i, strip.Color(0, 255, 255));
  }
  for (int i = 29; i < 35; i++) {
    strip.setPixelColor(i, strip.Color(0, 255, 255));
  }
  strip.show();
  */
}
