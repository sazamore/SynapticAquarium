#!/usr/bin/env python
"""
This file creates a large synaq model, runs it as fast as it can, and tells you how fast that is.
"""
from Neuron import Model 
import argparse
import random
import time
import io
import traceback
gargs = None # Global arguments

parser = argparse.ArgumentParser(description="Make the synaq go as fast as it can.")
parser.add_argument("-n", "--num", type=int, action="store", default=100, help="Number of neurons")
parser.add_argument("-c", "--connectivity", type=int, action="store", default=6, help="synapses per neuron")
parser.add_argument("-M", "--maxlen", type=int, default=20, action="store", help="Maximum synapse length")
parser.add_argument("-m", "--minlen", type=int, default=5, action="store", help="Minimum synapse length")
parser.add_argument("-t", "--time", type=float, default=5, action="store", metavar="S", help="How long to run the model")
parser.add_argument("-o", "--output", type=argparse.FileType('w'), default=None, help="Stream model output to here")

def main():
	global gargs
	gargs = parser.parse_args()
	m = Model(dT=0.0001, histlen=gargs.maxlen)
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
	stime = time.clock() # start time
	nsteps = 0;
	nbytes = 0;
	try:
		while time.clock() - stime < gargs.time:
			m.step()
			if gargs.output:
				gargs.output.write(m.buf.read())
			else:
				m.buf.seek(0, io.SEEK_END)
			nbytes += m.buf.tell()
			nsteps += 1
	except Exception as e: 
		print "FAILURE! %r" % e
		traceback.print_exc()

	ttime = time.clock() - stime
	bps = nbytes / ttime
	if bps > 1024:
		bpsstr = "%fKiB" % (bps / 1024)
	elif bps > (1024 ** 2):
		bpsstr = "%fMiB" % (bps / (1024 **2))
	elif bps > (1024 ** 3):
		bpsstr = "%fGiB" % (bps / (1024 **3))
	else:
		bpsstr = "%fb" % bps
	print("Created network of %d neurons with connectivity %d -- %d LEDs.\n"
		  "Simulated %d steps, creating %d bytes in %f seconds.\n"
		  "%s/sec, %f frames/sec" % 
		  (gargs.num, gargs.connectivity, m.buf.tell() / 3, nsteps, nbytes, ttime, bpsstr, nsteps / ttime))
if __name__ == "__main__":
	main()