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
file_path = os.path.abspath(__file__)
parent_dir_path        = os.path.dirname(file_path)
path_to_import_mainDir = os.path.dirname(parent_dir_path)
path_to_import_carac   = os.path.join(parent_dir_path,"Characterization")
path_to_import_energy  = os.path.join(parent_dir_path,"Energy_model")
path_to_import_LoRa    = os.path.join(os.path.dirname(parent_dir_path),"LoRa")
path_to_import_PL      = os.path.join(os.path.dirname(parent_dir_path),"Wireless_link")
path_to_import_PL_model= os.path.join(path_to_import_PL,"Path_loss_model")


path_to_save_svg = "D:/Pol/Documents/Research/Paper/ForestMe_Node/Figures/Generated_SVG"

sys.path.append(path_to_import_mainDir)
sys.path.append(path_to_import_carac)
sys.path.append(path_to_import_energy)
sys.path.append(path_to_import_LoRa)
sys.path.append(path_to_import_PL)
sys.path.append(path_to_import_PL_model)


import LoRa_library as LoRa
import logNormal_PL as logPL
import Path_loss_library as plLib 
import Optimal_strategy as optLoRa

from MyColors           import *
from Node_analysis      import *
from Energy_node_Lora   import *
from Node_task          import *
from Energy_node        import *
from Power_Unit         import *
from Apollo3            import *
from BME680             import *
from RFM95              import *


####################################################
class Node_BoM:
    def __init__(self,casing=[0,0,0],connectivtiy=[0,0,0],eol=[0,0,0],memory=[0,0,0],others=[0,0,0],pcb=[0,0,0],power_supply=[0,0,0],processing=[0,0,0],sensing=[0,0,0],ui=[0,0,0],transport=[0,0,0],battery=[0,0,0],placement=[0,0,0],replacement=[0,0,0],decom=[0,0,0],placementNnodes=1,replacementNnodes=1,decomNnodes=1):
        self.casing             = casing
        self.connectivtiy       = connectivtiy 
        self.eol                = eol
        self.memory             = memory
        self.others             = others 
        self.pcb                = pcb 
        self.power_supply       = power_supply 
        self.processing         = processing 
        self.sensing            = sensing
        self.ui                 = ui
        self.battery            = battery
        self.placement          = placement
        self.replacement        = replacement
        self.decom              = decom
        self.placementNnodes    = placementNnodes
        self.replacementNnodes  = replacementNnodes
        self.decomNnodes        = decomNnodes
        self.transport          = transport

        self.recompute()

    def set_transport(self,km,transport_model):
        transport_foot = transport_model(km)
        self.placement[0]    = transport_foot/self.placementNnodes
        self.replacement[0]  = transport_foot/self.replacementNnodes
        self.decom[0]        = transport_foot/self.decomNnodes


    def recompute(self):
        self.F_prod = [0,0,0]
        self.F_node = [0,0,0]
        self.F_prod[0] = self.casing[0] + self.connectivtiy[0] + self.eol[0] + self.memory[0] + self.others[0] + self.pcb[0] + self.power_supply[0] + self.processing[0] + self.sensing[0] + self.ui[0] 
        self.F_prod[1] = self.casing[1] + self.connectivtiy[1] + self.eol[1] + self.memory[1] + self.others[1] + self.pcb[1] + self.power_supply[1] + self.processing[1] + self.sensing[1] + self.ui[1] 
        self.F_prod[2] = self.casing[2] + self.connectivtiy[2] + self.eol[2] + self.memory[2] + self.others[2] + self.pcb[2] + self.power_supply[2] + self.processing[2] + self.sensing[2] + self.ui[2] 
        self.F_node[0] = self.F_prod[0] + self.battery[0]
        self.F_node[1] = self.F_prod[1] + self.battery[1]
        self.F_node[2] = self.F_prod[2] + self.battery[2]

    def plot_footprint(self,filename = None,figsize=(7,6)):
        self.recompute()
        barWidth = 0.6
        height      = np.array([self.casing[0],self.connectivtiy[0], self.eol[0],self.memory[0],self.others[0],self.pcb[0],self.power_supply[0],self.processing[0],self.sensing[0],self.ui[0],self.transport[0],self.battery[0],self.F_node[0]])
        height_e_up = np.array([self.casing[2],self.connectivtiy[2], self.eol[2],self.memory[2],self.others[2],self.pcb[2],self.power_supply[2],self.processing[2],self.sensing[2],self.ui[2],self.transport[0],self.battery[2],self.F_node[0]])
        height_e_do = np.array([self.casing[1],self.connectivtiy[1], self.eol[1],self.memory[1],self.others[1],self.pcb[1],self.power_supply[1],self.processing[1],self.sensing[1],self.ui[1],self.transport[0],self.battery[1],self.F_node[0]])
        height_n    = np.array([0             ,0                   , 0          ,0             ,0             ,0          ,0                   ,0                 ,0              ,0         ,0                ,0              ,self.battery[0]])
        xlabel      = np.array(["Casing","Connectivity","EoL" ,"Memory","Others","PCB" ,"PMU" ,"Processing","Sensing","User Interface"  ,"Transport", "Battery module", "Total"])
        color       = np.array([dictColor["CarolinaBlue"]  ,dictColor["CarolinaBlue"]        ,dictColor["CarolinaBlue"],dictColor["CarolinaBlue"]  ,dictColor["CarolinaBlue"]  ,dictColor["CarolinaBlue"],dictColor["CarolinaBlue"],dictColor["CarolinaBlue"]      ,dictColor["CarolinaBlue"]   ,dictColor["CarolinaBlue"],dictColor["Green"]    , dictColor["Sandy"] , dictColor["CarolinaBlue"] ])         
        toRemove    = [i for i in np.arange(len(height)) if height[i]==0]
        for index in toRemove[::-1]:
            height      = np.delete(height,         index)
            height_e_up = np.delete(height_e_up,    index)
            height_e_do = np.delete(height_e_do,    index)
            height_n    = np.delete(height_n,       index)
            color       = np.delete(color,          index)
            xlabel      = np.delete(xlabel,         index)

        index       = np.argsort(height)
        height      = height[index]
        height_e_up = height_e_up[index]
        height_e_do = height_e_do[index]
        xlabel      = xlabel[index]
        color       = color[index]

        ax_y_fig_span = np.max(height_e_up[:-1])*1.3
        ax_y_max      = np.max(height)*1.02

        height_e_up =        np.array(height_e_up) - np.array(height)
        height_e_do = np.abs(np.array(height_e_do) - np.array(height))

        fig,ax = plt.subplots(1,1,figsize=figsize)

        bar1 = ax.bar(xlabel,
                height = height, width =barWidth, 
                yerr = [height_e_do,height_e_up],color = color, capsize=5,edgecolor = "black")
        barn = ax.bar(xlabel,
                height = height_n, width =barWidth, 
                color = dictColor["Sandy"], capsize=5 ,edgecolor = "black")

        ax.set_ylabel("GWP [$kgCO_2 eq.$]")
        ax.set_ylim(ymin = 0, ymax = ax_y_fig_span)
        ax.tick_params(axis='x', labelrotation= 45 )
        plt.xticks(ha='right')

        for rect in bar1:
            rect_height = rect.get_height()
            toDisplay = (100*rect_height/self.F_node[0])
            plt.text(rect.get_x() + rect.get_width()/2, rect_height, f'{toDisplay:.1f}%',fontsize = 13, ha='right', va='bottom')
        plt.text(rect.get_x() + rect.get_width()*1.1, height[-2], f'{(100*self.F_prod[0]/self.F_node[0]):.1f}%',fontsize = 13, ha='left', va='bottom',rotation = -90)
        plt.text(rect.get_x() + rect.get_width()*1.1, self.battery[0]/2, f'{(100*self.battery[0]/self.F_node[0]):.1f}%',fontsize = 13, ha='left', va='center',rotation = -90)
        print(self.F_node[0])

        if(filename != None):
            to_save = filename+".svg"
            plt.savefig(to_save, format="svg")

        ####################################################

        fig,ax = plt.subplots(1,1,figsize=figsize)

        ax.bar(xlabel,
                height = height, width =barWidth, 
                color = color, capsize=5,edgecolor = "black")

        ax.set_ylabel("Carbon footprint [$kgCO_2 eq.$]")
        ax.set_ylim(ymin = ax_y_max-ax_y_fig_span, ymax = ax_y_max)
        ax.tick_params(axis='x', labelrotation= 45 )
        plt.xticks(ha='right')
        if(filename != None):
            to_save = filename+"2.svg"
            plt.savefig(to_save, format="svg")
####################################################


