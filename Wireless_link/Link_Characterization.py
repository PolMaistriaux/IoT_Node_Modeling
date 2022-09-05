#%%%
from matplotlib import pyplot as plt
import math
import numpy as np
import sys
import sys
import os
file_path = os.path.abspath(__file__)
parent_dir_path        = os.path.dirname(file_path)
path_to_import_mainDir = os.path.dirname(parent_dir_path)
path_to_import_PL      = os.path.join(parent_dir_path,"Path_loss_model")
print(path_to_import_PL)
sys.path.append(path_to_import_PL)

plt.rcParams.update({'font.size': 9, 'figure.subplot.hspace':0.3})

import logNormal_PL as logPL
import Path_loss_library as plLib 
c = 3e8

###################################################################
def rx_Sensitivity(SNR_req,B,NF=3,T=290, dBm=False):
    k =1.38 * 10**(-23)
    rx_S =  SNR_req+ 10*np.log10(k*T*B) + NF + dBm*30
    return np.squeeze(rx_S)
        
###################################################################
def link_budget(SNR_req=0,B=0,NF=0,T=0, Tx=0, loss=0,Gtx=0,Grx=0, rx_S = "default", dBm=False):
    
    if rx_S == "default":
        rx_S     = rx_Sensitivity(SNR_req,B,NF,T, dBm)
    lB = Tx + Gtx + Grx + loss - rx_S    
    return lB
###################################################################

def plotModels(linkBudget, linkName, colorLb,name, value, colorModel,colorOk, d, f,figsize=(8,6)):
    colors = [colorModel for model in name]
    for i in [index for index,val in enumerate(value) if val <= linkBudget]:
        colors[i] = colorOk
    name.insert(0,"Link budget")
    colors.insert(0,colorLb)
    value = np.insert(value,0,linkBudget)
    
    
    fig, ax = plt.subplots(figsize=figsize)
    bar_plot = ax.bar(name,value,color=colors)
    labels = ax.get_xticklabels()
    
    valueTxt = np.round(value*100)/100
    for idx,rect in enumerate(bar_plot):
        height = rect.get_height()
        ax.text(rect.get_x() + rect.get_width()/2., 1.05*height,
                valueTxt[idx],
                ha='center', va='bottom', rotation=90)
    
    plt.setp(labels, rotation = 45, horizontalalignment = 'right',fontsize=12)
    
    plt.title(linkName+': PL at %d m and at %.3f GHz'%(d,f/1e9),fontsize=15)
    #plt.xlabel('Path loss model',fontsize=15)
    plt.ylabel('Path loss [dB]',fontsize=15)
    plt.show()

#%%
if __name__ == '__main__':
    print(rx_Sensitivity(SNR_req=-20,B=125e3,NF=6,T=290, dBm=True))
    #print(rx_Sensitivity(SNR_req=15,B=2e6,NF=6,T=290, dBm=True))
    #print(link_budget(SNR_req=-20,B=125e3,NF=3,T=290, Tx=13, loss=0,dBm=True))
    
    f=868e6
    d=1500
    linkBud = link_budget(SNR_req=-20,B=125e3,NF=2,T=290, Tx=17, loss=0,dBm=True)
    print(linkBud)
    names, PLs= plLib.path_loss_All_Model(d=d,f=f)
    #plotModels(103,"Short range", 'blue',names, PLs,'red','green',d=100,f=0.868e9)
    plotModels(linkBud,"Short range", 'blue',names, PLs,'red','green',d=d,f=f,figsize=(8,6))
# %%
