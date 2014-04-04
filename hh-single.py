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


from __future__ import division
from numpy import *
import numpy as np
#from pylab import *
from scipy import *
import sys

class Neuron(object):
    def alpha_n(self,v):
        return 0.01*(-v + 10)/(exp((-v + 10)/10) - 1) if v != 10 else 0.1
    def beta_n(self,v):
        return 0.125*exp(-v/80)
    def alpha_m(self,v):
        return 0.1*(-v + 25)/(exp((-v + 25)/10) - 1) if v != 25 else 1
    def beta_m(self,v):
        return 4*exp(-v/18)
    def alpha_h(self,v):
        return 0.07*exp(-v/20)
    def beta_h(self,v):
        return 1/(exp((-v + 30)/10) + 1)
    def __init__(
        self,
        ### channel activity ###
        ## setup parameters and state variables
        T     = 55,     # ms

        ## HH Parameters
        V_zero  = -10,    # mV
        Cm      = 1,      # uF/cm2
        gbar_Na = 120,    # mS/cm2
        gbar_K  = 36,     # mS/cm2
        gbar_l  = 0.3,    # mS/cm2
        E_Na    = 115,    # mV
        E_K     = -12,    # mV
        E_l     = 10.613):# mV
        self.T      = T

        ## HH Parameters
        self.V_zero  = V_zero
        self.Cm      = Cm
        self.gbar_Na = gbar_Na    
        self.gbar_K  = gbar_K
        self.gbar_l  = gbar_l
        self.E_Na    = E_Na
        self.E_K     = E_K
        self.E_l     = E_l

        #Vm      = zeros(len(time)) # mV
        #Vm[0]   = V_zero
        self.V       = V_zero
        self.m       = self.alpha_m(V_zero)/(self.alpha_m(V_zero) + self.beta_m(V_zero))
        self.n       = self.alpha_n(V_zero)/(self.alpha_n(V_zero) + self.beta_n(V_zero))
        self.h       = self.alpha_h(V_zero)/(self.alpha_h(V_zero) + self.beta_h(V_zero))
        #self.time    = arange(0,T+dt,dt)
        ## Stimulus
        self.I = 0

    def __str__(self):
        return "HH Neuron: m: \t%r\tn:%r\th:\t%r\tV:\t%r" % (
               self.m, self.n, self.h, self.V)
    def step(self, dT):
        g_Na = self.gbar_Na*(self.m**3)*self.h
        g_K  = self.gbar_K*(self.n**4)
        g_l  = self.gbar_l  

        self.m += dT*(self.alpha_m(self.V)*(1 - self.m) - self.beta_m(self.V)*self.m)
        self.h += dT*(self.alpha_h(self.V)*(1 - self.h) - self.beta_h(self.V)*self.h)
        self.n += dT*(self.alpha_n(self.V)*(1 - self.n) - self.beta_n(self.V)*self.n)
        self.V += (self.I - 
                    g_Na*(self.V - self.E_Na) - 
                    g_K*(self.V - self.E_K) - 
                    g_l*(self.V- self.E_l)) / self.Cm * dT
        return self.V
        

        #Vm[i] = Vm[i-1] + (I[i-1] - g_Na*(Vm[i-1] - E_Na) - g_K*(Vm[i-1] - E_K) - g_l*(Vm[i-1] - E_l)) / Cm * dt 
        

## Simulate Model
"""
for i in range(1,len(time)):
    g_Na = gbar_Na*(m**3)*h
    g_K  = gbar_K*(n**4)
    g_l  = gbar_l

    m += dt*(alpha_mv(Vm[i-1])*(1 - m) - beta_m(Vm[i-1])*m)
    h += dt*(alpha_h(Vm[i-1])*(1 - h) - beta_h(Vm[i-1])*h)
    n += dt*(alpha_nv(Vm[i-1])*(1 - n) - beta_n(Vm[i-1])*n)

  Vm[i] = Vm[i-1] + (I[i-1] - g_Na*(Vm[i-1] - E_Na) - g_K*(Vm[i-1] - E_K) - g_l*(Vm[i-1] - E_l)) / Cm * dt 

"""
## plot membrane potential trace
def main(steps=1000, dT=0.025):
    a = Neuron()
    V = [a.step(dT) for _ in xrange(steps)]
    print V
    
"""
    figure()
    plot(time, Vm, time, -30+I)
    title('Hodgkin-Huxley Example')
    ylabel('Membrane Potential (mV)')
    xlabel('Time (msec)')
    show()
"""
if __name__ == "__main__":
    main(*sys.argv[1:])
