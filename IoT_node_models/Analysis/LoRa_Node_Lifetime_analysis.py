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



def sweep_dnode(Node, dmax, d_step ,nAA = [], Task_tx = None, PL_model=None, doPlot = False,filename =None,figsize=(7,6)):  

    capa_1AA = Node.get_Node().get_Battery().get_capacity_mAh()

    d_initial = Task_tx.get_distance()
    d= np.arange(10,dmax,d_step)
    result = np.zeros((3,len(nAA),len(d)))

    SF = 0
    Ptx = 0
    SF_change = []
    Ptx_change = []
    i = 0
    for indexAA, AA in  enumerate(nAA):
        for index,dist in enumerate(d):
            Node.get_Node().get_Battery().set_capacity_mAh( capa_1AA*AA )
            result[0,indexAA,index] = dist
            Task_tx.set_distance(dist)
            Node.compute()
            result[1:,indexAA,index]= [Node.average_power,Node.lifetime] 
            if i ==0 :
                if Task_tx.SF != SF :
                    SF = Task_tx.SF
                    SF_change = SF_change + [dist]   
                if Task_tx.Ptx != Ptx:
                    Ptx = Task_tx.Ptx
                    Ptx_change = Ptx_change + [dist] 
        i=1


    Node.get_Node().get_Battery().set_capacity_mAh( capa_1AA ) 
    Task_tx.set_distance(d_initial)

    fig,ax = plt.subplots(1,1,figsize=figsize)
    ax.set_xlabel("Distance [$km$]", fontsize = 14)
    
    ax.set_ylabel("Lifetime [$years$]")
    for  indexAA, AA in enumerate(nAA):
        ax.plot(result[0,indexAA,:]/1000,
                result[2,indexAA,:],
                color=dictColor["Green"])

    ax2=ax.twinx()
    tck = scipy.interpolate.splrep(d, y=result[1,0,:], s=10)
    ax2.plot(result[0,0,:]/1000,
            result[1,0,:]*1000,
            color=dictColor["CarolinaBlue"],label ="Optimal Strategy")
    ax2.plot(result[0,0,:]/1000,
            scipy.interpolate.splev(d, tck, der=0)*1000,
            color=dictColor["DeepBlue"],label ="Interpolated",linestyle="dashed")
    ax2.set_ylabel("Average power [$\mu W$]")

    ax_ylim  = np.max(result[2,:,:])*1.1
    ax2_ylim = np.max(result[1,:,:])*1100 
    ax.set_ylim( ymin= 0, ymax =ax_ylim )
    ax2.set_ylim(ymin= 0, ymax =ax2_ylim)
    ax2.legend()
    ax.set_title("Dnode and Ebatt : self-discharge rate = %.1f %%"%(Node.get_Node().get_Battery().get_selfdischarge_p_year()))

    #ax2.vlines(np.array(SF_change) /1000,ymin = ax2_ylim*0.1, ymax = ax2_ylim    , color = "red" ,  linestyle = "dashed")
    #ax2.vlines(np.array(Ptx_change)/1000,ymin = 0           , ymax = ax2_ylim*0.9, color = "black", linestyle = "dashed")
    if(filename != None):
        to_save= filename+".svg"
        plt.savefig(to_save, format="svg")  

####################################################################################################################################

def sweep_fdata(Node, fmax, f_step, Task_tx = None,nAA=[],d = 1000, doPlot = False,filename =None,figsize=(7,6)):   

    if Task_tx == None :
        print("No task tx specified")
        return
    capa_1AA = Node.get_Node().get_Battery().get_capacity_mAh()
    f_initial = Node.get_task_rate(Task_tx)
    fdata= np.arange(1,fmax,f_step)
    result = np.zeros((4,len(nAA),len(fdata)))

    for indexAA, AA in  enumerate(nAA):
        for index,f in enumerate(fdata):
            result[0,indexAA,index] = f
            Node.get_Node().get_Battery().set_capacity_mAh( capa_1AA*AA )
            Node.change_task_rate(Task_tx,f)
            Node.compute()
            result[1:3,indexAA,index]= [Node.average_power,Node.lifetime] 
            result[3,indexAA,index]=(Node.get_Node().get_Battery().get_capacity_mAh())/(24*365*(Node.get_Node().get_Battery().get_i()))

    Node.get_Node().get_Battery().set_capacity_mAh( capa_1AA )
    Node.change_task_rate(Task_tx,f_initial)

    fig,ax = plt.subplots(1,1)
    ax.set_xlabel("Transmission rate [$msg/day$]")
    
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

    ax.set_title("Fdata and Ebatt : self-discharge rate = %.1f %% \n dnode = %.1f m"%(Node.get_Node().get_Battery().get_selfdischarge_p_year(),d))

    if(filename != None):
        to_save= filename+".svg"
        plt.savefig(to_save, format="svg")

