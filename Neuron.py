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
#Original code from Byron Galbraith via neurdon


import math
import random
import sys
import uuid
import struct
import io
from collections import deque

class Model(object):
    def __init__(self, 
    			 dT,  			# integration step delta
    			 neurons=None,  # Map of key: Neuron kwargs
    			 synapses=None, # map of key: (Synapse kwargs, pre neuron key, post neuron key)
    			 keyorder=None):# Order that neuron or synapse values are serialized (need not be comprehensive)
        self.buf = io.BytesIO( # CHANGE TO SUM OF LEDs
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
            self._keyorder = keyorder
        else:
            self._keyorder = []
    def params(self):
    	return {
    		"dT": self._dT,
    		"synapses": {k: (s.params(), prekey, postkey) for k, (s, prekey, postkey) in self._synapses.items()},
    		"neurons": {k: n.params() for k, n in self._neurons.items()},
    		"keyorder": self._keyorder[:],
    	}
    def add(self, **kwargs):
        n = Neuron(**kwargs)
        k = str(uuid.uuid4())
        self._neurons[k] = n
        self._keyorder.append(k)
        return (k, n)
    def header(self):
        return self._keyorder;
    def connect(self, prekey, postkey, **kwargs):
    	k = str(uuid.uuid4())
        s = Synapse(self._neurons[prekey], self._neurons[postkey], **kwargs)
        self._synapses[k] = (s, prekey, postkey)
        self._keyorder.append(k)
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
            for k in self._keyorder:
                if k in self._neurons:
                    self._neurons[k].bufferize(self.buf)
                elif k in self._synapses:
                    self._synapses[k][0].bufferize(self.buf)
            self.buf.flush()
            self.buf.truncate()
            self.buf.seek(0)
        return v

class Synapse(object):
    def __init__(self, pre, post, weight, length, nlights=None):
        self._weight = weight
        self.pre = pre
        post.inputs.append(self)
        self._length = length
        self._nlights = nlights or length
        self._values = deque(maxlen=nlights) # from collections
        senf._frame = 0
        if length >= len(self.pre.history):
            raise AssertionError("Not long enough, prehistory is %d, this is %d" % (len(self.pre.history), length))

    def step(self):
        if self._frame % (self._length // self._nlights):
            self._values.popleft()
            self._values.append(sef.pre.V)
        self._frame++

    def output(self):
        "Effect on postsynaptic current"
        return self._values[0] * self._weight

    def params(self):
    	return {"weight": self._weight,
                "lights": self._nlights,
    			"length": self._length,}

    def bufferize(self, buf):
        buf.write("\x00\x00".join(self._values))

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
        length  = 1,      # LED
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
        self._length = length
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
            'length':   self._length,
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

    def bufferize(self, buf):
        buf.write(("\x00" + chr(int(max(0, min(self.V, 255)))) + "\x00") * self._length) #G