####################################################
def deployment_battery_replacement( Replacement_type = "Complete",Footprint=None,Node=None,Nyears= 100, d= 10 ,PL_model=None, PTX=[] , I_PTX=[]):

    [power,lifetime] = node_power(Node=Node, d= d ,PL_model=PL_model, PTX=PTX , I_PTX=I_PTX)
    Footprint.recompute()
    Placement_cost   = Footprint.F_prod[0] + Footprint.placement[0] + Footprint.battery[0]
    Decom_cost       = Footprint.decom[0]
    Replacement_cost = 0
    if Replacement_type == "Complete" : 
        Replacement_cost = Footprint.F_prod[0] + Footprint.replacement[0] + Footprint.battery[0]
    elif Replacement_type == "Battery" : 
        Replacement_cost = Footprint.replacement[0] + Footprint.battery[0]
    else:
        print("No replacement type found")
    Deployment_footprint   = Placement_cost + Decom_cost
    year = lifetime
    looping = True
    residue = 0 
    while looping :
        if year > Nyears:
            looping = False
            residue = year-Nyears
        else:
            Deployment_footprint = Deployment_footprint + Replacement_cost
            year = year + lifetime
    
    Deployment_footprint_2 = Placement_cost + Replacement_cost * np.max([0,(Nyears/lifetime)-1]) + Decom_cost
    Deployment_footprint_2 = Deployment_footprint_2/Nyears
    Deployment_footprint = Deployment_footprint/Nyears
    return [Deployment_footprint,Deployment_footprint_2,lifetime,power]
####################################################
def compare_replacement_type(Footprint=None,Node=None,Nyears= 100, nAAmax=2,d = 1000,PL_model=None, PTX=[] , I_PTX=[],filename=None,figsize=(7,6)):
    if truncature != "Continuous" and truncature != "Discrete" :
        print("No truncature model selected")
        return
    elif truncature == "Continuous":
        index_res = 2
    elif truncature == "Discrete":
        index_res = 1

    capa_1AA = Node.Battery.capacity_mAh

    res_battery  = deployment_sweep_ebatt(Replacement_type = "Battery" ,Footprint=Footprint,Node=Node,Nyears= Nyears, nAAmax=nAAmax,d = d,PL_model=PL_model, PTX=PTX , I_PTX=I_PTX)   
    res_complete = deployment_sweep_ebatt(Replacement_type = "Complete",Footprint=Footprint,Node=Node,Nyears= Nyears, nAAmax=nAAmax,d = d,PL_model=PL_model, PTX=PTX , I_PTX=I_PTX)   

    fig,ax = plt.subplots(1,1,figsize=figsize)
    
    ax.set_xlabel("Battery capacity [$mAh$]")
    ax.set_ylabel("Carbon footprint [$kgCO_2eq./year$]")
    ax.plot(res_battery[0,:],
            res_battery[index_res,:], label = "Battery replacements",
            color=dictColor["LightBlue"],
            marker="o",markersize=4)

    ax.plot(res_complete[0,:],
            res_complete[index_res,:], label = "Node replacements",
            color=dictColor["LightRed"],
            marker="o",markersize=4)

    ax2=ax.twinx()
    ax2.plot(res_battery[0,:],
            res_battery[3,:], label = "Lifetime",
            color=dictColor["Green"],
            marker="o",markersize=4)
    ax2.set_ylabel("Lifetime [$years$]")

    ax.legend()
    ax2.legend()
    ax.set_title("IoT node deployment comparison\n Time period: %d years \nBattery self-discharge is  %.1f %% and transport is %.2f kgCO_2eq."%(Nyears,Node.Battery.selfdischarge_p_year,Footprint.transport[0]))
    ax.set_xticks(res_battery[0,:])

    ax.set_ylim( ymin= 0, ymax =np.max(res_complete[index_res,:])*1.1 )
    ax2.set_ylim(ymin= 0, ymax =np.max(res_complete[3,:])*1.1 )
    ax.set_xticks(np.arange(0,nAAmax+1,1)*capa_1AA)

    ax.tick_params(axis='x', labelsize = 12)

    if(filename != None):
        to_save = filename+".svg"
        plt.savefig(to_save, format="svg")
####################################################
def deployment_sweep_dnode  (Both_Repl = False,Footprint=None,Node=None,Nyears= 100,fdata=1000,rsd = 3,dtrans = 10, nAA = [], param = [], paramType =None,dmin = 5, dmax=100, d_step=1,         Task_tx = None,PL_model=None,transport_model=None, PTX=[] , I_PTX=[],filename=None,figsize=(7,6)):   
    
    f_initial = Task_tx.task_rate
    battery_footprint = Footprint.battery[0]
    capa_1AA = Node.Battery.capacity_mAh    
    rsd_init = Node.Battery.selfdischarge_p_year

    Task_tx.task_rate= fdata
    Footprint.set_transport(dtrans,transport_model)
    Node.Battery.selfdischarge_p_year = rsd

    dnode= np.arange(dmin,dmax,d_step)
    result = np.zeros((7,len(dnode),len(nAA),len(param)))

    for index, value in enumerate(param):
        if paramType == "fdata":
            Task_tx.task_rate= value
        elif paramType == "rsd":
            Node.Battery.selfdischarge_p_year = value
        elif paramType == "dtrans":
            Footprint.set_transport(value,transport_model)

        for indexAA,AA in enumerate(nAA):
            Node.Battery.capacity_mAh = capa_1AA*AA
            Footprint.battery[0]      = battery_footprint *AA

            for indexd,d in enumerate(dnode):
                result[0,indexd,indexAA,index] = d
                [res1,res2,lifetime,residue] =deployment_battery_replacement(Replacement_type = "Complete",Footprint=Footprint,Node=Node,Nyears= Nyears, d= d ,PL_model=PL_model, PTX=PTX , I_PTX=I_PTX)
                [res3,res4,lifetime,residue] =deployment_battery_replacement(Replacement_type = "Battery" ,Footprint=Footprint,Node=Node,Nyears= Nyears, d= d ,PL_model=PL_model, PTX=PTX , I_PTX=I_PTX)
                if lifetime > Nyears : 
                    result[1:,indexd,indexAA,index] = [0,0,0,0,0,0]
                result[1:,indexd,indexAA,index]= [res1,res2,res3,res4,lifetime,Node.Battery.capacity_mAh/(24*365*Node.Battery.i)]

    Task_tx.task_rate = f_initial 
    Node.Battery.capacity_mAh         = capa_1AA      
    Node.Battery.selfdischarge_p_year = rsd_init
    Footprint.battery[0]      = battery_footprint

    fig,ax = plt.subplots(1,1,figsize=figsize)
    ax.set_xlabel("Node-basestation distance [$km$]")
    ax.set_ylabel("GWP [$kgCO_2eq./year$]")

    colorListList = [listGreen, listOrange ]
    for  indexAA, param_val in enumerate(nAA):
        for index, value in enumerate(param):
            ax.plot(result[0,:,indexAA,index]/1000,
                    result[2,:,indexAA,index],
                    color=colorListList[indexAA][(index+2)])
            if Both_Repl:
                ax.plot(result[0,:,indexAA,index]/1000,
                        result[4,:,indexAA,index],
                        color=colorGrey, linestyle = "dashed")        
    #ax.set_xscale("log")
    ax.set_yscale("log")

    ymin = np.min(result[(2,4),:])
    ymax = np.max(result[(2,4),:])
    ax.set_ylim( ymin= ymin  ,ymax =ymax+1 )
    ax.set_xlim( xmin= dmin/1e3,xmax =dmax/1e3)
    
    #ax.vlines(5, ymin, ymax    , linestyle = "dashed", color = "black")
    #ax.vlines(24, ymin, ymax   , linestyle = "dashed", color = "black")
    #ax.vlines(24*12, ymin, ymax, linestyle = "dashed", color = "black")
    ax.set_title("Dnode : Time period: %d years, Fdata : %u m, Rsd : %.1f %%, Ftrans %.1f"%(Nyears,fdata,Node.Battery.selfdischarge_p_year,placement_init))
    
    ax.tick_params(axis='x', labelsize = 12)
    if(filename != None):
        to_save = os.path.join(path_to_save_svg , filename+".svg")
        plt.savefig(to_save, format="svg")
