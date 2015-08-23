#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 28 16:19:21 2014

ACHTUNG!
ALLES TURISTEN UND NONTEKNISCHEN LOOKENPEEPERS!
DAS KOMPUTERMASCHINE IST NICHT FUR DER GEFINGERPOKEN UND MITTENGRABEN! 
ODERWISE IST EASY TO SCHNAPPEN DER SPRINGENWERK, BLOWENFUSEN UND POPPENCORKEN MIT SPITZENSPARKEN.
IST NICHT FUR GEWERKEN BEI DUMMKOPFEN. 
DER RUBBERNECKEN SIGHTSEEREN KEEPEN DAS COTTONPICKEN HANDER IN DAS POCKETS MUSS.
ZO RELAXEN UND WATSCHEN DER BLINKENLICHTEN.

@author: Sharri, Landon
"""
# Derived from code from Byron Galbraith via neurdon


import math
import random
import sys
import uuid
import struct
import io
import collections
from itertools import izip, count, repeat
# Transfer functions - take a float and return a chr
def clamp(val):
    return int(max(min(val, 255), 0))

class WhatTheFuck(Exception):
    pass

class Model(object):
    def __init__(self, 
                 dT,            # integration step delta
                 neurons=None,  # Map of key: Neuron kwargs
                 synapses=None, # map of key: (Synapse kwargs, pre neuron key, post neuron key)
                 keyorder=None):# Order that neuron or synapse values are serialized (need not be comprehensive)
        self._dT = dT
        self._t = 0.
        if neurons:
            self._neurons = {k: Neuron(**args) for k, args in neurons.items()}
        else:
            self._neurons = {}
        if synapses:
            self._synapses = {k: (Synapse(self._neurons[prekey], self._neurons[postkey], **args), prekey, postkey) for k, (args, prekey, postkey) in synapses.items()}
        else:
            self._synapses = {}
        if keyorder:
            self.keyorder = keyorder
        else:
            self.keyorder = []
        for keys, idx in izip(self.keyorder, count()):
            if isinstance(keys, basestring):
                thing = self.find(keys)
                if type(thing) == Neuron:
                    print "Keyorder entry [%d]%r is a string for a neuron. Assuming you want it green." % (idx, keys)
                    self.keyorder[idx] = [None, keys, None]
                elif type(thing) == Synapse:
                    print "Keyorder entry [%d]%r is a string for a synapse. Assuming you want it blue." % (idx, keys)
                    self.keyorder[idx] = [None, None, keys]
                else:
                    raise WhatTheFuck("Thing is (%r)%r. Expected Neuron or Synapse" % (type(thing), thing))
            if len(self.keyorder[idx]) < 3:
                self.keyorder[idx] += ([None] * len(3 - self.keyorder[keys]))
            if len(self.keyorder[idx]) is not 3:
                raise WhatTheFuck("Keyorder entry [%d]%r is the wrong length." % (idx, self.keyorder[idx]))
            if not set(keyorder[idx]) - set([None]):
                raise WhatTheFuck("Keyorder entry [%d]%r is entirely None." % (idx, self.keyorder[idx]))
        self.buf = io.BytesIO()
    def find(self, key):
        if key in self._neurons:
            return self._neurons[key]
        elif key in self._synapses:
            return self._synapses[key][0]
        else:
            raise WhatTheFuck("What the fuck is %s?" % key)
    def params(self):
        return {
            "dT": self._dT,
            "synapses": {k: (s.params(), prekey, postkey) for k, (s, prekey, postkey) in self._synapses.items()},
            "neurons": {k: n.params() for k, n in self._neurons.items()},
            "keyorder": self.keyorder[:],
        }
    def add(self, **kwargs):
        n = Neuron(**kwargs)
        k = str(uuid.uuid4())
        self._neurons[k] = n
        self.keyorder.append(k)
        return (k, n)
    def header(self):
        return self.keyorder;
    def connect(self, prekey, postkey, **kwargs):
        k = str(uuid.uuid4())
        s = Synapse(self._neurons[prekey], self._neurons[postkey], **kwargs)
        self._synapses[k] = (s, prekey, postkey)
        self.keyorder.append(k)
        return s
    def step(self, bufferize=True):
        v = [self._t]
        self._t += self._dT
        self.buf.seek(0)
        for n in self._neurons.values():
            v.append(n.step(self._dT)) # XXX - delete this perhaps? 
        for syn, prekey, postkey in self._synapses.values():
            syn.step()
        if bufferize:
            for rgbkey, idx in izip(self.keyorder, count()):
                R, G, B = [self.find(k).lights() if k is not None else repeat(0) for k in rgbkey]
                #print "%s" % [(r, g, b) for r, g, b in izip(R, G, B)]
                self.buf.write("".join([chr(r) + chr(g) + chr(b) for r, g, b in izip(R, G, B)]))
            self.buf.seek(0)
        """
        if bufferize:
            for k in self.keyorder:
                self.find(k).bufferize(self.buf)
            self.buf.flush()
            self.buf.truncate()
            self.buf.seek(0)
        """
        return v
    def test(self, key):
        self.buf.seek(0)
        for k in self.keyorder:
            if k == key:
                print "Found %s" % k
                if k in self._neurons:
                    self._neurons[k].test(self.buf)
                elif k in self._synapses:
                    self._synapses[k][0].test(self.buf)
            else:
                print "Blanking %s" % k
                if k in self._neurons:
                    self._neurons[k].blank(self.buf)
                elif k in self._synapses:
                    self._synapses[k][0].blank(self.buf)
        self.buf.flush()
        self.buf.truncate()
        self.buf.seek(0)

class Synapse(object):
    def __init__(self, pre, post, weight, length, reverse=True, nlights=None):
        self._weight = weight
        self.pre = pre
        post.inputs.append(self)
        self._length = length
        self._reverse = reverse
        self.nlights = nlights or length
        self._values = collections.deque([0 for _ in range(self.nlights)]) 
        self._frame = 0

    def step(self):
        if not self._frame % (self._length // self.nlights):
            self._values.popleft()
            self._values.append(self.pre.V)
        self._frame += 1
    def output(self):
        "Effect on postsynaptic current"
        return self._values[0] * self._weight
    def params(self):
        return {"weight": self._weight,
                "reverse": self._reverse,
                "nlights": self.nlights,
                "length": self._length,}
    def lights(self):
        if self._reverse:
            return [clamp(v)for v in reversed(self._values)]
        else:
            return [clamp(v)for v in self._values]
    def bufferize(self, buf):
        if self._reverse:
            buf.write("".join(["\x00\x00" + chr(clamp(v)) for v in reversed(self._values)]))
        else:
            buf.write("".join(["\x00\x00" + chr(clamp(v)) for v in self._values]))
    def test(self, buf):
        if self._reverse:
            buf.write("".join(["\x00\x00\xFF" for v in reversed(self._values)]))
        else:
            buf.write("".join(["\x00\x00\xFF" for v in self._values]))
    def blank(self, buf):
        if self._reverse:
            buf.write("".join(["\x00\x00\x00" for v in reversed(self._values)]))
        else:
            buf.write("".join(["\x00\x00\x00" for v in self._values]))

class Neuron(object):
    def alpha_n(self,v):
        return 0.01*(-v + 10)/(math.exp((-v + 10)/10) - 1) if v != 10 else 0.1
    def beta_n(self,v):
        return 0.125*math.exp(-v/80)
    def alpha_m(self,v):
        return 0.1*(-v + 25)/(math.exp((-v + 25)/10) - 1) if v != 25 else 1
    def beta_m(self,v):
        return 4*math.exp(-v/18)
    def alpha_h(self,v):
        return 0.07*math.exp(-v/20)
    def beta_h(self,v):
        return 1/(math.exp((-v + 30)/10) + 1)

    def __init__(
        self,
        nlights  = 0,     # LED
        ### channel activity ###
        ## setup parameters and state variables
        ## HH Parameters
        V_zero  = -10,    # mV
        I       = 0,      # IDKLOL
        Cm      = 1,      # uF/cm2
        gbar_Na = 120,    # mS/cm2
        gbar_K  = 36,     # mS/cm2
        gbar_l  = 0.3,    # mS/cm2
        E_Na    = 115,    # mV
        E_K     = -12,    # mV
        E_l     = 10.613):# mV
        ## LED parameters
        self.nlights =nlights
        ## HH Parameters
        self.V_zero = V_zero
        self.Cm     = Cm
        self.gbar_Na= gbar_Na    
        self.gbar_K = gbar_K
        self.gbar_l = gbar_l
        self.E_Na   = E_Na
        self.E_K    = E_K
        self.E_l    = E_l
        self._I     = I
        self.I      = 0
        # Initial Conditions
        self.V      = V_zero
        self.m      = self.alpha_m(V_zero)/(self.alpha_m(V_zero) + self.beta_m(V_zero))
        self.n      = self.alpha_n(V_zero)/(self.alpha_n(V_zero) + self.beta_n(V_zero))
        self.h      = self.alpha_h(V_zero)/(self.alpha_h(V_zero) + self.beta_h(V_zero))
        # idx n = value at T - n * dT
        self.inputs  = []

    def step(self, dT):
        "Step the model by dT. Strange things may happen if you vary dT"
        self.I = sum([i.output() for i in self.inputs])

        self.m += dT*(self.alpha_m(self.V)*(1 - self.m) - self.beta_m(self.V)*self.m)
        self.h += dT*(self.alpha_h(self.V)*(1 - self.h) - self.beta_h(self.V)*self.h)
        self.n += dT*(self.alpha_n(self.V)*(1 - self.n) - self.beta_n(self.V)*self.n)
        g_Na = self.gbar_Na*(self.m**3)*self.h
        g_K  = self.gbar_K*(self.n**4)
        g_l  = self.gbar_l 
        self.V += (self._I + self.I - 
                    g_Na*(self.V - self.E_Na) - 
                    g_K*(self.V - self.E_K) - 
                    g_l*(self.V - self.E_l)) / self.Cm * dT
        return self.V

    def __str__(self):
        return "HH Neuron: m: \t%r\tn:%r\th:\t%r\tV:\t%r" % \
                (self.m, self.n, self.h, self.V)

    def params(self): # return a dict such that you can pass it as kwargs to the constructor and get an equivalent neuron to this one
        return  {
            'nlights':  self.nlights,
            'V_zero':   self.V_zero,
            'Cm':       self.Cm,
            'gbar_Na':  self.gbar_Na,
            'gbar_K':   self.gbar_K,
            'gbar_l':   self.gbar_l,
            'E_Na':     self.E_Na,
            'E_K':      self.E_K,
            'E_l':      self.E_l,
            'I':        self._I
        }

    def lights(self):
        return [clamp(self.V)] * self.nlights
    def bufferize(self, buf):
        buf.write(("\x00" + chr(clamp(self.V)) + "\x00") * self.nlights) #G
    def test(self, buf):
        buf.write(("\x00\xFF\x00") * self.nlights) #G
    def blank(self, buf):
        buf.write(("\x00\x00\x00") * self.nlights) #G
