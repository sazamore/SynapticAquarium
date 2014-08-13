#!/usr/bin/env python2.7
"""
This file creates a large synaq model, runs it as fast as it can, and tells you how fast that is.
"""
from Neuron import Model 
import argparse
import random
import time
import io
import traceback
import json
import socket
gargs = None # Global arguments

parser = argparse.ArgumentParser(description="Make the synaq go as fast as it can.")
parser.add_argument("-i", "--input", type=argparse.FileType('r'), default=None, help="Network JSON file.")
parser.add_argument("-l", "--limit", type=float, default=None, help="Limit FPS.")
parser.add_argument("-n", "--num", type=int, action="store", default=100, help="Number of neurons")
parser.add_argument("-c", "--connectivity", type=int, action="store", default=6, help="synapses per neuron")
parser.add_argument("-M", "--maxlen", type=int, default=20, action="store", help="Maximum synapse length")
parser.add_argument("-m", "--minlen", type=int, default=5, action="store", help="Minimum synapse length")
parser.add_argument("-t", "--time", type=float, default=5, action="store", metavar="S", help="How long to run the model")
parser.add_argument("--test", action="store_true", help="Display a test pattern.")
mg = parser.add_mutually_exclusive_group()
mg.add_argument("-o", "--output", type=argparse.FileType('w'), default=None, help="Stream model output to here")
mg.add_argument("-u", "--udphost", type=str, default="10.10.32.1:9999", 
                                   help="host:port to send UDP packets to")
mg.add_argument("--tcphost", type=str, default=None, help="host:port to send TCP packets to")

def random_network():
    m = Model(dT=0.0001)
    nkeys = [None for _ in range(gargs.num)]
    for i in range(gargs.num):
    	nkeys[i], _ = m.add()
    print("Added %d neurons.\n" % gargs.num)
    nconns = 0
    for prekey in nkeys:
    	for i in range(gargs.connectivity):
    		postkey = None
    		while not postkey or postkey is prekey:
    			postkey = random.choice(nkeys)
    		weight = random.random() * 2 - 1
    		length = random.randint(1, gargs.maxlen)
    		#print("Connecting %s->%s weight %f length %d" % (prekey, postkey, weight, length))
    		m.connect(prekey, postkey, weight=weight, length=length)
    		nconns += 1
    print("Added %d connections" % nconns)
    return m
sock = None
host = None
port = None

def output(model):
    data = model.buf.read()
    #print "Outputting %d bytes" % len(data)
    #print repr(data)
    if gargs.output: # write to a file
        print(gargs.output.tell(), len(d), repr(d))
        gargs.output.write(d)
    elif gargs.udphost: # send over sock to host, port via UDP
        sock.sendto(data, (host, port))
    else: # Don't bother reading
        model.buf.seek(0, io.SEEK_END)

def main():
    global gargs, sock, host, port
    gargs = parser.parse_args()
    if gargs.input:
    	m = Model(**json.load(gargs.input))
    	print "Loaded network"
    else:
    	m = random_network()
    if gargs.udphost:
    	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    	host, port = gargs.udphost.split(":")
    	port = int(port)
    elif gargs.tcphost:
    	raise NotImplementedException("Can't do TCP yet")
    	# TODO: set sock
    	host, port = (None, None)
    else:
    	sock = None
    	host, port = (None, None)
    stime = time.time() # start time
    nsteps = 0;
    nbytes = 0;
    if gargs.test:
        print "TESTING"
        while True:
            for k in m.keyorder:
                print "Testing %s" % k
                m.test(k)
                output(m)
                time.sleep(1.5)
    else:
        print "RUNNING"
        try:
            while time.time() - stime < gargs.time:
                if gargs.limit is not None:
                    time.sleep(1./gargs.limit)
                m.step()
                for _ in xrange(10):
                    m.step(bufferize=False)
                output(m)
                nbytes += m.buf.tell()
                nsteps += 1
        except (Exception, KeyboardInterrupt) as e: 
            print "FAILURE! %r" % e
            traceback.print_exc()

    ttime = time.time() - stime
    bps = nbytes / ttime
    if bps > 1024:
    	bpsstr = "%fKiB" % (bps / 1024)
    elif bps > (1024 ** 2):
    	bpsstr = "%fMiB" % (bps / (1024 **2))
    elif bps > (1024 ** 3):
    	bpsstr = "%fGiB" % (bps / (1024 **3))
    else:
    	bpsstr = "%fb" % bps
    print("Network of %d LEDs.\n"
    	  "Simulated %d steps, creating %d bytes in %f seconds.\n"
    	  "%s/sec, %f frames/sec" % 
    	  (m.buf.tell() / 3, nsteps, nbytes, ttime, bpsstr, nsteps / ttime))
if __name__ == "__main__":
    main()