####################################################
def deployment_sweep_rsd    (Both_Repl = False,Footprint=None,Node=None,Nyears= 100,fdata=1000,d = 1000,dtrans = 10,nAA = [], param = [], paramType =None,rsdmin = 5, rsdmax=100, rsd_step=1,   Task_tx = None,PL_model=None,transport_model=None, PTX=[] , I_PTX=[],filename=None,figsize=(7,6)):   
    
    f_initial = Task_tx.task_rate
    battery_footprint = Footprint.battery[0]
    capa_1AA = Node.Battery.capacity_mAh    
    rsd_init = Node.Battery.selfdischarge_p_year

    Task_tx.task_rate= fdata
    Footprint.set_transport(dtrans,transport_model)

    rsd= np.arange(rsdmin,rsdmax,rsd_step)
    result = np.zeros((7,len(rsd),len(nAA),len(param)))

    for index, value in enumerate(param):
        if paramType == "fdata":
            Task_tx.task_rate= value
        elif paramType == "dnode":
            d = value
        elif paramType == "dtrans":
            Footprint.set_transport(value,transport_model)

        for indexAA,AA in enumerate(nAA):
            Node.Battery.capacity_mAh = capa_1AA*AA
            Footprint.battery[0]      = battery_footprint *AA

            for indexr,Rsd in enumerate(rsd):
                result[0,indexr,indexAA,index] = Rsd
                Node.Battery.selfdischarge_p_year = Rsd
                [res1,res2,lifetime,residue] =deployment_battery_replacement(Replacement_type = "Complete",Footprint=Footprint,Node=Node,Nyears= Nyears, d= d ,PL_model=PL_model, PTX=PTX , I_PTX=I_PTX)
                [res3,res4,lifetime,residue] =deployment_battery_replacement(Replacement_type = "Battery" ,Footprint=Footprint,Node=Node,Nyears= Nyears, d= d ,PL_model=PL_model, PTX=PTX , I_PTX=I_PTX)
                if lifetime > Nyears : 
                    result[1:,indexr,indexAA,index] = [0,0,0,0,0,0]
                result[1:,indexr,indexAA,index]= [res1,res2,res3,res4,lifetime,Node.Battery.capacity_mAh/(24*365*Node.Battery.i)]

    Task_tx.task_rate = f_initial 
    Node.Battery.capacity_mAh         = capa_1AA      
    Node.Battery.selfdischarge_p_year = rsd_init
    Footprint.battery[0]      = battery_footprint
    Footprint.placement[0]    = placement_init
    Footprint.replacement[0]  = replacement_init

    fig,ax = plt.subplots(1,1,figsize=figsize)
    ax.set_xlabel("Self-discharge rate [$\%C/year$]")
    ax.set_ylabel("GWP [$kgCO_2eq./year$]")

    colorListList = [listGreen, listOrange ]
    for  indexAA, param_val in enumerate(nAA):
        for index, value in enumerate(param):
            ax.plot(result[0,:,indexAA,index],
                    result[2,:,indexAA,index],
                    color=colorListList[indexAA][(index+2)])
            if Both_Repl:
                ax.plot(result[0,:,indexAA,index],
                        result[4,:,indexAA,index],
                        color=colorGrey, linestyle = "dashed")        
    #ax.set_xscale("log")
    ax.set_yscale("log")

    ymin = np.min(result[(2,4),:])
    ymax = np.max(result[(2,4),:])
    ax.set_ylim( ymin= ymin  ,ymax =ymax+1 )
    ax.set_xlim( xmin= rsdmin,xmax =rsdmax)
    
    #ax.vlines(5, ymin, ymax    , linestyle = "dashed", color = "black")
    #ax.vlines(24, ymin, ymax   , linestyle = "dashed", color = "black")
    #ax.vlines(24*12, ymin, ymax, linestyle = "dashed", color = "black")
    ax.set_title("Rsd : Time period: %d years, Fdata : %s m, d : %u %%, Ftrans %.1f"%(Nyears,fdata,d,placement_init))
    
    ax.tick_params(axis='x', labelsize = 12)
    if(filename != None):
        to_save = os.path.join(path_to_save_svg , filename+".svg")
        plt.savefig(to_save, format="svg")
####################################################
def deployment_sweep_fdata  (Both_Repl = False,Footprint=None,Node=None,Nyears= 100,d=1000    ,rsd = 3,dtrans = 10, nAA = [], param = [], paramType =None, fmax=100, f_step=1,                  Task_tx = None,PL_model=None,transport_model=None, PTX=[] , I_PTX=[],filename=None,figsize=(7,6)):   
    
    f_initial = Task_tx.task_rate
    battery_footprint = Footprint.battery[0]
    capa_1AA = Node.Battery.capacity_mAh    
    rsd_init = Node.Battery.selfdischarge_p_year

    Footprint.set_transport(dtrans,transport_model)
    Node.Battery.selfdischarge_p_year = rsd

    fdata= np.arange(1,fmax,f_step)
    result = np.zeros((7,len(fdata),len(nAA),len(param)))

    for index, value in enumerate(param):
        if paramType == "dnode":
            d = value
        elif paramType == "rsd":
            Node.Battery.selfdischarge_p_year = value
        elif paramType == "dtrans":
            Footprint.set_transport(value,transport_model)

        for indexAA,AA in enumerate(nAA):
            Node.Battery.capacity_mAh = capa_1AA*AA
            Footprint.battery[0]      = battery_footprint *AA

            for indexf,f in enumerate(fdata):
                result[0,indexf,indexAA,index] = f
                Task_tx.task_rate= f
                [res1,res2,lifetime,residue] =deployment_battery_replacement(Replacement_type = "Complete",Footprint=Footprint,Node=Node,Nyears= Nyears, d= d ,PL_model=PL_model, PTX=PTX , I_PTX=I_PTX)
                [res3,res4,lifetime,residue] =deployment_battery_replacement(Replacement_type = "Battery" ,Footprint=Footprint,Node=Node,Nyears= Nyears, d= d ,PL_model=PL_model, PTX=PTX , I_PTX=I_PTX)
                if lifetime > Nyears : 
                    result[1:,indexf,indexAA,index] = [0,0,0,0,0,0]
                result[1:,indexf,indexAA,index]= [res1,res2,res3,res4,lifetime,residue]

    Task_tx.task_rate = f_initial 
    Node.Battery.capacity_mAh         = capa_1AA      
    Node.Battery.selfdischarge_p_year = rsd_init
    Footprint.battery[0]      = battery_footprint

    fig,ax = plt.subplots(1,1,figsize=figsize)
    ax.set_xlabel("Transmission rate [$msg/day$]")
    ax.set_ylabel("GWP [$kgCO_2eq./year$]")

    colorListList = [listBlue, listTurquoise ]
    for  indexAA, param_val in enumerate(nAA):
        for index, value in enumerate(param):
            ax.plot(result[0,:,indexAA,index],
                    result[2,:,indexAA,index],
                    color=colorListList[indexAA][-(index+1)])
            '''if Both_Repl:
                ax.plot(result[0,:,indexAA,index],
                        result[4,:,indexAA,index],
                        color=colorGrey, linestyle = "dashed")  ''' 
    
    '''axP = ax.twinx()
    axP.set_ylabel("Current [$mA$]")
    axP.plot(result[0,:,0,0],
            result[6,:,0,0],
            color="black")'''

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
    ax.set_title("Fdata : Time period: %d years, distance : %s m, Rsd : %.1f %%, Dtrans %u km"%(Nyears,d,Node.Battery.selfdischarge_p_year,dtrans))
    
    ax.tick_params(axis='x', labelsize = 12)
    if(filename != None):
        to_save = os.path.join(path_to_save_svg , filename+".svg")
        plt.savefig(to_save, format="svg")
