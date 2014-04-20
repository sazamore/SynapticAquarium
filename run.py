#!/usr/bin/env python2.7

from Neuron import Model, Neuron
import sys
import argparse
import csv
import BaseHTTPServer
import urlparse
import uuid
import json
import time

def main(steps=1000, dT=.025, output=sys.stdout, **kwargs):
    """Serve doesn't do anything here, but filters the arg out for Neuron()"""
    print("Iterating %d steps, %fms/step" % (steps, dT))
    a = Neuron(**kwargs)
    b = Neuron(I=15);
    V = [a.step(dT) for _ in xrange(steps)]
    writer = csv.writer(output)
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

models = {} # Map of keys to model instances
gargs = None # global arguments (from cmdline)

class SARequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    """
    Calls main() with output=(request wfile), and **kwargs=GET/POST parameters.
    You should probably not deploy this on the actual internet.
    """
    def do_GET(self):
        global models, gargs
        res = urlparse.urlparse(self.path)
        params = { # urlparse passes EVERYTHING back as a list, this extracts singletons.
            key : try_parse(val[0]) if len(val) == 1 else val
            for key, val in urlparse.parse_qs(res.query).iteritems()
        }
        print("got a GET request for %r, params %r" % (res, params))
        # Empty strings are lame
        path = [pe for pe in res.path.strip().split("/") if pe is not ""]
        self.send_response(200)
        self.send_header('Content-Type', "text/plain")
        self.end_headers()
        model = models[params['model_id']] if 'model_id' in params else None
        if model:
            del params['model_id']
        if path[0] == 'one':
            writer = csv.writer(self.wfile)
            main(output=self.wfile, **params)
        elif path[0] == 'new':
            k, n = model.add(**params)
            self.wfile.write(k)
            print "Added %s" % k
        elif path[0] == 'step':
            print "Attempting to iterate %r steps" % params['steps']
            stime = time.clock()
            V = [model.step() for step in range(params['steps'])]
            print "Calculation in %fs" % (time.clock() - stime)
            json.dump(V, self.wfile)
            print "Whole step in %fs" % (time.clock() - stime)
            print "Stepped"
        elif path[0] == 'reset':
            # Create a new model and add it to models
            nu = str(uuid.uuid4())
            models[nu] = Model(params['dT'] if 'dT' in params else gargs.dT)
            self.wfile.write(nu)
            print "Created %s" % nu
        print("Finished request for %r" % path)

    def do_POST(self):
        print("got a POST request")
        print(self.rfile.read())

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
    parser.add_argument(      '--I',                        metavar="mA?",      type=float, action="store")
    gargs = parser.parse_args()
    if gargs.serve:
        server = BaseHTTPServer.HTTPServer(('', 3103), SARequestHandler)
        print "Giving up control flow!"
        server.serve_forever()
    else:
        kwargs = {k:v for k, v in vars(gargs).items() if v is not None and k is not 'serve'}
        main(**kwargs)
