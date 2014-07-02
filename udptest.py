#!/usr/bin/env python2.7

import socket
import argparse
import sys
import time

parser = argparse.ArgumentParser(description="Send test patterns over a UDP socket (presumably to an arduino).")
parser.add_argument("-H", "--host", type=str, default="10.10.32.1", help="host")
parser.add_argument('-p', '--port', type=int, default=9999, help="port")
parser.add_argument('-n', '--num', type=int, default=48, help="number of lights")
parser.add_argument('-f', '--fps', type=float, default=0.5, help="Frames/sec to send data at")
gargs = None

def main(host, port, num, fps):
	print "Sending some shit to %s:%d" % (host, port)
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	m = "\xFF\x00\xFF\xFF\x00\x00\x00\xFF\x00" * (num/3 + 3) # GRB
	try:
		i = 0
		while(True):
			i += 1
			sock.sendto(m[i % 9:(3*num) + i % 9], (host, port))
			time.sleep(1 / fps)
			sys.stdout.write('.')
	except KeyboardInterrupt:
		print "Done"


if __name__ == "__main__":
	global gargs
	gargs = parser.parse_args()
	main(**vars(gargs));