####################################################
def deployment_sweep_dtrans (Both_Repl = False,Footprint=None,Node=None,Nyears= 100,d=1000    ,rsd = 3,fdata = 24,  nAA = [], param = [], paramType =None, dmin =1,dmax=100, d_step=1,          Task_tx = None,PL_model=None,transport_model=None, PTX=[] , I_PTX=[],filename=None,figsize=(7,6)):   
    
    f_initial = Task_tx.task_rate
    battery_footprint = Footprint.battery[0]
    capa_1AA = Node.Battery.capacity_mAh    
    rsd_init = Node.Battery.selfdischarge_p_year

    Task_tx.task_rate = fdata
    Node.Battery.selfdischarge_p_year = rsd

    dtrans= np.arange(dmin,dmax,d_step)
    result = np.zeros((7,len(dtrans),len(nAA),len(param)))

    for index, value in enumerate(param):
        if paramType == "dnode":
            d = value
        elif paramType == "rsd":
            Node.Battery.selfdischarge_p_year = value
        elif paramType == "fdata":
            Task_tx.task_rate= value


        for indexAA,AA in enumerate(nAA):
            Node.Battery.capacity_mAh = capa_1AA*AA
            Footprint.battery[0]      = battery_footprint *AA

            for indexd,dt in enumerate(dtrans):
                result[0,indexd,indexAA,index] = dt
                Footprint.set_transport(dt,transport_model)
                [res1,res2,lifetime,residue] =deployment_battery_replacement(Replacement_type = "Complete",Footprint=Footprint,Node=Node,Nyears= Nyears, d= d ,PL_model=PL_model, PTX=PTX , I_PTX=I_PTX)
                [res3,res4,lifetime,residue] =deployment_battery_replacement(Replacement_type = "Battery" ,Footprint=Footprint,Node=Node,Nyears= Nyears, d= d ,PL_model=PL_model, PTX=PTX , I_PTX=I_PTX)
                result[1:,indexd,indexAA,index]= [res1,res2,res3,res4,lifetime,Node.Battery.capacity_mAh/(24*365*Node.Battery.i)]
                if lifetime > Nyears : 
                    result[1:,indexd,indexAA,index] = [0,0,0,0,0,0]

    Task_tx.task_rate = f_initial 
    Node.Battery.capacity_mAh         = capa_1AA      
    Node.Battery.selfdischarge_p_year = rsd_init
    Footprint.battery[0]      = battery_footprint

    fig,ax = plt.subplots(1,1,figsize=figsize)
    ax.set_xlabel("Transport distance [$km$]")
    ax.set_ylabel("GWP [$kgCO_2eq./year$]")

    colorListList = [listBlue, listTurquoise ]
    for  indexAA, param_val in enumerate(nAA):
        for index, value in enumerate(param):
            ax.plot(result[0,:,indexAA,index],
                    result[2,:,indexAA,index],
                    color=colorListList[indexAA][-(index+1)])
            if Both_Repl:
                ax.plot(result[0,:,indexAA,index],
                        result[4,:,indexAA,index],
                        color=colorGrey, linestyle = "dashed")        
    ax.set_xscale("log")
    ax.set_yscale("log")

    '''ymin = np.min(result[(2,4),:])
    ymax = np.max(result[(2,4),:])
    ax.set_ylim( ymin= ymin , ymax =ymax+1 )
    ax.set_xlim( xmin= dmin/1.1 , xmax =dmax)'''
    
    #ax.vlines(1, ymin, ymax    , linestyle = "dashed", color = "black")
    #ax.vlines(24, ymin, ymax   , linestyle = "dashed", color = "black")
    #ax.vlines(24*12, ymin, ymax, linestyle = "dashed", color = "black")
    ax.set_title("Dtrans : Time period: %d years, distance : %s m, Rsd : %.1f %%, fdata %.1f msd/d"%(Nyears,d,Node.Battery.selfdischarge_p_year,fdata))
    
    ax.tick_params(axis='x', labelsize = 12)
    if(filename != None):
        to_save = os.path.join(path_to_save_svg , filename+".svg")
        plt.savefig(to_save, format="svg")
####################################################
def deployment_sweep_ebatt  (Both_Repl = False,Footprint=None,Node=None,Nyears= 100,fdata=1000,d = 1000,dtrans = 10,rsd = [], param = [], paramType =None,nAAmin = 1, nAAmax=6, nAA_step=1,     Task_tx = None,PL_model=None,transport_model=None, PTX=[] , I_PTX=[],filename=None,figsize=(7,6)):   
    
    f_initial = Task_tx.task_rate
    battery_footprint = Footprint.battery[0]
    capa_1AA = Node.Battery.capacity_mAh    
    rsd_init = Node.Battery.selfdischarge_p_year

    Task_tx.task_rate= fdata
    Footprint.set_transport(dtrans,transport_model)

    nAAint = np.arange(nAAmin,nAAmax+1,1)
    nAA    = np.arange(nAAmin,nAAmax+1,nAA_step)
    result = np.zeros((7,len(nAA),len(rsd),len(param)))

    for index, value in enumerate(param):
        if paramType == "fdata":
            Task_tx.task_rate= value
        elif paramType == "dnode":
            d = value
        elif paramType == "dtrans":
            Footprint.set_transport(value,transport_model)

        for indexR,Rsd in enumerate(rsd):
            Node.Battery.selfdischarge_p_year = Rsd

            for indexAA,AA in enumerate(nAA):
                result[0,indexAA,indexR,index] = capa_1AA*AA
                Node.Battery.capacity_mAh = capa_1AA*AA
                Footprint.battery[0]      = battery_footprint *AA
                [res1,res2,lifetime,residue] =deployment_battery_replacement(Replacement_type = "Complete",Footprint=Footprint,Node=Node,Nyears= Nyears, d= d ,PL_model=PL_model, PTX=PTX , I_PTX=I_PTX)
                [res3,res4,lifetime,residue] =deployment_battery_replacement(Replacement_type = "Battery" ,Footprint=Footprint,Node=Node,Nyears= Nyears, d= d ,PL_model=PL_model, PTX=PTX , I_PTX=I_PTX)
                if lifetime > Nyears : 
                    result[1:,indexAA,indexR,index] = [0,0,0,0,0,0]
                result[1:,indexAA,indexR,index]= [res1,res2,res3,res4,lifetime,Node.Battery.capacity_mAh/(24*365*Node.Battery.i)]

    Task_tx.task_rate = f_initial 
    Node.Battery.capacity_mAh         = capa_1AA      
    Node.Battery.selfdischarge_p_year = rsd_init
    Footprint.battery[0]      = battery_footprint

    fig,ax = plt.subplots(1,1,figsize=figsize)
    ax.set_xlabel("Battery capacity [$mAh$]")
    ax.set_ylabel("GWP [$kgCO_2eq./year$]")

        
    colorListList = [listOrange,listGreen,listBlue,listTurquoise ]
    for  indexR, param_val in enumerate(rsd):
        for index, value in enumerate(param):
            ax.plot(result[0,:,indexR,index],
                    result[2,:,indexR,index],
                    color=colorListList[indexR][-(index+2)])
            ax.scatter(result[0,np.argmin(result[2,:,indexR,index]),indexR,index],np.min(result[2,:,indexR,index]),color=colorListList[indexR][-(index+2)],marker ="s" )   
        
            if Both_Repl:
                ax.plot(result[0,:,indexR,index],
                        result[4,:,indexR,index],
                        color=colorListList[indexR][-(index+2)], linestyle = "dashed") 
                ax.scatter(result[0,np.argmin(result[4,:,indexR,index]),indexR,index],np.min(result[4,:,indexR,index]),color=colorListList[indexR][-(index+2)],marker ="s" )   
               
    #ax.set_xscale("log")
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
    
    #ax.vlines(5, ymin, ymax    , linestyle = "dashed", color = "black")
    #ax.vlines(24, ymin, ymax   , linestyle = "dashed", color = "black")
    #ax.vlines(24*12, ymin, ymax, linestyle = "dashed", color = "black")
    ax.set_title("Ebatt : Time period: %d years, Fdata : %s msg/d, d : %u m, dtrans %u m"%(Nyears,fdata,d,dtrans))

    if(filename != None):
        to_save = os.path.join(path_to_save_svg , filename+".svg")
        plt.savefig(to_save, format="svg")
####################################################

