# -*- coding: utf-8 -*-
"""
Created on Fri Mar 28 16:19:21 2014

@author: Sharri
"""
#Original code from Byron Galbraith via neurdon


from __future__ import division
import numpy as np
import pylab as py
#import scipy as sp     #haven't used this yet but I added it in for something and now I can't remember

## Functions
# K channel
alpha_n = np.vectorize(lambda v: 0.01*(-v + 10)/(np.exp((-v + 10)/10) - 1) if v != 10 else 0.1)
beta_n  = lambda v: 0.125*np.exp(-v/80)
n_inf   = lambda v: alpha_n(v)/(alpha_n(v) + beta_n(v))

# Na channel (activating)
alpha_m = np.vectorize(lambda v: 0.1*(-v + 25)/(np.exp((-v + 25)/10) - 1) if v != 25 else 1)
beta_m  = lambda v: 4*np.exp(-v/18)
m_inf   = lambda v: alpha_m(v)/(alpha_m(v) + beta_m(v))

# Na channel (inactivating)
alpha_h = lambda v: 0.07*np.exp(-v/20)
beta_h  = lambda v: 1/(np.exp((-v + 30)/10) + 1)
h_inf   = lambda v: alpha_h(v)/(alpha_h(v) + beta_h(v))

## setup parameters and state variables
T     = 100  # ms
dt    = 0.025 # ms
time  = np.arange(0,T+dt,dt)

## HH Parameters
V_rest  = -10    # Resting potential (mV), previously value = 1
Cm      = 1      # Membrane capacity (uF/cm2) 
gbar_Na = 120    # mS/cm2
gbar_K  = 36     # mS/cm2
gbar_l  = 0.3    # mS/cm2
E_Na    = 115    # mV
E_K     = -12    # mV
E_l     = 10.613 # mV

Vm      = np.zeros(len(time)) # mV
Vm[0]   = V_rest
m       = m_inf(V_rest)      
h       = h_inf(V_rest)
n       = n_inf(V_rest)

## Stimulus
I = np.random.rand(len(time))*10
mu = 0          #centeroid
sigma = 0.5     #gaussian width
x = np.arange(0,len(time),1)
I = I*3+np.sin(.018*x/np.pi)*2+ np.sin(0.09*x/np.pi)*2  #noise plus multiple sine input
x = np.arange(0,15,1)
gaus = np.exp((-x**2)/(2*sigma**2))/100
I = np.convolve(I,x,mode='same')   #Convolve (smooth) input
I = I/100
I1 = I

## Simulate Model
for i in range(1,len(time)):
  g_Na = gbar_Na*(m**3)*h
  g_K  = gbar_K*(n**4)
  g_l  = gbar_l

  m += dt*(alpha_m(Vm[i-1])*(1 - m) - beta_m(Vm[i-1])*m)
  h += dt*(alpha_h(Vm[i-1])*(1 - h) - beta_h(Vm[i-1])*h)
  n += dt*(alpha_n(Vm[i-1])*(1 - n) - beta_n(Vm[i-1])*n)

  Vm[i] = Vm[i-1] +  np.random.normal(0,1,1)+(I[i-1] - g_Na*(Vm[i-1] - E_Na) - g_K*(Vm[i-1] - E_K) - g_l*(Vm[i-1] - E_l)) / Cm * dt 
  
I = -Vm*.1+np.random.rand(len(time))*5
Vm      = np.zeros(len(time)) # mV
Vm[0]   = V_rest
m       = m_inf(V_rest)      
h       = h_inf(V_rest)
n       = n_inf(V_rest)
I2 = I

for i in range(1,len(time)):
  g_Na = gbar_Na*(m**3)*h
  g_K  = gbar_K*(n**4)
  g_l  = gbar_l

  m += dt*(alpha_m(Vm[i-1])*(1 - m) - beta_m(Vm[i-1])*m)
  h += dt*(alpha_h(Vm[i-1])*(1 - h) - beta_h(Vm[i-1])*h)
  n += dt*(alpha_n(Vm[i-1])*(1 - n) - beta_n(Vm[i-1])*n)

  Vm[i] = Vm[i-1] + np.random.normal(0,1,1)+(I[i-1] - g_Na*(Vm[i-1] - E_Na) - g_K*(Vm[i-1] - E_K) - g_l*(Vm[i-1] - E_l)) / Cm * dt 

I = I - Vm*.2+np.random.rand(len(time))*5

Vm      = np.zeros(len(time)) # mV
Vm[0]   = V_rest
m       = m_inf(V_rest)      
h       = h_inf(V_rest)
n       = n_inf(V_rest)

for i in range(1,len(time)):
  g_Na = gbar_Na*(m**3)*h
  g_K  = gbar_K*(n**4)
  g_l  = gbar_l

  m += dt*(alpha_m(Vm[i-1])*(1 - m) - beta_m(Vm[i-1])*m)
  h += dt*(alpha_h(Vm[i-1])*(1 - h) - beta_h(Vm[i-1])*h)
  n += dt*(alpha_n(Vm[i-1])*(1 - n) - beta_n(Vm[i-1])*n)

  Vm[i] = Vm[i-1] + np.random.normal(0,1,1)+(I[i-1] - g_Na*(Vm[i-1] - E_Na) - g_K*(Vm[i-1] - E_K) - g_l*(Vm[i-1] - E_l)) / Cm * dt 


## plot membrane potential trace
py.figure()
py.plot(time, Vm, time, I, time, I1, time, I2) #when using step function subtract 30 from I
py.title('Second order cell response Example')
py.ylabel('Membrane Potential (mV)')
py.xlabel('Time (msec)')
py.legend('I', 'I1','I2')

py.show()