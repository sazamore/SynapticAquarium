#!/usr/bin/env python2.7

from Neuron import Neuron
import sys
import argparse
import csv
import BaseHTTPServer
import urlparse

class SARequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_GET(self):
        res = urlparse.urlparse(self.path)
        params = { # urlparse passes EVERYTHING back as a list, this extracts singletons.
            key : val[0] if len(val) == 1 else val
            for key, val in urlparse.parse_qs(res.query).iteritems()
        }
        print "got a GET request for %r, params %r" % (res, params)
        path = res.path.split("/")[1:];
        writer = csv.writer(self.wfile)
        self.send_response(200)
        self.send_header('Content-Type', "text/plain")
        self.end_headers()
        main(output=self.wfile, **params)
        print "Finished request for %s" % self.path
        
    def do_POST(self):
        print "got a POST request"
        print self.rfile.read()

def main(steps=1000, dT=.025, output=sys.stdout, **kwargs):
    print("Iterating %d steps, %fms/step" % (steps, dT))
    a = Neuron(**kwargs)
    V = [a.step(dT) for _ in xrange(steps)]
    writer = csv.writer(output)
    writer.writerows(zip(xrange(len(V)), V))
        
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simulate a neuron")
    parser.add_argument("-s", '--steps',    dest="steps",   metavar="N",    type=int,   action="store",     default="1000",     help="Number of steps")
    parser.add_argument("-t",               dest="dT",      metavar="ms",   type=float, action="store",     default=.025,       help="Step interval")
    parser.add_argument("-o",               dest="output",                  type=argparse.FileType(mode='w'),
                                                                                        action="store",     default=sys.stdout, help="Output CSV file")
    parser.add_argument("-S",               dest="serve",                               action="store_true",default=.025,       help="Step interval")
    args = parser.parse_args()
    if args.serve:
        server = BaseHTTPServer.HTTPServer(('', 3103), SARequestHandler)
        print "Giving up control flow!"
        server.serve_forever()
    else:
        main(**vars(args))
