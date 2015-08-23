#!/usr/bin/env python2.7
"""
This file creates a large synaq model, runs it as fast as it can, and tells you how fast that is.
"""
from Neuron import Model, WhatTheFuck 
import argparse
import random
import time
import io
import traceback
import json
import socket
import serial
import serial.tools.list_ports
gargs = None # Global arguments

parser = argparse.ArgumentParser(description="Make the synaq go as fast as it can.")
parser.add_argument("-i", "--input", type=argparse.FileType('r'), default=None, help="Network JSON file.")
parser.add_argument("-l", "--limit", type=float, default=None, help="Limit FPS.")
parser.add_argument("-n", "--num", type=int, action="store", default=100, help="Number of neurons")
parser.add_argument("-c", "--connectivity", type=int, action="store", default=6, help="synapses per neuron")
parser.add_argument("-M", "--maxlen", type=int, default=20, action="store", help="Maximum synapse length")
parser.add_argument("-m", "--minlen", type=int, default=5, action="store", help="Minimum synapse length")
parser.add_argument("-t", "--time", type=float, default=None, action="store", metavar="S", help="How long to run the model")
parser.add_argument("-b", "--baud", type=int, default=9600, action="store", metavar="baud", help="Baud rate to open serial port")
parser.add_argument("--test", action="store_true", help="Display a test pattern.")
mg = parser.add_mutually_exclusive_group()
mg.add_argument("--output", type=argparse.FileType('w'), default=None, help="Stream model output to here")
mg.add_argument("--udphost", type=str, default=None, 
                                   help="host:port to send UDP packets to")
mg.add_argument("--serial", type=str, default=None, help="Stream model output to serial port, 'auto' to attempt autodiscovery")

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
            length = random.randint(gargs.minlen, gargs.maxlen)
            #print("Connecting %s->%s weight %f length %d" % (prekey, postkey, weight, length))
            m.connect(prekey, postkey, weight=weight, length=length)
            nconns += 1
    print("Added %d connections" % nconns)
    return m
sock = None
host = None
port = None
serport = None

def output(model):
    data = model.buf.read()
    #print "Outputting %d bytes" % len(data)
    #print repr(data)
    if gargs.output: # write to a file
        print(gargs.output.tell(), len(d), repr(d))
        gargs.output.write(d)
    elif gargs.udphost: # send over sock to host, port via UDP
        sock.sendto(data, (host, port))
    elif gargs.serial:
        serport.write(data)
        """
        resp = serport.read(9999)
        if resp:
            print repr(resp);
        """
    else: # Don't bother reading
        model.buf.seek(0, io.SEEK_END)

def bytestr(nbytes):
    if nbytes > 1024:
        return "%fKiB" % (nbytes / 1024)
    elif nbytes > (1024 ** 2):
        return "%fMiB" % (nbytes / (1024 **2))
    elif nbytes > (1024 ** 3):
        return "%fGiB" % (nbytes / (1024 **3))
    else:
        return "%fb" % nbytes

def main():
    global gargs, sock, host, port, serport
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
    if gargs.serial == 'auto':
        print "Attempting serial autodiscovery"
        for p in serial.tools.list_ports.grep('Arduino Due'):
            if 'Programming Port' in p[1]:
                continue
            print "Found serial port %s" % str(p)
            gargs.serial = p[0]
        if gargs.serial == 'auto':
            raise WhatTheFuck("Serial autodetection failed. Am I plugged into the furthest port from the power jack on the ardweenoh?")
    if gargs.serial:
        serport = serial.Serial(port=gargs.serial, baudrate=gargs.baud, timeout=0)
    stime = time.time() # start time
    nsteps = 0
    nbytes = 0
    if gargs.test:
        print "TESTING"
        while True:
            for k in m.keyorder:
                print "Testing %s" % k
                m.test(k)
                output(m)
                time.sleep(1.5)
    else:
        print "RUNNING\n"
        outputtime = None # moving average of time to output 
        simtime = None # moving average of time to simulate 
        obps = None # moving average of output bytes/sec
        try:
            while gargs.time is None or time.time() - stime < gargs.time:
                if gargs.limit is not None:
                    time.sleep(1. / gargs.limit)
                sbegin = time.clock()
                m.step()
                for _ in xrange(10):
                    m.step(bufferize=False)
                obegin = time.clock()
                output(m)
                oend = time.clock()

                sbytes = m.buf.tell()
                nbytes += sbytes
                
                nsteps += 1
                if outputtime is None:
                    outputtime = (oend - obegin)
                if simtime is None:
                    simtime = (obegin - sbegin)
                if obps is None:
                    obps = sbytes / outputtime
                outputtime = outputtime * 0.95 + (oend - obegin) * 0.05
                simtime = simtime * 0.95 + (obegin - sbegin) * 0.05
                obps = obps * 0.95 + (sbytes / (oend - obegin)) 
                if nsteps % 20 == 0:
                    print "\rSim: %f%%\tOutput: %f%%\t%s/sec" % ((simtime) / (simtime + outputtime), (outputtime) / (simtime + outputtime), bytestr(obps))
        except KeyboardInterrupt:
            print "Keyboard interrupt. Exiting";
        except Exception as e: 
            print "FAILURE! %r" % e
            traceback.print_exc()

    ttime = time.time() - stime
    bps = nbytes / ttime
    print("Network of %d LEDs.\n"
      "Simulated %d steps, creating %d bytes in %f seconds.\n"
      "%s/sec, %f frames/sec" % 
      (m.buf.tell() / 3, nsteps, nbytes, ttime, bytestr(bps), nsteps / ttime))
if __name__ == "__main__":
    main()
