
#include <Ethernet.h>
#include <EthernetUdp.h>

#include <Dns.h>

#include <Adafruit_NeoPixel.h>

#define DEBUG 
#ifdef DEBUG
#define debug(x) Serial.print(x)
#else
#define debug(x) 
#endif

//#define UDP_TX_PACKET_MAX_SIZE 1986 //Bigger than this and it appears the arduino just drops them.
#include <SPI.h>
#define LED_PIN 22

#define NUM_LEDS 1000 // Actually 992

#define PACKET_SIZE (NUM_LEDS / 250) + 4
char packetBuffer[PACKET_SIZE];    // Buffer for incoming UDP packets

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

//EthernetServer server = EthernetServer(9999);

/* UDP Setup */
EthernetUDP udp;




/* Frame Buffer Setup */
char frameBuffer[NUM_LEDS * 3];
int prev_offset = 0;

int packet = 0;

void setup() {
  for (int i = 0; i < NUM_LEDS; i++) {
    frameBuffer[i] = 0xFF;
    frameBuffer[i+1] = 0x00;
    frameBuffer[i+2] = 0xFF;
  }
  
  
  // Initialize LED Strip
  // Initialize Serial
  Serial.begin(9600);
  debug("Starting Test.\n");
  strip.begin();
  for (int i = 0; i < NUM_LEDS; i++) {
    strip.setPixelColor(i, 0x440000);
  }
  strip.show();
  delay(1000);
  for (int i = 0; i < NUM_LEDS; i++) {
    strip.setPixelColor(i, 0x004400);
  }
  strip.show();
  delay(1000);
  for (int i = 0; i < NUM_LEDS; i++) {
    strip.setPixelColor(i, 0x000044);
  }
  strip.show();
  delay(1000);
  
  // Initialize Ethernet and UDP
  Ethernet.begin(mac, ip);
  udp.begin(port);
  
  //server.begin();
  
  // Initialize Serial
  Serial.begin(9600);
  debug("listening.\n");
}

void loop() {
  int packet_size = udp.parsePacket();
  if (packet_size) {
    udp.read(packetBuffer, PACKET_SIZE); 
  }
  
  for (int i = 0; i < NUM_LEDS; i++) {
    strip.setPixelColor(i, strip.Color(packetBuffer[(i * 3)],
                                       packetBuffer[(i * 3) + 1],
                                       packetBuffer[(i * 3) + 2]));     
  }
  strip.show();
}  
  // Read a TCP packet if available
  /*EthernetClient client = server.available();
  if (client) {
    size_t bytes_read = client.read(packetBuffer, 10000);*/
  
    
       
    //debug("bytes_read = ");
    //debug(bytes_read);
    //debug("\n");
    /*debug("buffer = { ");
    for (int i = 0; i < bytes_read; i++) {
      debug(packetBuffer[i]);
      debug(", ");
    }
    debug("\n")*/;
    /*if (bytes_read > 0) {
      memcpy(frameBuffer, packetBuffer, bytes_read);
    }*/
 
  //client.stop();
  

  
  
  /*int b = 0;
  char byte_ = client.read();
  while (byte_ != -1) {
    packetBuffer[b] = byte_;
    byte_ = client.read();
    b++;
    // TODO: Deal with overflowing the buffer
  }*/
    

    
  /*   packet++;
     //udp.read(packetBuffer, UDP_TX_PACKET_MAX_SIZE);
    
     
    // Copy from packet into frame buffer
    // (i is in bytes)
    int offset = prev_offset;
    debug("Starting copy, prev_offset =");
    debug(prev_offset);
    debug("\n");
    int j = 0;
    for (int i = 0; i < packetSize - 1; i++) {
      frameBuffer[offset + i] = packetBuffer[i];
     
      // Flip offset in frameBuffer (within this trip through loop)
      if (offset + i == NUM_LEDS - 1) {
        debug("Flipping offset, i = ");
        debug(i);
        debug("\n");
        offset = 0;
      }
      
      // Setup offset for next trip through loop
      /*if (i == packetSize - 2) {
        debug("End of packet copy\n");
        prev_offset = offset + i;
      }*\/
    }
  }*/
  
  // Copy from framebuffer to lights
  // (i is in LEDs)
  
  
  /*
  // Read a UDP packet if available
  int packetSize = udp.parsePacket();
  int frames = 0;
  int lastPacket = 0;
  if (packetSize > 0)
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
     *\/  
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
       *\/
       strip.setPixelColor(i, strip.Color(packetBuffer[(i * 3)],
                                          packetBuffer[(i * 3) + 1],
                                          packetBuffer[(i * 3) + 2]));
    }
    strip.show();
  } else {
    if (frames % 1000) {
      debug(".");
    }
  }*/

  
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
