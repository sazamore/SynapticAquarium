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


import numpy as np
import scipy as sp
import random
import sys
import uuid

class Model(object):
    def __init__(self, dT):
        self._dT = dT
        self._neurons = {}
        self._synapses = []
        self._key_order = []
        self._t = 0.
    def add(self, **kwargs):
        n = Neuron(**kwargs)
        k = str(uuid.uuid4())
        self._neurons[k] = n
        self._key_order.append(k)
        return (k, n)
    def header(self):
        return self._key_order;
    def connect(self, prekey, postkey, weight):
        s = Synapse(self._neurons[prekey], self._neurons[postkey], weight=weight)
        self._synapses.append((s, prekey, postkey))
        return s
    def step(self):
        v = [self._t]
        self._t += self._dT
        for k in self._key_order:
            v.append(self._neurons[k].step(self._dT))
        return v
    def graph(self): # Serialize the model
        neurons = {k: n.params() for (k, n) in self._neurons.items()}
        edges = [(prekey, postkey, s.weight) for s, prekey, postkey in self._synapses]
        return (neurons, edges)
        
class Synapse(object):
    def __init__(self, pre, post, weight=None):
        self.weight = random.random() if weight is None else weight
        self.pre = pre
        post.inputs.append(self)
    def output(self):
        "Effect on postsynaptic current"
        return self.pre.history[-1].V * self.weight

class Neuron(object):
    def alpha_n(self,v):
        return 0.01*(-v + 10)/(sp.exp((-v + 10)/10) - 1) if v != 10 else 0.1
    def beta_n(self,v):
        return 0.125*sp.exp(-v/80)
    def alpha_m(self,v):
        return 0.1*(-v + 25)/(sp.exp((-v + 25)/10) - 1) if v != 25 else 1
    def beta_m(self,v):
        return 4*sp.exp(-v/18)
    def alpha_h(self,v):
        return 0.07*sp.exp(-v/20)
    def beta_h(self,v):
        return 1/(sp.exp((-v + 30)/10) + 1)

    class _histent(object):
        def __init__(self, V, m, n, h, I):
            self.V = V
            self.m = m
            self.n = n
            self.h = h
            self.I = I

    def __init__(
        self,
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
        self.histlen = 10
        self.history = [self._histent(self.V, self.m, self.n, self.h, self.I) for _ in range(self.histlen)]

    def __str__(self):
        return "HH Neuron: m: \t%r\tn:%r\th:\t%r\tV:\t%r" % (
               self.m, self.n, self.h, self.V)
    def params(self): # return a dict such that you can pass it as kwargs to the constructor
        return  {
            'V_zero':   self.V_zero,
            'Cm':       self.Cm,
            'gbar_Na':  self.gbar_Na,
            'gbar_K':   self.gbar_K,
            'gbar_l':   self.gbar_l,
            'E_Na':     self.E_Na,
            'E_K':      self.E_K,
            'E_l':      self.E_l,
            'I':        self.I
        }
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
                    g_l*(self.V- self.E_l)) / self.Cm * dT
        self.history.append(self._histent(self.V, self.m, self.n, self.h, self.I))
        del self.history[0]
        return self.V
