
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

from Impact_model.Node_BoM  import *
from Impact_model.Transport import *




def deployment_battery_replacement( Replacement_type = "Complete",Footprint=None,Node=None,Nyears= 100):
    Node.compute()
    [power,lifetime] = [Node.average_power,Node.lifetime] 
    Footprint.recompute()
    Placement_cost   = Footprint.F_prod[0] + Footprint.placement + Footprint.battery[0]
    Decom_cost       = Footprint.decom
    Replacement_cost = 0
    if Replacement_type == "Complete" : 
        Replacement_cost = Footprint.F_prod[0] + Footprint.replacement + Footprint.battery[0]
    elif Replacement_type == "Battery" : 
        Replacement_cost = Footprint.replacement + Footprint.battery[0]
    else:
        print("No replacement type found")
    Deployment_footprint   = Placement_cost + Decom_cost

    
    Tot_Deployment_footprint = Placement_cost + Replacement_cost * np.floor((Nyears/lifetime)) + Decom_cost
    Tot_Deployment_footprint = Tot_Deployment_footprint
    return [Deployment_footprint,Tot_Deployment_footprint,lifetime,power]




    

def plot_service_footprint(filename = None,figsize=(7,6), separatePlot=False,Footprint=None,Node=None,Nyears= 100):
    Footprint.recompute()
    [Deployment_footprint,Tot_Deployment_footprint,lifetime,power] = deployment_battery_replacement(Replacement_type ="Battery",Footprint=Footprint,Node=Node,Nyears= Nyears)
    barWidth = 0.6
    carolina_blue = dictColor["CarolinaBlue"]

    NReplacement = int(np.floor(Nyears/lifetime))
    transport_fix = Footprint.placement+Footprint.decom
    transport_maint = NReplacement * Footprint.replacement
    
    height      = np.array([Footprint.casing[0],Footprint.connectivtiy[0], Footprint.eol[0],Footprint.memory[0],Footprint.others[0],Footprint.pcb[0],Footprint.power_supply[0],Footprint.processing[0],Footprint.sensing[0],Footprint.ui[0] ,transport_fix      , transport_maint      ,Footprint.battery[0]* NReplacement,Tot_Deployment_footprint ] )
    height_e_up = np.array([Footprint.casing[2],Footprint.connectivtiy[2], Footprint.eol[2],Footprint.memory[2],Footprint.others[2],Footprint.pcb[2],Footprint.power_supply[2],Footprint.processing[2],Footprint.sensing[2],Footprint.ui[2] ,transport_fix      , transport_maint      ,Footprint.battery[2]* NReplacement,Tot_Deployment_footprint ] )
    height_e_do = np.array([Footprint.casing[1],Footprint.connectivtiy[1], Footprint.eol[1],Footprint.memory[1],Footprint.others[1],Footprint.pcb[1],Footprint.power_supply[1],Footprint.processing[1],Footprint.sensing[1],Footprint.ui[1] ,transport_fix      , transport_maint      ,Footprint.battery[1]* NReplacement,Tot_Deployment_footprint ] )
    height_n    = np.array([0                  ,0                        , 0               ,0                  ,0                  ,0               ,0                        ,0                      ,0                   ,0               ,0                  , 0                    ,0                                 ,Footprint.battery[0]* NReplacement])
    xlabel      = np.array(["Casing"           ,"Connectivity"           ,"EoL"            ,"Memory"           ,"Others"           ,"PCB"           ,"PMU"                    ,"Processing"           ,"Sensing"           ,"User Interface","Transport (P&D)"  , "Transport (Maint)"  , "Battery module"                 , "Total"])
    color       = np.array([carolina_blue      ,carolina_blue            ,carolina_blue    ,carolina_blue      ,carolina_blue      ,carolina_blue   ,carolina_blue            ,carolina_blue          ,carolina_blue       ,carolina_blue   ,dictColor["Green"] , dictColor["Green"]   , dictColor["Sandy"]               , carolina_blue ])         
    toRemove    = [i for i in np.arange(len(height)) if height[i]==0]
    for index in toRemove[::-1]:
        height      = np.delete(height,         index)
        height_e_up = np.delete(height_e_up,    index)
        height_e_do = np.delete(height_e_do,    index)
        height_n    = np.delete(height_n,       index)
        color       = np.delete(color,          index)
        xlabel      = np.delete(xlabel,         index)

    index       = np.append(np.argsort([height[:-1]]),len(height)-1)
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
        toDisplay = (100*rect_height/Footprint.F_node[0])
        plt.text(rect.get_x() + rect.get_width()/2, rect_height, f'{toDisplay:.1f}%',fontsize = 13, ha='right', va='bottom')
    plt.text(rect.get_x() + rect.get_width()*1.1, height[-2], f'{(100*Footprint.F_prod[0]/Footprint.F_node[0]):.1f}%',fontsize = 13, ha='left', va='bottom',rotation = -90)
    plt.text(rect.get_x() + rect.get_width()*1.1, Footprint.battery[0]/2, f'{(100*Footprint.battery[0]/Footprint.F_node[0]):.1f}%',fontsize = 13, ha='left', va='center',rotation = -90)
    print(Footprint.F_node[0])

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