####################################################################################################################################
        

def sweep_dnode_fdata_Ebatt(Node,dmin, dmax, d_step ,f_batt = 24, fdata = [],nAA=[], Task_tx = None, PL_model=None ,filename =None,figsize=(7,6)):  

    f_initial = Node.get_task_rate(Task_tx)
    d_initial = Task_tx.get_distance()
    capa_1AA = Node.get_Node().get_Battery().get_capacity_mAh()

    d= np.arange(dmin,dmax+d_step,d_step)
    result_fdata = np.zeros((3,len(fdata),len(d)))

    SF = 0
    Ptx = 0
    SF_change = []
    Ptx_change = []
    i = 0
    for indexf, f in  enumerate(fdata):
        Task_tx.task_rate = f
        Node.change_task_rate(Task_tx,f)
        for index,dist in enumerate(d):
            result_fdata[0,indexf,index] = dist
            Task_tx.set_distance(dist)
            Node.compute()
            result_fdata[1:,indexf,index]=[Node.average_power,Node.lifetime] 
            if i ==0 :
                if Task_tx.SF != SF :
                    SF = Task_tx.SF
                    SF_change = SF_change + [dist]   
                if Task_tx.Ptx != Ptx:
                    Ptx = Task_tx.Ptx
                    Ptx_change = Ptx_change + [dist] 
        i=1

    #Task_tx.task_rate = f_batt 
    Node.change_task_rate(Task_tx,f_batt)

    result_nAA  = np.zeros((4,len(nAA),len(d)))
    for indexAA, AA in  enumerate(nAA):
        Node.get_Node().get_Battery().set_capacity_mAh( capa_1AA*AA )
        for index,dist in enumerate(d):
            result_nAA[0,indexAA,index] = dist
            Task_tx.set_distance(dist)
            Node.compute()
            result_nAA[1:3,indexAA,index]= [Node.average_power,Node.lifetime] 
            result_nAA[3,indexAA,index]=(Node.get_Node().get_Battery().get_capacity_mAh())/(24*365*(Node.get_Node().get_Battery().get_i()))

    #Task_tx.task_rate = f_initial 
    Node.change_task_rate(Task_tx,f_initial)
    Task_tx.set_distance(d_initial)
    Node.compute()
    Node.get_Node().get_Battery().set_capacity_mAh( capa_1AA )

    fig,ax = plt.subplots(2,1,figsize=figsize)
    ax[1].set_xlabel("Distance [$m$]", fontsize = 14)
    ax[1].set_xlabel("Distance [$m$]", fontsize = 14)
    
    WattFactor = 1

    ax[1].set_ylabel("Node lifetime [$years$]")
    for  indexAA, AA in enumerate(nAA):
        ax[1].step(result_nAA[0,indexAA,:],
                result_nAA[2,indexAA,:],
                color=listGreen[(indexAA+3)])
                #marker="o",markersize=2)
        ax[1].step(result_nAA[0,indexAA,:],
            result_nAA[3,indexAA,:],
            color=listGreen[(indexAA+3)], linestyle = "dashed")

    ax[0].set_ylabel("Average power [$mW$]")
    for indexf, f in  enumerate(fdata):
        ax[0].step(result_fdata[0,indexf,:],
                result_fdata[1,indexf,:]*WattFactor,
                color=listBlue[(indexf)])

    ax2_ylim = np.max(result_fdata[1,:,:])*WattFactor*1.05 
    ax_ylim  = np.max(  result_nAA[3,:,:])*1.1 
    ax[0].set_ylim(  ymin= 0, ymax =ax2_ylim )
    ax[1].set_ylim(  ymin= 0, ymax = ax_ylim )
    #ax.set_xticks(np.arange(0,nAAmax+1,1)*capa_1AA)
    ax[1].set_xlim(xmin = dmin, xmax = dmax )
    ax[0].set_xlim(xmin = dmin, xmax = dmax )
    #ax.legend()
    fig.suptitle("dnode for fdata and ebatt : self-discharge rate = %.1f %%"%(Node.get_Node().get_Battery().get_selfdischarge_p_year()))

    #ax.vlines(np.array(SF_change) /1000,ymin = ax2_ylim*0.1, ymax = ax2_ylim    , color = "red" ,  linestyle = "dashed")
    #ax.vlines(np.array(Ptx_change)/1000,ymin = 0           , ymax = ax2_ylim*0.9, color = "black", linestyle = "dashed")
    if(filename != None):
        to_save= filename+".svg"
        plt.savefig(to_save, format="svg")  