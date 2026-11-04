import math
import numpy as np
import sys

c = 3e8

def path_loss(d=0,f = 0, n=0):
    return 20*math.log10(4*math.pi*f/c) + 10*n*math.log10(d)

def path_loss_PLd0(d=0, PLd0=0, d0=0, n=0):
    return PLd0 + 10*n*math.log10(d/d0)

def path_loss_distance(PL=0,f = 0, n=0):
    return 10**((PL-(20*math.log10(4*math.pi*f/c)))/(10*n)) 

def path_loss_distance_PLd0(PL=0, PLd0=0,d0=0, n=0):
    return d0*10**((PL-PLd0)/(10*n))

def path_loss_exponent(PL=0, d = 0, f= 0):
    n= (PL-(20*math.log10(4*math.pi*f/c)))/(10*math.log10(d))
    return n

def ple_from_distance(d_FPL=0, d_PLE = 0, f= 0):
    PL = path_loss(d_FPL,f,2)
    n= (PL-(20*math.log10(4*math.pi*f/c)))/(10*math.log10(d_PLE))
    return n


if __name__ == '__main__':
    f = 0.87e9
    d0= 1 #160e3

    print(path_loss(d=d0,f = f, n=3.76))
    print(path_loss_PLd0(d=6350, PLd0=7.7, d0=1, n=3.76))
    print(path_loss_distance_PLd0(PL=150.684, PLd0=7.7,d0=1, n=3.76))