####################################################
def deployment_ebatt_HP_LP (Tasks_to_swap = [],Footprint=None,Node=None,Nyears= 100,fdata=1000,d = 1000,dtrans = 10,rsd = 3, param = [], paramType =None,nAAmin = 1, nAAmax=6, nAA_step=1,     Task_tx = None,PL_model=None,transport_model=None, PTX=[] , I_PTX=[],filename=None,figsize=(7,6)):   
    
    f_initial = Task_tx.task_rate
    battery_footprint = Footprint.battery[0]
    capa_1AA = Node.Battery.capacity_mAh    
    rsd_init = Node.Battery.selfdischarge_p_year

    Task_tx.task_rate= fdata
    Footprint.set_transport(dtrans,transport_model)
    Node.Battery.selfdischarge_p_year = rsd

    nAAint= np.arange(nAAmin,nAAmax+1,1)
    nAA   = np.arange(nAAmin,nAAmax+1,nAA_step)
    result = np.zeros((6,len(nAA),len(param)))

    node.remove_task(Tasks_to_swap[1])
    node.add_task(   Tasks_to_swap[0])
    for index, value in enumerate(param):
        if paramType == "fdata":
            Task_tx.task_rate= value
        elif paramType == "dnode":
            d = value
        elif paramType == "rsd":
            Node.Battery.selfdischarge_p_year = value
        elif paramType == "dtrans":
            Footprint.set_transport(value,transport_model)

        for indexAA,AA in enumerate(nAA):
            result[0,indexAA,index] = capa_1AA*AA
            Node.Battery.capacity_mAh = capa_1AA*AA
            Footprint.battery[0]      = battery_footprint *AA
            [res1,res2,lifetime,residue] =deployment_battery_replacement(Replacement_type = "Complete",Footprint=Footprint,Node=Node,Nyears= Nyears, d= d ,PL_model=PL_model, PTX=PTX , I_PTX=I_PTX)
            
            node.remove_task(Tasks_to_swap[0])
            node.add_task(   Tasks_to_swap[1])
            
            [res3,res4,lifetime,residue] =deployment_battery_replacement(Replacement_type = "Complete",Footprint=Footprint,Node=Node,Nyears= Nyears, d= d ,PL_model=PL_model, PTX=PTX , I_PTX=I_PTX)
            result[1:,indexAA,index]= [res1,res2,res3,res4,lifetime]
            node.remove_task(Tasks_to_swap[1])
            node.add_task(   Tasks_to_swap[0])


    Task_tx.task_rate = f_initial 
    Node.Battery.capacity_mAh         = capa_1AA      
    Node.Battery.selfdischarge_p_year = rsd_init
    Footprint.battery[0]      = battery_footprint

    fig,ax = plt.subplots(1,1,figsize=figsize)
    ax.set_xlabel("Battery capacity [$mAh$]")
    ax.set_ylabel("GWP [$kgCO_2eq./year$]")

    ax.plot(result[0,:,0],
            result[2,:,0],
            color=listRed[2], linestyle = "dashed")
    ax.plot(result[0,:,0],
            result[4,:,0],
            color=listGreen[3], linestyle = "dashed")   
    colorListList = [listGreen, listOrange,listBlue,listTurquoise ]
    for index, value in enumerate(param[1:]):
        ax.plot(result[0,:,index+1],
                result[2,:,index+1],
                color=listRed[(index+2)])
        ax.scatter(result[0,np.argmin(result[2,:,index+1]),index+1],np.min(result[2,:,index+1]),color=listRed[(index+2)],marker ="s" )
        ax.plot(result[0,:,index+1],
                result[4,:,index+1],
                color=listGreen[(index+4)])    
        ax.scatter(result[0,np.argmin(result[4,:,index+1]),index+1],np.min(result[4,:,index+1]),color=listGreen[(index+4)],marker ="s" )   
        #ax.hlines(np.min(result[4,:,index+1]),  capa_1AA*nAAmin/1.05, capa_1AA*nAAmax, linestyle = "dashed", color = "black")
    #ax.set_xscale("log")
    ax.set_yscale("log")
    
    plt.gca().yaxis.set_major_formatter(mpl.ticker.ScalarFormatter())
    plt.gca().yaxis.set_minor_formatter(mpl.ticker.ScalarFormatter())
    plt.gca().yaxis.set_minor_formatter(mpl.ticker.NullFormatter())

    ax.set_xticks(nAAint*capa_1AA)
    ax.set_yticks([0.1,0.3,1,3,10,30])
    ax.tick_params(axis='x', labelsize = 12)

    ymin = np.min(result[(2,4),:,:])
    ymax = np.max(result[(2,4),:,:])
    ax.set_ylim( ymin= ymin/1.2  ,ymax =ymax+1 )
    ax.set_xlim( xmin= capa_1AA*nAAmin/1.2,xmax =capa_1AA*nAAmax)
    
    #ax.vlines(5, ymin, ymax    , linestyle = "dashed", color = "black")
    #ax.vlines(24, ymin, ymax   , linestyle = "dashed", color = "black")
    #ax.vlines(24*12, ymin, ymax, linestyle = "dashed", color = "black")
    ax.set_title("Ebatt HP-LP: Time period: %d years, Fdata : %s msg/d, d : %u m, dtrans %u m"%(Nyears,fdata,d,dtrans))

    if(filename != None):
        to_save = os.path.join(path_to_save_svg , filename+".svg")
        plt.savefig(to_save, format="svg")
####################################################


####################################################
def E_F_comp_dtrans (Both_Repl = False,Footprint=None,Cost=None,Node=None,Nyears= 100,d=1000 ,rsd = 3,fdata = 24, nAA=1 , param = [], paramType =None, dmin =1,dmax=100, d_step=1,              Task_tx = None,PL_model=None,trans_F_model=None,trans_C_model=None, PTX=[] , I_PTX=[],filename=None,figsize=(7,6)):   
    
    f_initial = Task_tx.task_rate
    battery_footprint = Footprint.battery[0]
    battery_cost      = Cost.battery[0]
    capa_1AA = Node.Battery.capacity_mAh    
    rsd_init = Node.Battery.selfdischarge_p_year

    Task_tx.task_rate = fdata
    Node.Battery.selfdischarge_p_year = rsd
    Node.Battery.capacity_mAh = capa_1AA*nAA
    Footprint.battery[0]      = battery_footprint*nAA
    Cost.battery[0]           = battery_cost     *nAA

    dtrans= np.arange(dmin,dmax,d_step)
    result = np.zeros((6,len(dtrans),len(param)))

    for index, value in enumerate(param):
        if paramType == "dnode":
            d = value
        elif paramType == "rsd":
            Node.Battery.selfdischarge_p_year = value
        elif paramType == "fdata":
            Task_tx.task_rate= value
        elif paramType == "C":
            Node.Battery.capacity_mAh = capa_1AA*value
            Footprint.battery[0]      = battery_footprint *value
            Cost.battery[0]         = battery_cost      *value

        for indexd,dt in enumerate(dtrans):
            result[0,indexd,index] = dt
            Footprint.set_transport(dt,trans_F_model)
            [dummy,Fcomp,lifetime,dummy] =deployment_battery_replacement(Replacement_type = "Complete",Footprint=Footprint,Node=Node,Nyears= Nyears, d= d ,PL_model=PL_model, PTX=PTX , I_PTX=I_PTX)
            [dummy,Fbatt,lifetime,dummy] =deployment_battery_replacement(Replacement_type = "Battery" ,Footprint=Footprint,Node=Node,Nyears= Nyears, d= d ,PL_model=PL_model, PTX=PTX , I_PTX=I_PTX)
            
            Cost.set_transport(dt,trans_C_model)
            [dummy,Ccomp,lifetime,dummy] =deployment_battery_replacement(Replacement_type = "Complete",Footprint=Cost,Node=Node,Nyears= Nyears, d= d ,PL_model=PL_model, PTX=PTX , I_PTX=I_PTX)
            [dummy,Cbatt,lifetime,dummy] =deployment_battery_replacement(Replacement_type = "Battery" ,Footprint=Cost,Node=Node,Nyears= Nyears, d= d ,PL_model=PL_model, PTX=PTX , I_PTX=I_PTX)
            if lifetime > Nyears : 
                result[1:,indexd,index] = [0,0,0,0,0,0]
            result[1:,indexd,index]= [Fcomp,Fbatt,Ccomp,Cbatt,lifetime]

    Task_tx.task_rate = f_initial 
    Node.Battery.capacity_mAh         = capa_1AA      
    Node.Battery.selfdischarge_p_year = rsd_init
    Footprint.battery[0]      = battery_footprint
    Cost.battery[0]      = battery_cost

    fig,axF = plt.subplots(1,1,figsize=figsize)
    axF.set_xlabel("Transport distance [$km$]")
    axF.set_ylabel("GWP [$kgCO_2eq./year$]")
    for index, value in enumerate(param):
        axF.plot(result[0,:,index],
                result[1,:,index],
                color=listGreen[-(index+1)])
        if Both_Repl:
            axF.plot(result[0,:,index],
                    result[2,:,index],
                    listGreen[-(index+1)], linestyle = "dashed") 

    axC = axF.twinx()
    axC.set_ylabel("Cost [$\txteuro/year$]")
    for index, value in enumerate(param):
        axC.plot(result[0,:,index],
                result[3,:,index],
                color=listRed[-(index+1)])
        if Both_Repl:
            axC.plot(result[0,:,index],
                    result[4,:,index],
                    color=listRed[-(index+1)], linestyle = "dashed")        
    axC.set_xscale("log")
    axC.set_yscale("log")
    axF.set_xscale("log")
    axF.set_yscale("log")

    yminF= np.min(result[(1,2),:]) 
    ymaxF =np.max(result[(1,2),:])
    sc = 10
    ymin = 0.1
    ymax = 10
    axF.set_ylim( ymin= ymin    , ymax =ymax)
    axC.set_ylim( ymin= ymin*sc , ymax =ymax*sc)
    axF.set_xlim( xmin= dmin/1.1 , xmax =dmax)
    axC.set_xlim( xmin= dmin/1.1 , xmax =dmax)
    
    #ax.vlines(1, ymin, ymax    , linestyle = "dashed", color = "black")
    #ax.vlines(24, ymin, ymax   , linestyle = "dashed", color = "black")
    #ax.vlines(24*12, ymin, ymax, linestyle = "dashed", color = "black")
    axF.set_title("Dtrans : Time period: %d years, distance : %s m, Rsd : %.1f %%, fdata %.1f msd/d"%(Nyears,d,Node.Battery.selfdischarge_p_year,fdata))
    
    axF.tick_params(axis='x', labelsize = 12)
    if(filename != None):
        to_save = os.path.join(path_to_save_svg , filename+".svg")
        plt.savefig(to_save, format="svg")
