from matplotlib import pyplot as plt
import math
import numpy as np
import scipy.special as sp
import sys
sys.path.insert(0, './Path_loss_model')

plt.rcParams.update({'font.size': 9, 'figure.subplot.hspace':0.3})

c = 3e8

###################################################################
def rx_Sensitivity(BER = 0, Rb= 0, SNR_req='default', modulation = 'default', B=0,NF=3,T=290, dBm=False):
    BER=BER/100
    if SNR_req=='default':
        SNR_req = ebN0(BER,modulation)+10*np.log10(Rb/B)
    k =1.38 * 10**(-23)
    rx_S =  SNR_req+ 10*np.log10(k*T*B) + NF + dBm*30
    return np.squeeze(rx_S)
 
###################################################################
def reqSNR(BER = 0, Rb= 0, modulation = 'default', B=0, dBm=False):
    BER=BER/100
    SNR_req = ebN0(BER,modulation)+10*np.log10(Rb/B)
    return SNR_req 

###################################################################
def link_budget(SNR_req=0,B=0,NF=0,T=0, Tx=0, loss=0,Gtx=0,Grx=0, rx_S = "default", dBm=False):
    
    if rx_S == "default":
        rx_S     = rx_Sensitivity(SNR_req,B,NF,T, dBm)
    lB = Tx + Gtx + Grx + loss - rx_S    
    return lB

###################################################################
def ebN0(ber=0, modulation = "default"):
    
    if modulation == "default":
        ebn0 = 10*np.log10((sp.erfcinv(ber*2))**2)
        return ebn0

###################################################################
def BER(ebN0=0, modulation = "default"):
    
    if modulation == "default":
        ber = 0.5 * sp.erfc(np.sqrt(10**(ebN0/10)))
        
    return ber
###################################################################

if __name__ == '__main__':
    NF = 8
    GTx = 3
    GRx = 0
    loss = -5
    print(rx_Sensitivity(SNR_req=-20,B=125e3,T=290,NF=NF, dBm=True))
    #print(rx_Sensitivity(BER=0.1,Rb=600,B=200,T=290,NF=NF, dBm=True))
    #print(rx_Sensitivity(BER=0.1,Rb=20*15e3,B=2*15*250e3,T=290,NF=NF, dBm=True))
    #print(rx_Sensitivity(BER=0.1,Rb=2000e3,B=2*15*250e3,T=290,NF=NF, dBm=True))