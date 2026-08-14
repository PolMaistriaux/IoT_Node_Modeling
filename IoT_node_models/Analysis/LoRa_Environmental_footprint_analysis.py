#%%
from matplotlib import colors, pyplot as plt
import matplotlib as mpl
import matplotlib.pyplot as plt
plt.rcParams['figure.facecolor'] = 'white'
plt.rcParams['mathtext.fontset'] = 'stix'
plt.rcParams['font.family'] = 'STIXGeneral'
plt.rcParams['font.size'] = 16
import math
import numpy as np
import inspect
import scipy.interpolate
import plotly.graph_objects as go
import plotly.express as px
import plotly.io as pio
pio.renderers.default = "svg"
from plotly.offline import plot

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from IoT_node_models.Energy_model import *
from IoT_node_models.Hardware_Modules import *
from IoT_node_models.Impact_model import *

path_to_save_svg = "SavedFiles"

########################################################################################################

def lora_deployment_sweep_dnode  (Replacement_strategy = False,Footprint=None,Node=None,Nyears= 100,  param = [], paramType =None,dmin = 5, dmax=100, d_step=1, Task_tx = None,PL_model=None,filename=None,figsize=(7,6)):   
    
    d_initial = Task_tx.get_distance()
    f_initial = Node.get_task_rate(Task_tx)
    battery_footprint = Footprint.battery[0]
    capa_1AA = Node.get_Node().get_Battery().get_capacity_mAh()
    rsd_init = Node.get_Node().get_Battery().get_selfdischarge_p_year()


    dnode= np.arange(dmin,dmax,d_step)
    result = np.zeros((7,len(dnode),len(param)))

    for index, value in enumerate(param):
        if paramType == "fdata":
            Node.change_task_rate(Task_tx,value)
        elif paramType == "rsd":
            Node.Battery.selfdischarge_p_year = value
        elif paramType == "ebatt":
            Node.get_Node().get_Battery().set_capacity_mAh(value*capa_1AA)
        #elif paramType == "dtrans":
        #    Footprint.set_transport(value,transport_model)

        for indexd,d in enumerate(dnode):
            result[0,indexd,index] = d
            Task_tx.set_distance(d)
            [res1,res2,lifetime,residue] =deployment_battery_replacement(Replacement_type = "Complete",Footprint=Footprint,Node=Node,Nyears= Nyears)
            
            [res3,res4,lifetime,residue] =deployment_battery_replacement(Replacement_type = "Battery" ,Footprint=Footprint,Node=Node,Nyears= Nyears)
            if lifetime > Nyears : 
                result[1:,indexd,index] = [0,0,0,0,0,0]
            result[1:,indexd,index]= [res1,res2,res3,res4,lifetime,(Node.get_Node().get_Battery().get_capacity_mAh())/(24*365*(Node.get_Node().get_Battery().get_i()))]
    
    Task_tx.set_distance(d_initial)
    Node.change_task_rate(Task_tx,f_initial)
    Node.get_Node().get_Battery().set_capacity_mAh( capa_1AA )   
    Node.get_Node().get_Battery().set_selfdischarge_p_year(rsd_init)  
    Footprint.battery[0]      = battery_footprint

    fig,ax = plt.subplots(1,1,figsize=figsize)
    ax.set_xlabel("Node-basestation distance [$km$]")
    ax.set_ylabel("GWP [$kgCO_2eq./year$]")

    colorListList = [listGreen, listOrange ]
    for index, value in enumerate(param):
        if Replacement_strategy == "Complete":
            ax.plot(result[0,:,index],   result[2,:,index],   color=colorListList[0][-(index+1)])
        elif Replacement_strategy == "Battery":
            ax.plot(result[0,:,index],   result[4,:,index],   color=colorListList[0][-(index+1)])
        elif Replacement_strategy == "Both":
            ax.plot(result[0,:,index],   result[2,:,index],   color=colorListList[0][-(index+1)])
            ax.plot(result[0,:,index],   result[4,:,index],   color=colorListList[0][-(index+1)],linestyle = "dashed") 


    #ax.set_xscale("log")
    ax.set_yscale("log")

    
    ax.set_title("Dnode : Time period: %d years, Fdata : %u/day, Rsd : %.1f %%"%(Nyears,Node.get_task_rate(Task_tx), Node.get_Node().get_Battery().get_selfdischarge_p_year()))
    
    ax.tick_params(axis='x', labelsize = 12)
    if(filename != None):
        to_save= filename+".svg"
        plt.savefig(to_save, format="svg")
####################################################