####################################################
def E_F_comp_fdata (Both_Repl = False,Footprint=None,Cost=None,Node=None,Nyears= 100,d=1000 ,rsd = 3,dtrans = 10, nAA=1 , param = [], paramType =None, fmin =1,fmax=100, f_step=1,              Task_tx = None,PL_model=None,trans_F_model=None,trans_C_model=None, PTX=[] , I_PTX=[],filename=None,figsize=(7,6)):   
    
    f_initial = Task_tx.task_rate
    battery_footprint = Footprint.battery[0]
    battery_cost      = Cost.battery[0]
    capa_1AA = Node.Battery.capacity_mAh    
    rsd_init = Node.Battery.selfdischarge_p_year

    Node.Battery.selfdischarge_p_year = rsd
    Node.Battery.capacity_mAh = capa_1AA*nAA
    Footprint.battery[0]      = battery_footprint*nAA
    Cost.battery[0]           = battery_cost     *nAA
    Footprint.set_transport(dtrans,trans_F_model)
    Cost.set_transport(dtrans,trans_C_model)

    fdata= np.arange(fmin,fmax,f_step)
    result = np.zeros((6,len(fdata),len(param)))

    for index, value in enumerate(param):
        if paramType == "dnode":
            d = value
        elif paramType == "rsd":
            Node.Battery.selfdischarge_p_year = value
        elif paramType == "dtrans":
            Footprint.set_transport(value,trans_F_model)
            Cost.set_transport(value,trans_C_model)
        elif paramType == "C":
            Node.Battery.capacity_mAh = capa_1AA*value
            Footprint.battery[0]    = battery_footprint *value
            Cost.battery[0]         = battery_cost      *value

        for indexf,f in enumerate(fdata):
            result[0,indexf,index] = f
            Task_tx.task_rate= f
            [dummy,Fcomp,lifetime,dummy] =deployment_battery_replacement(Replacement_type = "Complete",Footprint=Footprint,Node=Node,Nyears= Nyears, d= d ,PL_model=PL_model, PTX=PTX , I_PTX=I_PTX)
            [dummy,Fbatt,lifetime,dummy] =deployment_battery_replacement(Replacement_type = "Battery" ,Footprint=Footprint,Node=Node,Nyears= Nyears, d= d ,PL_model=PL_model, PTX=PTX , I_PTX=I_PTX)
            
            [dummy,Ccomp,lifetime,dummy] =deployment_battery_replacement(Replacement_type = "Complete",Footprint=Cost,Node=Node,Nyears= Nyears, d= d ,PL_model=PL_model, PTX=PTX , I_PTX=I_PTX)
            [dummy,Cbatt,lifetime,dummy] =deployment_battery_replacement(Replacement_type = "Battery" ,Footprint=Cost,Node=Node,Nyears= Nyears, d= d ,PL_model=PL_model, PTX=PTX , I_PTX=I_PTX)
            if lifetime > Nyears : 
                result[1:,indexf,index] = [0,0,0,0,0,0]
            result[1:,indexf,index]= [Fcomp,Fbatt,Ccomp,Cbatt,lifetime]

    Task_tx.task_rate = f_initial 
    Node.Battery.capacity_mAh         = capa_1AA      
    Node.Battery.selfdischarge_p_year = rsd_init
    Footprint.battery[0]      = battery_footprint
    Cost.battery[0]      = battery_cost

    fig,axF = plt.subplots(1,1,figsize=figsize)
    axF.set_xlabel("Transmission rate [$msg/day$]")
    axF.set_ylabel("GWP [$kgCO_2eq./year$]")
    for index, value in enumerate(param):
        axF.plot(result[0,:,index],
                result[1,:,index],
                color=listGreen[-(index+1)])
        if Both_Repl:
            axF.plot(result[0,:,index],
                    result[2,:,index],
                    listGreen[-(index+1)], linestyle = "dashed") 

    axC = axF.twinx()
    axC.set_ylabel("Cost [$\txteuro/year$]")
    for index, value in enumerate(param):
        axC.plot(result[0,:,index],
                result[3,:,index],
                color=listRed[-(index+1)])
        if Both_Repl:
            axC.plot(result[0,:,index],
                    result[4,:,index],
                    color=listRed[-(index+1)], linestyle = "dashed")        
    axC.set_xscale("log")
    axC.set_yscale("log")
    axF.set_xscale("log")
    axF.set_yscale("log")

    yminF= np.min(result[(1,2),:]) 
    ymaxF =np.max(result[(1,2),:])
    sc = 3
    ymin = 0.1
    ymax = 50
    axF.set_ylim( ymin= ymin    , ymax =ymax)
    axC.set_ylim( ymin= ymin*sc , ymax =ymax*sc)
    axF.set_xlim( xmin= fmin/1.1 , xmax =fmax)
    axC.set_xlim( xmin= fmin/1.1 , xmax =fmax)
    
    #ax.vlines(1, ymin, ymax    , linestyle = "dashed", color = "black")
    #ax.vlines(24, ymin, ymax   , linestyle = "dashed", color = "black")
    #ax.vlines(24*12, ymin, ymax, linestyle = "dashed", color = "black")
    axF.set_title("Fdata : Time period: %d years, distance : %s m, Rsd : %.1f %%, dtrans %u km"%(Nyears,d,Node.Battery.selfdischarge_p_year,dtrans))
    
    axF.tick_params(axis='x', labelsize = 12)
    if(filename != None):
        to_save = os.path.join(path_to_save_svg , filename+".svg")
        plt.savefig(to_save, format="svg")
