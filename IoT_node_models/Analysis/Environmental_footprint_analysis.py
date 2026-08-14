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

def deployment_sweep_fdata  (Replacement_strategy = False,Footprint=None,Node=None,Nyears= 100,rsd = 3,dtrans = 10, nAA = [], param = [], paramType =None, fmax=100, f_step=1, Task = None,transport_model=None,filename=None,figsize=(7,6), figAppend=None):   
    
    f_initial = Node.get_task_rate(Task)
    battery_footprint = Footprint.battery[0]
    capa_1AA = Node.get_Node().get_Battery().get_capacity_mAh()
    rsd_init = Node.get_Node().get_Battery().get_selfdischarge_p_year()

    Footprint.set_transport(dtrans,transport_model)

    fdata= np.arange(1,fmax,f_step)
    result = np.zeros((7,len(fdata),len(nAA),len(param)))

    for index, value in enumerate(param):
        if paramType == "dnode":
            d = value
        elif paramType == "rsd":
            Node.get_Node().get_Battery().set_selfdischarge_p_year(value)
        elif paramType == "dtrans":
            Footprint.set_transport(value,transport_model)

        for indexAA,AA in enumerate(nAA):
            Node.get_Node().get_Battery().set_capacity_mAh( capa_1AA*AA )
            Footprint.battery[0]      = battery_footprint *AA

            for indexf,f in enumerate(fdata):
                result[0,indexf,indexAA,index] = f
                Node.change_task_rate(Task,f)
                [res1,res2,lifetime,residue] =deployment_battery_replacement(Replacement_type = "Complete",Footprint=Footprint,Node=Node,Nyears= Nyears)
                [res3,res4,lifetime,residue] =deployment_battery_replacement(Replacement_type = "Battery" ,Footprint=Footprint,Node=Node,Nyears= Nyears)
                if lifetime > Nyears : 
                    result[1:,indexf,indexAA,index] = [0,0,0,0,0,0]
                result[1:,indexf,indexAA,index]= [res1,res2,res3,res4,lifetime,residue]


    Node.change_task_rate(Task,f_initial)
    Node.get_Node().get_Battery().set_capacity_mAh( capa_1AA )   
    Node.get_Node().get_Battery().set_selfdischarge_p_year(rsd_init)  
    Footprint.battery[0]      = battery_footprint


    if figAppend is None :
        fig,ax = plt.subplots(1,1,figsize=figsize)
    else : 
        fig = figAppend[0]
        ax  = figAppend[1]
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

    
    if figAppend is  None :
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

    else:
        ax.set_ylim( ymin= None , ymax =None )
        ax.set_xlim( xmin= None , xmax =None)

    if(filename != None):
        to_save= filename+".svg"
        plt.savefig(to_save, format="svg")

    return fig, ax

########################################################################################################
        

