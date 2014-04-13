#!/usr/bin/env python2.7

from Neuron import Neuron
import sys
import argparse
import csv
import BaseHTTPServer
import urlparse

def main(steps=1000, dT=.025, output=sys.stdout, **kwargs):
    """Serve doesn't do anything here, but filters the arg out for Neuron()"""
    print("Iterating %d steps, %fms/step" % (steps, dT))
    a = Neuron(**kwargs)
    V = [a.step(dT) for _ in xrange(steps)]
    writer = csv.writer(output)
    writer.writerow(["T", "V"])
    writer.writerows(zip((i * dT for i in xrange(len(V))), V))

def try_parse(thing):
    "Attempt to parse a string into an int or float. If we can't just return it"
    try:
        return int(thing)
    except ValueError:
        pass
    try:
        return float(thing)
    except ValueError:
        pass
    return thing

class SARequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    """
    Calls main() with output=(request wfile), and **kwargs=GET/POST parameters.
    You should probably not deploy this on the actual internet.
    """
    def do_GET(self):
        res = urlparse.urlparse(self.path)
        params = { # urlparse passes EVERYTHING back as a list, this extracts singletons.
            key : try_parse(val[0]) if len(val) == 1 else val
            for key, val in urlparse.parse_qs(res.query).iteritems()
        }
        print "got a GET request for %r, params %r" % (res, params)
        path = res.path.split("/")
        
        writer = csv.writer(self.wfile)
        self.send_response(200)
        self.send_header('Content-Type', "text/plain")
        self.end_headers()
        main(output=self.wfile, **params)
        print "Finished request for %s" % self.path
        
    def do_POST(self):
        print "got a POST request"
        print self.rfile.read()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simulate a neuron")
    parser.add_argument("-s", '--steps',    dest="steps",   metavar="N",        type=int,   action="store",     default="1000",     help="Number of steps")
    parser.add_argument("-t",               dest="dT",      metavar="ms",       type=float, action="store",     default=.025,       help="Step interval")
    parser.add_argument("-o",               dest="output",                      type=argparse.FileType(mode='w'),
                                                                                            action="store",     default=sys.stdout, help="Output CSV file")
    parser.add_argument("-S",               dest="serve",                                   action="store_true",                    help="Serve over HTTP")
    # Parameter args
    parser.add_argument(      '--V_zero',                   metavar="mV",       type=float, action="store",                         help="Initial V" )
    parser.add_argument(      '--Cm',                       metavar="uF/cm2",   type=float, action="store",                         help="Membrane Capacitance")
    parser.add_argument(      '--gbar_Na',                  metavar="mS/cm2",   type=float, action="store")
    parser.add_argument(      '--gbar_K',                   metavar="mS/cm2",   type=float, action="store")
    parser.add_argument(      '--gbar_l',                   metavar="mS/cm2",   type=float, action="store")
    parser.add_argument(      '--E_Na',                     metavar="mV",       type=float, action="store")
    parser.add_argument(      '--E_K',                      metavar="mV",       type=float, action="store")
    parser.add_argument(      '--E_l',                      metavar="mV",       type=float, action="store")
    args = parser.parse_args()
    if args.serve:
        server = BaseHTTPServer.HTTPServer(('', 3103), SARequestHandler)
        print "Giving up control flow!"
        server.serve_forever()
    else:
        kwargs = {k:v for k, v in vars(args).items() if v is not None and k is not 'serve'}
        main(**kwargs)
