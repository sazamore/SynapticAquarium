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
    def do_req(self, path, params):
        global models, gargs
        #print("got a request for %r, params %r" % (path, params))
        model = models[params['model_id']] if 'model_id' in params else None
        if model:
            del params['model_id']
        # routing
        if not path:
            self.send_response(200)
            self.send_header('Content-Type', "text/html")
            self.end_headers()
            self.wfile.write(open("./synaq.html", 'r').read())
        elif path[0] == 'add':
            self.send_response(200)
            self.send_header('Content-Type', "text/plain")
            self.end_headers()
            if 'steps' in params:
               del params['steps']
            if 'dT' in params:
               del params['dT']
            k, n = model.add(**params)
            self.wfile.write(k)
            print "Added %s" % k
        elif path[0] == 'step':
            self.send_response(200)
            self.send_header('Content-Type', "application/json")
            self.end_headers()
            #print "Attempting to iterate %r steps" % params['steps']
            stime = time.clock()
            V = [model.step() for step in range(params['steps'])]
            #print "Calculation in %fs" % (time.clock() - stime)
            json.dump(V, self.wfile)
        elif path[0] == 'connect':
            self.send_response(200)
            self.send_header('Content-Type', "text/plain")
            self.end_headers()
            model.connect(**params)
        elif path[0] == 'new':
            self.send_response(200)
            self.send_header('Content-Type', "text/plain")
            self.end_headers()
            # Create a new model and add it to models
            nu = str(uuid.uuid4())
            models[nu] = Model(params['dT'] if 'dT' in params else gargs.dT)
            self.wfile.write(nu)
            print "Created %s" % nu
        elif path[0] == 'graph':
            self.send_response(200)
            self.send_header('Content-Type', "application/json")
            self.end_headers()
            g = model.params()
            json.dump(g, self.wfile)
            print "Dumping", repr(g)
        else:
            self.send_response(404)
            self.send_header('Content-Type', "text/plain")
            self.end_headers()
            self.wfile.write("nope")
            print "GOT NONEXISTANT PAGE %r" % path
        
    def do_GET(self):
        "Translate a GET request into path and a parameter map"
        global models, gargs
        res = urlparse.urlparse(self.path)
        params = { # urlparse passes EVERYTHING back as a list, this extracts singletons.
            key : try_parse(val[0]) if len(val) == 1 else val
            for key, val in urlparse.parse_qs(res.query).iteritems()
        }
        # Empty strings are lame
        path = [pe for pe in res.path.strip().split("/") if pe is not ""]
        self.do_req(path, params)
    def do_POST(self):
        "Translate a POST request into path and a parameter map"
        path = [pe for pe in self.path.strip().split("/") if pe is not ""]
        reqf = self.rfile.read(int(self.headers['Content-Length']))
        params = { # urlparse passes EVERYTHING back as a list, this extracts singletons.
            key : try_parse(val[0]) if len(val) == 1 else val
            for key, val in urlparse.parse_qs(reqf).iteritems()
        }
        self.do_req(path, params)
        

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simulate a neuron")
    parser.add_argument("-p", '--port',     dest="port",                        type=int,   action="store",     default=3103,       help="Port to serve HTTP on")
    parser.add_argument("-s", '--steps',    dest="steps",   metavar="N",        type=int,   action="store",     default="1000",     help="Number of steps")
    parser.add_argument("-t",               dest="dT",      metavar="ms",       type=float, action="store",     default=.025,       help="Step interval")
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
    server = BaseHTTPServer.HTTPServer(('', gargs.port), SARequestHandler)
    print "Serving on port %d!" % gargs.port
    server.serve_forever()
