
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


if __name__ == '__main__':

    node = Node_profile("Node", module_List_3V3)



    node = LoRa_node(name = "LoRa node", module_list = module_List_3V3,  
                    MCU_module   = apollo_module_3V3, MCU_active_state = apollo_state_active_3V3,
                    radio_module = radio_module_3V3,  radio_state_TX=radio_state_TX_3V3, radio_state_RX= radio_state_RX_3V3, Ptx = 2)
        
    node.set_radio_parameters(SF=9 ,Coding=1,Header=True,DE = 1,BW = 125e3, Payload = 50) 
    node.set_TX_Power_config( P_TX= PTX_PABOOST_3V3, I_TX=I_PABoost_3V3)  
    node.set_TX_Power(Ptx = 17)
    node.task_rx.task_rate= 0
    node.task_tx.task_rate= 24*4
    task_TPHG_3V3.task_rate = 24*12
    task_TPH_3V3.task_rate = 24*12
    node.add_task(task_TPHG_3V3)
    #node.add_task(task_TPH_3V3)
    # %%
    node.recompute()
    node.print_Tasks()
    node.print_Modules()
    node.plot_Power()