def lora_deployment_sweep_fdata  (Replacement_strategy = False,Footprint=None,Node=None,Nyears= 100,rsd = 3,dtrans = 10, nAA = [], param = [], paramType =None, fmax=100, f_step=1, Task_tx = None,transport_model=None,filename=None,figsize=(7,6)):
    
    f_initial = Node.get_task_rate(Task_tx)
    battery_footprint = Footprint.battery[0]
    capa_1AA = Node.get_Node().get_Battery().get_capacity_mAh()
    rsd_init = Node.get_Node().get_Battery().get_selfdischarge_p_year()
    dist_init = Task_tx.get_distance()

    Footprint.set_transport(dtrans,transport_model)

    fdata= np.arange(1,fmax,f_step)
    result = np.zeros((7,len(fdata),len(nAA),len(param)))

    for index, value in enumerate(param):
        if paramType == "dnode":
            Task_tx.set_distance(value)
        elif paramType == "rsd":
            Node.get_Node().get_Battery().set_selfdischarge_p_year(value)
        elif paramType == "dtrans":
            Footprint.set_transport(value,transport_model)

        for indexAA,AA in enumerate(nAA):
            Node.get_Node().get_Battery().set_capacity_mAh( capa_1AA*AA )
            Footprint.battery[0]      = battery_footprint *AA

            for indexf,f in enumerate(fdata):
                result[0,indexf,indexAA,index] = f
                Node.change_task_rate(Task_tx,f)
                [res1,res2,lifetime,residue] =deployment_battery_replacement(Replacement_type = "Complete",Footprint=Footprint,Node=Node,Nyears= Nyears)
                [res3,res4,lifetime,residue] =deployment_battery_replacement(Replacement_type = "Battery" ,Footprint=Footprint,Node=Node,Nyears= Nyears)
                if lifetime > Nyears : 
                    result[1:,indexf,indexAA,index] = [0,0,0,0,0,0]
                result[1:,indexf,indexAA,index]= [res1,res2,res3,res4,lifetime,residue]


    Node.change_task_rate(Task_tx,f_initial)
    Task_tx.set_distance(dist_init)
    Node.get_Node().get_Battery().set_capacity_mAh( capa_1AA )   
    Node.get_Node().get_Battery().set_selfdischarge_p_year(rsd_init)  
    Footprint.battery[0]      = battery_footprint

    fig,ax = plt.subplots(1,1,figsize=figsize)
    ax.set_xlabel("Transmission rate [$msg/day$]")
    ax.set_ylabel("GWP [$kgCO_2eq./year$]")

    colorListList = [listBlue, listTurquoise ]
    for  indexAA, param_val in enumerate(nAA):
        for index, value in enumerate(param):
            if Replacement_strategy == "Complete":
                ax.plot(result[0,:,indexAA,index],   result[2,:,indexAA,index],   color=colorListList[indexAA][-(index+1)])
            elif Replacement_strategy == "Battery":
                ax.plot(result[0,:,indexAA,index],   result[4,:,indexAA,index],   color=colorListList[indexAA][-(index+1)])
            elif Replacement_strategy == "Both":
                ax.plot(result[0,:,indexAA,index],   result[2,:,indexAA,index],   color=colorListList[indexAA][-(index+1)])
                ax.plot(result[0,:,indexAA,index],   result[4,:,indexAA,index],   color=colorListList[indexAA][-(index+1)],linestyle = "dashed") 


    ax.set_xscale("log")
    ax.set_yscale("log")
    #axP.set_yscale("log")

    plt.gca().yaxis.set_major_formatter(mpl.ticker.ScalarFormatter())
    plt.gca().yaxis.set_minor_formatter(mpl.ticker.ScalarFormatter())
    plt.gca().yaxis.set_minor_formatter(mpl.ticker.NullFormatter())

    ax.set_yticks([0.1,0.3,1,3,10,30])

    ymin = np.min(result[(2,4),:])
    ymax = np.max(result[(2,4),:])
    ax.set_ylim( ymin= ymin , ymax =ymax+1 )
    ax.set_xlim( xmin= 1/1.1 , xmax =fmax)
    
    ax.vlines(1, ymin, ymax    , linestyle = "dashed", color = "black")
    ax.vlines(24, ymin, ymax   , linestyle = "dashed", color = "black")
    ax.vlines(24*12, ymin, ymax, linestyle = "dashed", color = "black")
    ax.set_title("Fdata : Time period: %d years, Rsd : %.1f %%, Dtrans %u km"%(Nyears,Node.get_Node().get_Battery().get_selfdischarge_p_year(),dtrans))
    
    ax.tick_params(axis='x', labelsize = 12)
    if(filename != None):
        to_save= filename+".svg"
        plt.savefig(to_save, format="svg")
