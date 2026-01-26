#%%
import math
import numpy as np
import inspect
import importlib

import scipy.interpolate

import matplotlib
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
parent_directory = os.path.dirname(os.getcwd())
sys.path.append(parent_directory)
#sys.path.append(os.path.dirname(parent_directory))
#sys.path.append(os.path.dirname(os.path.dirname(parent_directory)))

from IoT_node_models.Energy_model                        import *
from IoT_node_models.Energy_model.Wireless_communication import *
from IoT_node_models.Hardware_Modules                    import *
from IoT_node_models.Impact_model                        import *



def sweep_task_rate(Node, fmax, f_step, Task = None,nAA=[], doPlot = False,filename =None,figsize=(7,6)):   

    if Task == None :
        print("No task tx specified")
        return
    capa_1AA = Node.get_Node().get_Battery().get_capacity_mAh()
    f_initial = Node.get_task_rate(Task)
    fdata= np.arange(1,fmax,f_step)
    result = np.zeros((4,len(nAA),len(fdata)))

    for indexAA, AA in  enumerate(nAA):
        for index,f in enumerate(fdata):
            result[0,indexAA,index] = f
            Node.get_Node().get_Battery().set_capacity_mAh( capa_1AA*AA )
            Node.change_task_rate(Task,f)
            Node.compute()
            result[1:3,indexAA,index]= [Node.average_power,Node.lifetime] 
            result[3,indexAA,index]=(Node.get_Node().get_Battery().get_capacity_mAh())/(24*365*(Node.get_Node().get_Battery().get_i()))

    Node.get_Node().get_Battery().set_capacity_mAh( capa_1AA )
    #Task_tx.task_rate= f_initial
    Node.change_task_rate(Task,f_initial)

    fig,ax = plt.subplots(1,1)
    ax.set_xlabel("Task rate [$task/day$]")
    
    ax.set_ylabel("Node lifetime [$years$]")
    for  indexAA, AA in enumerate(nAA):
        ax.plot(result[0,indexAA,:],
                result[2,indexAA,:],
                color=dictColor["Green"])
        ax.plot(result[0,indexAA,:],
            result[3,indexAA,:],
            color=dictColor["DeepBlue"],
            linestyle="dashed")
                            

    ax2=ax.twinx()
    ax2.plot(result[0,0,:],
            result[1,0,:]*1000,
            color=dictColor["CarolinaBlue"])

    ax2.set_ylabel("Average power [$\mu W$]")

    ax.set_ylim(ymin= 0,  ymax =np.max(result[2,:,:])*1.1 )
    ax2.set_ylim(ymin= 0, ymax =np.max(result[1,:,:])*1100 )

    ax.set_title("Fdata and Ebatt : self-discharge rate = %.1f %% "%(Node.get_Node().get_Battery().get_selfdischarge_p_year()))

    if(filename != None):
        to_save= filename+".svg"
        plt.savefig(to_save, format="svg")