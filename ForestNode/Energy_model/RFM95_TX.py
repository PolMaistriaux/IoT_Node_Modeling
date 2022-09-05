# -*- coding: utf-8 -*-
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

"""
Created on Tue Jun  7 21:38:34 2022

@author: maistriauxp
"""
from turtle import position
import matplotlib.pyplot as plt
plt.rcParams['figure.facecolor'] = 'white'
import pandas as pd
import numpy as np

import sys
import os

file_path = os.path.abspath(__file__)
parent_dir_path  = os.path.dirname(os.path.dirname(file_path))
path_to_import   = os.path.join(parent_dir_path,"Characterization")
sys.path.append(path_to_import)
import RFM95 as rfm


#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
Power_dBm  = rfm.PTX_PABOOST_configured
Power_mW = 10**(Power_dBm/10)

Power_dBm_3V3  = rfm.PTX_PABOOST_3V3
Power_mW_3V3   = 10**(Power_dBm_3V3/10)

Power_dBm_1V8  = rfm.PTX_PABOOST_1V8
Power_mW_1V8   = 10**(Power_dBm_1V8/10)

Current_3V3 = rfm.I_PABoost_3V3
Current_1V8 = rfm.I_PABoost_1V8


fig, ax = plt.subplots(2,1,figsize =(6, 10))
fig.suptitle("Power consumption of RFM95W \n in TX mode using PA boost",fontsize = 17)

ax[0].set_xlabel('Transmission power[dBm]')
ax[0].set_ylabel('Current in TX [mA]')
ax[0].set_xlim([2-0.5,20+0.25])
ax[0].set_xticks(np.arange(2,20+2,2))
ax[0].grid()
ax[1].set_xlabel('Transmission power[mW]')
ax[1].set_ylabel('Power in TX [mW]')
ax[1].set_xlim([0,10**(20/10)+5])
#ax[1].set_xticks(np.arange(2,20+2,2))
ax[1].grid()

ax[0].plot(Power_dBm_3V3,Current_3V3     , color ='red' , label ="@3V3: effective PTX") 
ax[0].plot(Power_dBm    ,Current_3V3,'--', color ='red' , label ="@3V3: configured PTX")
ax[0].plot(Power_dBm_1V8,Current_1V8     , color ='blue', label ="@1V8: effective PTX")
ax[0].plot(Power_dBm    ,Current_1V8,'--', color ='blue', label ="@1V8: configured PTX")
ax[0].scatter(Power_dBm_3V3[Power_dBm<=17],Current_3V3[Power_dBm<=17] , color ='red' , marker = "^") 
ax[0].scatter(Power_dBm_3V3[Power_dBm> 17],Current_3V3[Power_dBm> 17] , color ='red' , marker = "o",s=50) 
ax[0].scatter(Power_dBm_1V8[Power_dBm<=17],Current_1V8[Power_dBm<=17] , color ='blue', marker = "^") 
ax[0].scatter(Power_dBm_1V8[Power_dBm> 17],Current_1V8[Power_dBm> 17] , color ='blue', marker = "o",s=50) 

ax[0].legend(fontsize =12, loc='lower right')

ax[1].plot(Power_mW_3V3,Current_3V3     , color ='red' , label ="@3V3: effective PTX")
ax[1].plot(Power_mW    ,Current_3V3,'--', color ='red' , label ="@3V3: configured PTX")
ax[1].plot(Power_mW_1V8,Current_1V8     , color ='blue', label ="@1V8: effective PTX")
ax[1].plot(Power_mW    ,Current_1V8,'--', color ='blue', label ="@1V8: configured PTX")
ax[1].scatter(Power_mW_3V3[Power_dBm<=17],Current_3V3[Power_dBm<=17] , color ='red' , marker = "^") 
ax[1].scatter(Power_mW_3V3[Power_dBm> 17],Current_3V3[Power_dBm> 17] , color ='red' , marker = "o",s=50) 
ax[1].scatter(Power_mW_1V8[Power_dBm<=17],Current_1V8[Power_dBm<=17] , color ='blue', marker = "^") 
ax[1].scatter(Power_mW_1V8[Power_dBm> 17],Current_1V8[Power_dBm> 17] , color ='blue', marker = "o",s=50) 
ax[1].legend(fontsize =12, loc='lower right')

plt.show()


# %%