####################################################
def E_F_comp_ebatt (Both_Repl = False,Footprint=None,Cost=None,Node=None,Nyears= 100,d=1000 ,rsd = 3,dtrans = 10,fdata=24 , param = [], paramType =None, nAAmin =1,nAAmax=100, nAA_step=1,      Task_tx = None,PL_model=None,trans_F_model=None,trans_C_model=None, PTX=[] , I_PTX=[],filename=None,figsize=(7,6)):   
    
    f_initial = Task_tx.task_rate
    battery_footprint = Footprint.battery[0]
    battery_cost      = Cost.battery[0]
    capa_1AA = Node.Battery.capacity_mAh    
    rsd_init = Node.Battery.selfdischarge_p_year
    Footprint.set_transport(dtrans,trans_F_model)
    Cost.set_transport(dtrans,trans_C_model)

    Node.Battery.selfdischarge_p_year = rsd
    Task_tx.task_rate           = fdata


    nAA= np.arange(nAAmin,nAAmax+1,nAA_step)
    result = np.zeros((6,len(nAA),len(param)))

    for index, value in enumerate(param):
        if paramType == "dnode":
            d = value
        elif paramType == "rsd":
            Node.Battery.selfdischarge_p_year = value
        elif paramType == "dtrans":
            transport_footprint = trans_F_model(value)
            Footprint.set_transport(value,trans_F_model)
            Cost.set_transport(value,trans_C_model)
        elif paramType == "fdata":
            Task_tx.task_rate= value

        for indexAA,AA in enumerate(nAA):
            result[0,indexAA,index] = AA
            Node.Battery.capacity_mAh = capa_1AA*AA
            Footprint.battery[0]      = battery_footprint*AA
            Cost.battery[0]           = battery_cost     *AA
            [dummy,Fcomp,lifetime,dummy] =deployment_battery_replacement(Replacement_type = "Complete",Footprint=Footprint,Node=Node,Nyears= Nyears, d= d ,PL_model=PL_model, PTX=PTX , I_PTX=I_PTX)
            [dummy,Fbatt,lifetime,dummy] =deployment_battery_replacement(Replacement_type = "Battery" ,Footprint=Footprint,Node=Node,Nyears= Nyears, d= d ,PL_model=PL_model, PTX=PTX , I_PTX=I_PTX)
            
            [dummy,Ccomp,lifetime,dummy] =deployment_battery_replacement(Replacement_type = "Complete",Footprint=Cost,Node=Node,Nyears= Nyears, d= d ,PL_model=PL_model, PTX=PTX , I_PTX=I_PTX)
            [dummy,Cbatt,lifetime,dummy] =deployment_battery_replacement(Replacement_type = "Battery" ,Footprint=Cost,Node=Node,Nyears= Nyears, d= d ,PL_model=PL_model, PTX=PTX , I_PTX=I_PTX)
            if lifetime > Nyears : 
                result[1:,indexAA,index] = [0,0,0,0,0]
            result[1:,indexAA,index]= [Fcomp,Fbatt,Ccomp,Cbatt,lifetime]

    Task_tx.task_rate = f_initial 
    Node.Battery.capacity_mAh         = capa_1AA      
    Node.Battery.selfdischarge_p_year = rsd_init
    Footprint.battery[0]      = battery_footprint
    Cost.battery[0]      = battery_cost

    fig,axF = plt.subplots(1,1,figsize=figsize)
    axF.set_xlabel("Battery capacity [$mAh$]")
    axF.set_ylabel("GWP [$kgCO_2eq./year$]")
    for index, value in enumerate(param):
        axF.plot(result[0,:,index]*capa_1AA,
                result[1,:,index],
                color=listGreen[-(index+1)])
        if Both_Repl:
            axF.plot(result[0,:,index]*capa_1AA,
                    result[2,:,index],
                    listGreen[-(index+1)], linestyle = "dashed") 

    axC = axF.twinx()
    axC.set_ylabel("Cost [$\txteuro/year$]")
    for index, value in enumerate(param):
        axC.plot(result[0,:,index]*capa_1AA,
                result[3,:,index],
                color=listRed[-(index+1)])
        if Both_Repl:
            axC.plot(result[0,:,index]*capa_1AA,
                    result[4,:,index],
                    color=listRed[-(index+1)], linestyle = "dashed")        
    #axC.set_xscale("log")
    axC.set_yscale("log")
    #axF.set_xscale("log")
    axF.set_yscale("log")

    
    yminF= np.min(result[(1,2),:]) 
    ymaxF =np.max(result[(1,2),:])
    sc =3
    ymin = 1/1.5
    ymax = 20
    axF.set_ylim( ymin= ymin    , ymax =ymax)
    axC.set_ylim( ymin= ymin*sc , ymax =ymax*sc)
    axF.set_xlim( xmin= nAAmin*capa_1AA/1.1 , xmax =nAAmax*capa_1AA)
    axC.set_xlim( xmin= nAAmin*capa_1AA/1.1 , xmax =nAAmax*capa_1AA)
    
    #ax.vlines(1, ymin, ymax    , linestyle = "dashed", color = "black")
    #ax.vlines(24, ymin, ymax   , linestyle = "dashed", color = "black")
    #ax.vlines(24*12, ymin, ymax, linestyle = "dashed", color = "black")
    axF.set_title("Ebatt : Time period: %d years, \ndistance : %s m, Rsd : %.1f %%, dtrans %u km, fdata: %u msg/day"%(Nyears,d,Node.Battery.selfdischarge_p_year,dtrans,fdata))
    
    axF.tick_params(axis='x', labelsize = 12)
    if(filename != None):
        to_save = os.path.join(path_to_save_svg , filename+".svg")
        plt.savefig(to_save, format="svg")
####################################################
def transport_footprint(km_one_way = 10, type ="Unit", weight_g = 500, footprint_p_tkm = 0.545,unit_factor = 1,footprint_p_km = 0.350,km_fixed=5):
    km = 2* km_one_way
    if(type == "Unit"):
        return (km_fixed+km*unit_factor)* footprint_p_km
    elif type =="Per_tkm":
        return km*footprint_p_tkm*weight_g/10e6
    else: 
        print("Error in type specification for transport footprint calculation")
####################################################
def transport_cost(worker = 1, salary_p_hour = 20, work_hour =1, km_p_h = 50,km_one_way = 10, type ="Unit", weight_g = 500, cost_p_tkm = 0.545,unit_factor = 1,cost_p_km = 6*2):
    km = 2* km_one_way
    transp_hour = km /km_p_h
    fixed_cost = worker*salary_p_hour * (work_hour + transp_hour)
    if(type == "Unit"):
        return fixed_cost + cost_p_km*km*unit_factor
    elif type =="Per_tkm":
        return fixed_cost + km*cost_p_tkm*weight_g/10e6
    else: 
        print("Error in type specification for transport footprint calculation")
####################################################


transport_f =transport_footprint(km_one_way = 10, type ="Unit", 
                                weight_g = 500,  footprint_p_tkm = 0.545,
                                unit_factor = 1,footprint_p_km = 0.350)
transport_c =   transport_cost( worker = 1, salary_p_hour = 20, work_hour =0.3, km_p_h = 50,km_one_way = 10, 
                                type ="Unit", 
                                weight_g = 500, cost_p_tkm =  0.2/1e3,
                                unit_factor = 1,cost_p_km = 0.2)
    
show = 0

AA_series = 3
AA_footprint = 0.165
AA_cost      = 0.25 
Batt_footprint = AA_series*AA_footprint
Batt_cost      = AA_series*AA_cost

node_footprint = Node_BoM(  casing            =[0.709,    0.3932, 1.3259], #709
                            connectivtiy      =[0.517,    0.2262, 0.5817],
                            eol               =[0.0812,   0.0388, 0.1201],
                            memory            =[0,        0,      0     ],
                            others            =[0.0938,   0.0546, 0.1394],
                            pcb               =[1.17,     0.9403, 1.5696], #1.17
                            power_supply      =[0.132,    0.0446, 0.1751],
                            processing        =[0.366,    0.3665, 0.4537],
                            sensing           =[0.0539,   0.0539, 0.5561],
                            ui                =[0.0306,   0.0017, 0.1155],
                            transport         =[transport_f*show,transport_f*show,transport_f*show],
                            battery           =[Batt_footprint  ,Batt_footprint,Batt_footprint],
                            placement         =[transport_f,transport_f,transport_f],
                            replacement       =[transport_f,transport_f,transport_f],
                            decom             =[transport_f,transport_f,transport_f], 
                            placementNnodes   = 100,
                            decomNnodes       = 100,
                            replacementNnodes = 10)

node_Cost   = Node_BoM(     casing            =[10    ,    0 , 0], #ABS , IP rated
                            connectivtiy      =[5.3   ,    0 , 0], #SX1276 : 5.3
                            eol               =[0     ,    0 , 0],
                            memory            =[0     ,    0 , 0],
                            others            =[1.42  ,    0 , 0], #MLCC : 0.05*15 + XTAL32MHz: 0.5 + R: 0.002*15 + D : 0.07*2  
                            pcb               =[1.17  ,    0 , 0], #PCB 60cm2 : 1.75 
                            power_supply      =[0.228 ,    0 , 0], #XC6206 : 0.228 + Diode and Transistor?
                            processing        =[3.65  ,    0 , 0], #Apollo3: 3.65
                            sensing           =[6.94  ,    0 , 0], #BME680 : 6.94
                            ui                =[0.54  ,    0 , 0], #Push button : 0.17*2 + LED SMD : 0.2*1
                            transport         =[transport_c,0 , 0],
                            battery           =[Batt_cost  ,0 , 0],
                            placement         =[transport_c,0 , 0],
                            replacement       =[transport_c,0 , 0],
                            decom             =[transport_c,0 , 0],
                            placementNnodes   = 100,
                            decomNnodes       = 100,
                            replacementNnodes = 10)

 