def deployment_sweep_ebatt  (Replacement_strategy = False,Footprint=None,Node=None,Nyears= 100,dtrans = 10, param = [], paramType =None,nAAmin = 1, nAAmax=6, nAA_step=1,transport_model=None,filename=None,figsize=(7,6), figAppend=None):   
    

    battery_footprint = Footprint.battery[0]
    capa_1AA = Node.get_Node().get_Battery().get_capacity_mAh()
    rsd_init = Node.get_Node().get_Battery().get_selfdischarge_p_year()

    Footprint.set_transport(dtrans,transport_model)

    nAAint = np.arange(nAAmin,nAAmax+1,1)
    nAA    = np.arange(nAAmin,nAAmax+1,nAA_step)
    result = np.zeros((7,len(nAA),len(param)))

    for index, value in enumerate(param):
        if paramType == "rsd":
            Node.get_Node().get_Battery().set_selfdischarge_p_year(value)
        elif paramType == "dtrans":
            Footprint.set_transport(value,transport_model)

        for indexAA,AA in enumerate(nAA):
            result[0,indexAA,index] = capa_1AA*AA
            Node.get_Node().get_Battery().set_capacity_mAh( capa_1AA*AA )
            Footprint.battery[0]      = battery_footprint *AA

            [res1,res2,lifetime,residue] =deployment_battery_replacement(Replacement_type = "Complete",Footprint=Footprint,Node=Node,Nyears= Nyears)
            [res3,res4,lifetime,residue] =deployment_battery_replacement(Replacement_type = "Battery" ,Footprint=Footprint,Node=Node,Nyears= Nyears)
            if lifetime > Nyears : 
                result[1:,indexAA,index] = [0,0,0,0,0,0]
            result[1:,indexAA,index]= [res1,res2,res3,res4,lifetime,Node.get_Node().get_Battery().get_capacity_mAh()/(24*365*Node.get_Node().get_Battery().get_i())]

    Node.get_Node().get_Battery().set_capacity_mAh( capa_1AA )   
    Node.get_Node().get_Battery().set_selfdischarge_p_year(rsd_init)  
    Footprint.battery[0]      = battery_footprint

    if figAppend is None :
        fig,ax = plt.subplots(1,1,figsize=figsize)
    else : 
        fig = figAppend[0]
        ax  = figAppend[1]
    ax.set_xlabel("Battery capacity [$mAh$]")
    ax.set_ylabel("GWP [$kgCO_2eq./year$]")

        
    colorListList = [listOrange,listGreen,listBlue,listTurquoise ]


    for index, value in enumerate(param):
        if Replacement_strategy == "Complete":
            ax.plot(result[0,:,index],   result[2,:,index],   color=colorListList[0][-(index+1)])
            ax.scatter(result[0,np.argmin(result[2,:,index]),index],np.min(result[2,:,index]),color=colorListList[0][-(index+1)],marker ="s" )
        elif Replacement_strategy == "Battery":
            ax.plot(result[0,:,index],   result[4,:,index],   color=colorListList[0][-(index+1)])
            ax.scatter(result[0,np.argmin(result[4,:,index]),index],np.min(result[4,:,index]),color=colorListList[0][-(index+1)],marker ="s" ) 
        elif Replacement_strategy == "Both":
            ax.plot(result[0,:,index],   result[2,:,index],   color=colorListList[0][-(index+1)])
            ax.plot(result[0,:,index],   result[4,:,index],   color=colorListList[0][-(index+1)],linestyle = "dashed") 
            ax.scatter(result[0,np.argmin(result[2,:,index]),index],np.min(result[2,:,index]),color=colorListList[0][-(index+1)],marker ="s" )
            ax.scatter(result[0,np.argmin(result[4,:,index]),index],np.min(result[4,:,index]),color=colorListList[0][-(index+1)],marker ="s" ) 


    if figAppend is None :
        ax.set_yscale("log")

        plt.gca().yaxis.set_major_formatter(mpl.ticker.ScalarFormatter())
        plt.gca().yaxis.set_minor_formatter(mpl.ticker.ScalarFormatter())
        plt.gca().yaxis.set_minor_formatter(mpl.ticker.NullFormatter())

        ax.set_xticks(nAAint*capa_1AA)
        ax.set_yticks([0.1,0.3,1,3,10,30])
        ax.tick_params(axis='x', labelsize = 12)

        ymin = np.min(result[(2,4),:])
        ymax = np.max(result[(2,4),:])
        ax.set_ylim( ymin= ymin/1.1  ,ymax =ymax*1.1 )
        ax.set_xlim( xmin= capa_1AA*nAAmin/1.2,xmax =capa_1AA*nAAmax)
        
        ax.set_title("Ebatt : Time period: %d years, dtrans %u m"%(Nyears,dtrans))
    
    else:
        ax.set_ylim( ymin= None , ymax =None )
        ax.set_xlim( xmin= None , xmax =None )

    if(filename != None):
        to_save= filename+".svg"
        plt.savefig(to_save, format="svg")

    return fig, ax