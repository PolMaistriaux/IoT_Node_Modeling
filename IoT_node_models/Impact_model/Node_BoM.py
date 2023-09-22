

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

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from MyColors           import *


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

    def plot_footprint(self,filename = None,figsize=(7,6), separatePlot=False):
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

        if separatePlot:
            ax_y_fig_span = np.max(height_e_up[:-1])*1.3
        else:
            ax_y_fig_span = np.max(height_e_up)*1.3
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
        if separatePlot:
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