# %%
if __name__ == '__main__':
    
    node_LDO = LDO(name = "Node LDO", v_out = 3.3, i_q = 1e-3, v_in = 4.5, module_list = module_List_3V3)
    node_Batt= Battery(name = "Node Battery", v = 4.5, capacity_mAh = 2800, i = 0, selfdischarge_p_year = 5)

    node = LoRa_node(module_list = module_List_3V3,  PMU_composition =[node_LDO], Battery = node_Batt, 
                    MCU_module   = apollo_module_3V3, MCU_active_state = apollo_state_active_3V3,
                    radio_module = radio_module_3V3,  radio_state_TX=radio_state_TX_3V3, radio_state_RX= radio_state_RX_3V3, Ptx = 2)

    PTX_config = PTX_PABOOST_3V3
    ITX_config = I_PABoost_3V3
    Ptx_used = 17

    node.set_radio_parameters(SF=12 ,Coding=1,Header=True,DE = None,BW = 125e3, Payload = 50) 
    node.set_TX_Power_config( P_TX= PTX_config, I_TX=ITX_config)  
    node.set_TX_Power(Ptx = Ptx_used)
    #node.task_rx.task_rate= 24*3
    #node.change_RX_duration(0.5)
    node.task_tx.task_rate= 24

    task_TPHG_3V3.task_rate = 24*12
    task_TPH_3V3.task_rate = 24*12
    node.add_task(task_TPHG_3V3)
    

    def PL_model(d):
        return (plLib.path_loss_Model(d=d,f = 8.68e8, model = "Callebaut"))[0]
        #return (plLib.path_loss_Model(d=d,f = 8.68e8, model = "PLE", arg=[3]))[0]

    def F_trans(km):
        return transport_footprint(km_one_way = km, type ="Unit", 
                                weight_g = 500,  footprint_p_tkm = 0.545,
                                unit_factor = 1,footprint_p_km = 0.350,km_fixed = 5)
    
    def C_trans(km):
        return transport_cost(  worker = 1, salary_p_hour = 5, work_hour =10/60, km_p_h = 50,km_one_way = km, 
                                type ="Unit", 
                                weight_g = 500, cost_p_tkm =  0.2/1e3,
                                unit_factor = 1,cost_p_km = 0.2)

    n_years = 30                                #case study period
    km_trans = 40
    r_type  = "Complete"                        #Replacement type
    node.Battery.selfdischarge_p_year = 5       #Battery self discharge rate per year    
    #node_footprint.set_transport(10,F_trans)    #Set transport footprint based on F_trans 
    figsize = (6,3.8) #figsize = (5,4)

    #deployment_sweep_dnode(Both_Repl = False, Footprint=node_footprint,Node=node,Nyears=n_years,fdata=24,rsd=5   ,dtrans=10,nAA = [1,2]  , param = [1,24,24*12]     , paramType ="fdata"   ,dmin=3000,dmax=12000,d_step=10 ,Task_tx = node.task_tx,PL_model=PL_model,transport_model=F_trans, PTX=PTX_config, I_PTX=ITX_config,filename = os.path.join(path_to_save_svg , "Footprint_dnode")            ,figsize =figsize )
    #deployment_sweep_fdata(Both_Repl = True, Footprint=node_Cost     ,Node=node,Nyears=n_years,d=12000 ,rsd=5   ,dtrans=10,nAA = [1,2]  , param = [5000,9000,12000]   , paramType ="dnode",fmax=24*12+50, f_step=2         ,Task_tx = node.task_tx,PL_model=PL_model,transport_model=C_trans, PTX=PTX_config, I_PTX=ITX_config,filename = None            ,figsize =figsize )
    #deployment_sweep_fdata(Both_Repl = True, Footprint=node_footprint     ,Node=node,Nyears=n_years,d=12000 ,rsd=5   ,dtrans=10,nAA = [1,2]  , param = [0]   , paramType =None,fmax=24*12+50, f_step=2         ,Task_tx = node.task_tx,PL_model=PL_model,transport_model=C_trans, PTX=PTX_config, I_PTX=ITX_config,filename = None           ,figsize =figsize )
    #deployment_sweep_rsd  (Both_Repl = False, Footprint=node_footprint,Node=node,Nyears=n_years,d=12000 ,fdata=24,dtrans=10,nAA = [1,2]  , param = [1,24,24*12]  , paramType ="fdata",rsdmin=1,rsdmax=12,rsd_step=0.2      ,Task_tx = node.task_tx,PL_model=PL_model,transport_model=F_trans, PTX=PTX_config, I_PTX=ITX_config,filename = os.path.join(path_to_save_svg , "Footprint_rsd")            ,figsize =figsize )
    #deployment_sweep_dtrans(Both_Repl = False, Footprint=node_footprint,Node=node,Nyears=n_years,d=800 ,fdata=24, rsd=3,nAA = [1,5], param = [0], paramType =None, dmin =1,dmax=100, d_step=1                              , Task_tx = node.task_tx,PL_model=PL_model,transport_model=F_trans, PTX=PTX_config, I_PTX=ITX_config,filename = os.path.join(path_to_save_svg , "Footprint_dtrans")            ,figsize =figsize )
    #deployment_sweep_dtrans(Both_Repl = True, Footprint=node_Cost     ,Node=node,Nyears=n_years,d=12000 ,fdata=24, rsd=5,nAA = [1,2], param = [0], paramType =None, dmin =1,dmax=100, d_step=1                              , Task_tx = node.task_tx,PL_model=PL_model,transport_model=C_trans, PTX=PTX_config, I_PTX=ITX_config,filename = os.path.join(path_to_save_svg , "Footprint_dtrans")            ,figsize =figsize )
    deployment_ebatt_HP_LP(Tasks_to_swap = [task_TPHG_3V3,task_TPH_3V3],Footprint=node_footprint,Node=node,Nyears=n_years,d=700 ,fdata=24,dtrans=km_trans,rsd = 3, param = [0,3,10]  , paramType ="rsd",nAAmin = 1, nAAmax=7, nAA_step=0.1        ,Task_tx = node.task_tx,PL_model=PL_model,transport_model=F_trans, PTX=PTX_config, I_PTX=ITX_config,filename = os.path.join(path_to_save_svg , "Footprint_Ebattery_HP_LP")            ,figsize =figsize ) 
    deployment_sweep_fdata(Both_Repl = False, Footprint=node_footprint,Node=node,Nyears=n_years,d=700 ,rsd=3   ,dtrans=km_trans,nAA = [1,4]  , param = [200,700,1200]   , paramType ="dnode",fmax=24*12+50, f_step=2         ,Task_tx = node.task_tx,PL_model=PL_model,transport_model=F_trans, PTX=PTX_config, I_PTX=ITX_config,filename = os.path.join(path_to_save_svg , "Footprint_fdata")            ,figsize =figsize )
    deployment_sweep_ebatt(Both_Repl = True, Footprint=node_footprint,Node=node,Nyears=n_years,d=700 ,fdata=24,dtrans=km_trans,rsd = [3], param = [5,40,100]  , paramType ="dtrans",nAAmin = 1, nAAmax=7, nAA_step=0.1        ,Task_tx = node.task_tx,PL_model=PL_model,transport_model=F_trans, PTX=PTX_config, I_PTX=ITX_config,filename = os.path.join(path_to_save_svg , "Footprint_Ebattery_dtrans")            ,figsize =figsize )
    
    #deployment_sweep_ebatt(Both_Repl = True, Footprint=node_Cost     ,Node=node,Nyears=n_years,d=8000 ,fdata=24,dtrans=10,rsd = [3,5], param = [24,24*12]  , paramType ="fdata",nAAmin = 1, nAAmax=5, nAA_step=1        ,Task_tx = node.task_tx,PL_model=PL_model,transport_model=C_trans, PTX=PTX_config, I_PTX=ITX_config,filename = os.path.join(path_to_save_svg , "Footprint_Ebattery")            ,figsize =figsize )
    
    #E_F_comp_dtrans (Both_Repl = True,Footprint=node_footprint,Cost=node_Cost,Node=node,Nyears=n_years,d=12000 ,fdata=24 ,rsd=5,nAA=1   , param = [0], paramType =None, dmin =1  ,dmax=50  , d_step=1  ,Task_tx = node.task_tx,PL_model=PL_model,trans_F_model=F_trans,trans_C_model=C_trans, PTX=PTX_config, I_PTX=ITX_config,filename = os.path.join(path_to_save_svg , "E_F_comp_Dtrans")         ,figsize =figsize )  
    #E_F_comp_fdata  (Both_Repl = True,Footprint=node_footprint,Cost=node_Cost,Node=node,Nyears=n_years,d=12000 ,dtrans=10,rsd=5,nAA=1   , param = [0], paramType =None, fmin =1  ,fmax=1000, f_step=2  ,Task_tx = node.task_tx,PL_model=PL_model,trans_F_model=F_trans,trans_C_model=C_trans, PTX=PTX_config, I_PTX=ITX_config,filename = os.path.join(path_to_save_svg , "E_F_comp_Fdata")          ,figsize =figsize ) 
    #E_F_comp_ebatt  (Both_Repl = True,Footprint=node_footprint,Cost=node_Cost,Node=node,Nyears=n_years,d=12000 ,dtrans=10,rsd=5,fdata=24, param = [0], paramType =None, nAAmin =1,nAAmax=5, nAA_step=0.1,Task_tx = node.task_tx,PL_model=PL_model,trans_F_model=F_trans,trans_C_model=F_trans, PTX=PTX_config, I_PTX=ITX_config,filename = os.path.join(path_to_save_svg , "E_F_comp_Ebatt")          ,figsize =figsize ) 
    
    #figsize = (6,3.8)
    #node_footprint.plot_footprint(filename = os.path.join(path_to_save_svg , "Node_Footprint_breakdown") ,figsize =figsize)
    plt.show()
    # %%