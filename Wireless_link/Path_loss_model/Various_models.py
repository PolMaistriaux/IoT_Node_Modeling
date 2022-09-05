import math
import numpy as np
import sys
import logNormal_PL as logPL
from scipy import optimize

def test_freq_range(f,fLow,fHigh,model):
    if (f<=fHigh and f>=fLow):
        return True
    else:
        print(model+" : Freq out of model range")
        return False
###################################################################
  
def twoRay(d=0 , h_tx = 3, h_rx=2):
    return 40*math.log10(d) - 20*math.log10(h_tx*h_rx)

def twoRay_distance(PL=0 , h_tx = 3, h_rx=2):
    return 10**((PL + 20*math.log10(h_tx*h_rx))/40)

###################################################################
    
def Callebaut_lowH(d=0,f=8.68e8):
    if test_freq_range(f,7e8,10e8,"Callebaut"):
        return logPL.path_loss_PLd0(d=d, PLd0=94.40,d0=1, n=2.03)
    return 0


def Callebaut_lowH_distance(PL=0,f=8.68e8):
    if test_freq_range(f,7e8,10e8,"Callebaut"):
        return logPL.path_loss_distance_PLd0(PL=PL, PLd0=94.40,d0=1, n=2.03)
    return 0
###################################################################

def Silva_tropical(d=0, h_tx=0 ,f=0, isCloseTrunk=True):
    if test_freq_range(f,7e8,9e8,"Silva Tropical"):
        fMHz = f/1e6
        PL = 121.795- 0.0062*fMHz - 0.525*h_tx + (39.945 - 0.0124*fMHz+ 0.0071*h_tx)*math.log10(d/1e3)+isCloseTrunk*10.29
        return PL
    return 0

def Silva_tropical_distance(PL=0, h_tx=0 ,f=0, isCloseTrunk=True):
    if test_freq_range(f,7e8,9e8,"Silva Tropical"):
        fMHz = f/1e6
        d =1000* 10**((PL - 121.795 + 0.0062*fMHz + 0.525*h_tx - isCloseTrunk*10.29)/(39.945 - 0.0124*fMHz + 0.0071*h_tx))
        return d
    return 0

###################################################################

def Jiang_NDVI(d=0, NDVI=0 ,f=0):
    if test_freq_range(f,0,100e8,"Jiang"):
        PLE = -8.3959* NDVI**2 + 21.513*NDVI - 8.649
        return logPL.path_loss(d=d, f = f , n=PLE)
    return 0

def Jiang_NDVI_distance(PL=0, NDVI=0 ,f=0):
    if test_freq_range(f,0,100e8,"Jiang"):
        PLE = -8.3959* NDVI**2 + 21.513*NDVI - 8.649
        return logPL.path_loss_distance(PL=PL, f = f , n=PLE)
    return 0

###################################################################

def Ibdah_inLeaf(d=0 ,f=0, h_tx = 1.5, h_rx=1.25):
    if test_freq_range(f,0,100e8,"Ibdah in-leaf"):
        fMHz = f/1e6
        K = 0.77* (fMHz**(0.24)) * (d**0.41) +40*math.log10(d)-20*math.log10(h_tx*h_rx) - 10.8
        return K
    return 0

###################################################################

def COST235(d=0, f=0 ):
    if test_freq_range(f,0,100e8,"COST235"):
        fMHz = f/1e6
        return 15.6* (fMHz**(-0.009)) * (d**0.26)
    return 0

def Weissberger(d=0, f=0 ):
    test_freq_range(f,0,100e8,"Weissberger")
    if(d<14 and d>400):
        print("Weisseberger model is out of range : %d is not in 14<d<400"%d)
    fGHz = f/1e9
    return 1.33* (fGHz**(0.284)) * (d**0.588)

def ITUR(d=0, f=0 ):
    if test_freq_range(f,0,100e8,"ITUR"):
        fMHz = f/1e6
        return 0.2* (fMHz**(0.3)) * (d**0.6)
    return 0

def FITUR(d=0, f=0 ):
    if test_freq_range(f,0,100e8,"FITUR"):
        fMHz = f/1e6
        return 0.39* (fMHz**(0.39)) * (d**0.25)
    return 0

def LITUR(d=0, f=0 ):
    if test_freq_range(f,0,100e8,"LITUR"):
        fMHz = f/1e6
        return 0.48* (fMHz**(0.33)) * (d**0.13)
    return 0
