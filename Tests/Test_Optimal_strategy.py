#%%
import math
import numpy as np
import inspect

import scipy.interpolate

from matplotlib import pyplot as plt
import matplotlib.pyplot as plt
plt.rcParams['figure.facecolor'] = 'white'
plt.rcParams['mathtext.fontset'] = 'stix'
plt.rcParams['font.family'] = 'STIXGeneral'
plt.rcParams['font.size'] = 16

import plotly.graph_objects as go
import plotly.express as px
import plotly.io as pio
from plotly.offline import plot
pio.renderers.default = "svg"

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from IoT_node_models.Energy_model import *
from IoT_node_models.Hardware_Modules import *
from IoT_node_models.Node_examples import *

path_to_save_svg = "SavedFiles"

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