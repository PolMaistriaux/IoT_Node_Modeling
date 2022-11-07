#%%

from matplotlib import pyplot as plt
import matplotlib.pyplot as plt
plt.rcParams['figure.facecolor'] = 'white'
import math
import numpy as np
import Energy_node as eNode
import sys
import os
import LoRa_library as LoRa
import logNormal_PL as logPL
import inspect
import scipy.interpolate
import plotly.graph_objects as go
import plotly.express as px
import plotly.io as pio
pio.renderers.default = "svg"
from plotly.offline import plot

I_PABoost_3V3 =np.array([34.397,  35.830,  37.055,  38.271,  39.891, 41.939,  43.8,    46.098,  49.611,  53.285, 57.641,  63.79,   69.597,  75.265,  82.35, 89.071,  93.224, 100.775, 107.872])
k =1.38 * 10**(-23)
T=290
B=125e3
kTB = 10*np.log10(k*T*B) +30 # expressed in dBm

NF = 6
G_TX = 2
G_RX = 2
H = G_TX + G_RX - kTB - NF -10

PTX    = np.arange(2,21,1) # expressed in dBm
PTX_EU = np.arange(2,15,1) # expressed in dBm
SF     = np.array([7   ,8  ,9    ,10 ,11   ,12 ]) 
SNRreq = np.array([-7.5,-10,-12.5,-15,-17.5,-20])

def find_Opti_Strategy(d_max,d_step,PL,SF=SF,PTX=PTX,H=H,I_PTX=[],verbose=False,NF=NF,G_TX=G_TX,G_RX=G_RX,B=B):
    kTB = 10*np.log10(k*T*B) +30
    H = G_TX + G_RX - kTB - NF -10

    d= np.arange(10,d_max,d_step)
    result = np.zeros((3,len(d)))

    for index,dist in enumerate(d):
        PL = PL_model(dist)
        res = find_Opti_SF_PTX(SF_possible=SF,PTX_possible=PTX,PL=PL,I_PTX=I_PTX)
        result[0,index] = dist
        result[1:,index]  = res[0:2]
    
    return result

def find_Opti_SF_PTX(PL,SF_possible=SF,PTX_possible=PTX,H=H,I_PTX=[],verbose=False,NF=NF,G_TX=G_TX,G_RX=G_RX,B=B):
    kT = 10*np.log10(k*T) +30
    kTB = kT + 10*np.log10(B)
    Sensi = kTB + NF + 10 #-2.5*SF
    LB = G_TX + G_RX - Sensi #-10 comes from the Spreading factor 

    E_best_solution = np.inf
    best_solution = [SF_possible[0],PTX_possible[0],E_best_solution]

    sol_found = 0

    for SF in SF_possible:
        for index,PTX_enum in enumerate(PTX_possible):
            if PL <= (LB+2.5*SF+PTX_enum):
                sol_found = sol_found+1
                if np.size(I_PTX)==0:
                    E_trial = (10**(0.5*PTX_enum/10)) * (2**SF)
                else:
                    E_trial = I_PTX[index] * (2**SF)
                if E_best_solution >  E_trial:
                    best_solution[0] = SF
                    best_solution[1] = PTX_enum
                    best_solution[2] = E_trial
                    E_best_solution = E_trial

    if sol_found ==0:
        if verbose:
            print("Careful, not solution found for SF and PTX, out of range")
        return [0,0,0]
    else:
        return best_solution


if __name__ == '__main__':

    def PL_model(d):
        return logPL.path_loss_PLd0(d=d, PLd0=94.40,d0=1, n=2.03)

    d= np.arange(10,25000,10)
    result = np.zeros((3,len(d)))

    for index,dist in enumerate(d):
        PL = PL_model(dist)
        result[:,index] = find_Opti_SF_PTX(SF_possible=SF,PTX_possible=PTX_EU,PL=PL,I_PTX=I_PABoost_3V3)

    ###########################################
    #           PLOT
    ###########################################
    fig,ax = plt.subplots(2,1)
    ax[0].set_xlabel("Distance [m]", fontsize = 14)
    ax[0].plot(d,
            result[0,:],
            color="red", 
            marker="o")
    ax[0].set_ylabel("SF", color="red", fontsize=14)

    ax2=ax[0].twinx()
    ax2.plot(d,
            result[1,:],
            color="blue",
            marker="o")
    ax2.set_ylabel("Ptx [dBm]",color="blue",fontsize=14)

    ax[1].plot(d,
            result[2,:]/min([i for i in result[2,:] if i>0]),
            color="red", 
            marker="o")
    ax[1].set_xlabel("Distance [m]", fontsize = 14)
    ax[1].set_ylabel("Normalized energy efficiency",fontsize=14)

    plt.show()

    print(np.unique(result[0:2,:],axis= 1))


