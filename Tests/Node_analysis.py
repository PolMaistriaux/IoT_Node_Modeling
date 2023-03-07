#%%
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
from IoT_node_models.Wireless_communication import *
from IoT_node_models.Hardware_Modules import *
from IoT_node_models.Node_examples import *

import IoT_node_models

path_to_save_svg = "SavedFiles"

####################################################

def node_power(Node, d= 10 ,PL_model=None, PTX=[] , I_PTX=[], doPlot = False, verbose = False):

    PL = PL_model(d)    
    [opt_SF,opt_PTX,dummy] = find_Opti_SF_PTX(PTX_possible = PTX, PL = PL , I_PTX=I_PTX,verbose=True)
    if opt_SF == 0:
        print("Out of range for d = %.2f"%(d))
        return [0,0]
    Node.SF =opt_SF
    Node.set_radio_parameters(SF=opt_SF)
    Node.set_TX_Power(Ptx = opt_PTX) 
    Node.recompute()
    if verbose:
        Node.print_Tasks()
        Node.print_Modules()
        print("Radio parameter : SF = %d and PTx = %.1f dBm"%(opt_SF,opt_PTX))
    if doPlot:
        Node.plot_Power()
    return [Node.average_power,Node.lifetime]

def sweep_dnode(Node, dmax, d_step ,nAA = [], PL_model=None, PTX=[] , I_PTX=[], doPlot = False,filename =None,figsize=(7,6)):  

    capa_1AA = Node.Battery.capacity_mAh

    d= np.arange(10,dmax,d_step)
    result = np.zeros((3,len(nAA),len(d)))

    SF = 0
    Ptx = 0
    SF_change = []
    Ptx_change = []
    i = 0
    for indexAA, AA in  enumerate(nAA):
        for index,dist in enumerate(d):
            Node.Battery.capacity_mAh = capa_1AA*AA
            result[0,indexAA,index] = dist
            result[1:,indexAA,index]=node_power(Node=Node, d= dist ,PL_model=PL_model, PTX=PTX , I_PTX=I_PTX, doPlot = False)
            if i ==0 :
                if Node.SF != SF :
                    SF = Node.SF
                    SF_change = SF_change + [dist]   
                if Node.Ptx != Ptx:
                    Ptx = Node.Ptx
                    Ptx_change = Ptx_change + [dist] 
        i=1


    Node.Battery.capacity_mAh = capa_1AA

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
    ax.set_title("Dnode and Ebatt : self-discharge rate = %.1f %%"%(Node.Battery.selfdischarge_p_year))

    #ax2.vlines(np.array(SF_change) /1000,ymin = ax2_ylim*0.1, ymax = ax2_ylim    , color = "red" ,  linestyle = "dashed")
    #ax2.vlines(np.array(Ptx_change)/1000,ymin = 0           , ymax = ax2_ylim*0.9, color = "black", linestyle = "dashed")
    if(filename != None):
        to_save= filename+".svg"
        plt.savefig(to_save, format="svg")  
    
####################################################
def sweep_fdata(Node, fmax, f_step, Task_tx = None,nAA=[],d = 1000,PL_model=None, PTX=[] , I_PTX=[], doPlot = False,filename =None,figsize=(7,6)):   

    if Task_tx == None :
        print("No task tx specified")
        return
    capa_1AA = Node.Battery.capacity_mAh
    f_initial = Task_tx.task_rate
    fdata= np.arange(1,fmax,f_step)
    result = np.zeros((4,len(nAA),len(fdata)))

    for indexAA, AA in  enumerate(nAA):
        for index,f in enumerate(fdata):
            result[0,indexAA,index] = f
            Node.Battery.capacity_mAh = capa_1AA*AA
            Task_tx.task_rate= f
            [av_power,lifetime]=node_power(Node=Node, d= d ,PL_model=PL_model, PTX=PTX , I_PTX=I_PTX, doPlot = False)
            result[1:3,indexAA,index]= [av_power,lifetime]
            result[3,indexAA,index]=Node.Battery.capacity_mAh/(24*365*Node.Battery.i)

    Node.Battery.capacity_mAh = capa_1AA
    Task_tx.task_rate= f_initial

    fig,ax = plt.subplots(1,1)
    ax.set_xlabel("Transmission rate [$msg/day$]")
    
    ax.set_ylabel("Node lifetime [$years$]")
    for  indexAA, AA in enumerate(nAA):
        ax.plot(result[0,indexAA,:],
                result[2,indexAA,:],
                color=dictColor["Green"])
                #marker="o",markersize=2)
        ax.plot(result[0,indexAA,:],
            result[3,indexAA,:],
            color=dictColor["DeepBlue"],
            linestyle="dashed")
                            

    ax2=ax.twinx()
    ax2.plot(result[0,0,:],
            result[1,0,:]*1000,
            color=dictColor["CarolinaBlue"])
            #marker="o",markersize=2)

    ax2.set_ylabel("Average power [$\mu W$]")

    ax.set_ylim(ymin= 0,  ymax =np.max(result[2,:,:])*1.1 )
    ax2.set_ylim(ymin= 0, ymax =np.max(result[1,:,:])*1100 )

    ax.set_title("Fdata and Ebatt : self-discharge rate = %.1f %% \n dnode = %.1f m"%(Node.Battery.selfdischarge_p_year,d))

    if(filename != None):
        to_save= filename+".svg"
        plt.savefig(to_save, format="svg")  

####################################################
def sweep_ebatt(Node, nAAmax,d = 1000,PL_model=None, PTX=[] , I_PTX=[], doPlot = False,filename =None,figsize=(7,6)):   

    capa_1AA = Node.Battery.capacity_mAh
    nAA= np.arange(1,nAAmax,1)
    result = np.zeros((3,len(nAA)))
    for index,AA in enumerate(nAA):
        result[0,index] = capa_1AA*AA
        Node.Battery.capacity_mAh = capa_1AA*AA
        result[1:,index]=node_power(Node=Node, d= d ,PL_model=PL_model, PTX=PTX , I_PTX=I_PTX, doPlot = False,verbose = True)
    
    fig,ax = plt.subplots(1,1)
    ax.set_xlabel("Battery capacity [mAh]", fontsize = 14)
    
    ax.set_ylabel("Node lifetime [y.]", color="red", fontsize=14)
    ax.plot(result[0,:],
            result[2,:],
            color="red",
            marker="o",markersize=4)

    ax2=ax.twinx()
    ax2.plot(result[0,:],
            result[1,:]*1000,
            color="blue")
            #marker="o",markersize=2)
    ax2.set_ylabel("Average power [uW]",color="blue",fontsize=14)
    if(filename != None):
        to_save= filename+".svg"
        plt.savefig(to_save, format="svg")  

####################################################
def sweep_dnode_fdata_Ebatt(Node,dmin, dmax, d_step ,f_batt = 24, fdata = [],nAA=[], Task_tx = None, PL_model=None, PTX=[] , I_PTX=[],filename =None,figsize=(7,6)):  

    f_initial = Task_tx.task_rate
    capa_1AA = Node.Battery.capacity_mAh

    d= np.arange(dmin,dmax+d_step,d_step)
    result_fdata = np.zeros((3,len(fdata),len(d)))

    SF = 0
    Ptx = 0
    SF_change = []
    Ptx_change = []
    i = 0
    for indexf, f in  enumerate(fdata):
        Task_tx.task_rate = f
        for index,dist in enumerate(d):
            result_fdata[0,indexf,index] = dist
            result_fdata[1:,indexf,index]=node_power(Node=Node, d= dist ,PL_model=PL_model, PTX=PTX , I_PTX=I_PTX, doPlot = False)
            if i ==0 :
                if Node.SF != SF :
                    SF = Node.SF
                    SF_change = SF_change + [dist]   
                if Node.Ptx != Ptx:
                    Ptx = Node.Ptx
                    Ptx_change = Ptx_change + [dist] 
        i=1

    Task_tx.task_rate = f_batt 

    result_nAA  = np.zeros((4,len(nAA),len(d)))
    for indexAA, AA in  enumerate(nAA):
        Node.Battery.capacity_mAh = capa_1AA*AA
        for index,dist in enumerate(d):
            result_nAA[0,indexAA,index] = dist
            [av_power,lifetime]=node_power(Node=Node, d= dist ,PL_model=PL_model, PTX=PTX , I_PTX=I_PTX, doPlot = False)
            result_nAA[1:3,indexAA,index]= [av_power,lifetime]
            result_nAA[3,indexAA,index]=Node.Battery.capacity_mAh/(24*365*Node.Battery.i)

    Task_tx.task_rate = f_initial 
    Node.Battery.capacity_mAh = capa_1AA

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
    fig.suptitle("dnode for fdata and ebatt : self-discharge rate = %.1f %%"%(Node.Battery.selfdischarge_p_year))

    #ax.vlines(np.array(SF_change) /1000,ymin = ax2_ylim*0.1, ymax = ax2_ylim    , color = "red" ,  linestyle = "dashed")
    #ax.vlines(np.array(Ptx_change)/1000,ymin = 0           , ymax = ax2_ylim*0.9, color = "black", linestyle = "dashed")
    if(filename != None):
        to_save= filename+".svg"
        plt.savefig(to_save, format="svg")  

####################################################
def sweep_dnode_fdata(Node, dmax, d_step ,fdata = [], Task_tx = None, PL_model=None, PTX=[] , I_PTX=[],filename =None,figsize=(7,6)):  

    d= np.arange(10,dmax,d_step)
    result = np.zeros((3,len(fdata),len(d)))
    f_initial = Task_tx.task_rate

    SF = 0
    Ptx = 0
    SF_change = []
    Ptx_change = []
    i = 0
    for indexf, f in  enumerate(fdata):
        Task_tx.task_rate = f
        for index,dist in enumerate(d):
            result[0,indexf,index] = dist
            result[1:,indexf,index]=node_power(Node=Node, d= dist ,PL_model=PL_model, PTX=PTX , I_PTX=I_PTX, doPlot = False)
            if i ==0 :
                if Node.SF != SF :
                    SF = Node.SF
                    SF_change = SF_change + [dist]   
                if Node.Ptx != Ptx:
                    Ptx = Node.Ptx
                    Ptx_change = Ptx_change + [dist] 
        i=1

    Task_tx.task_rate = f_initial 

    fig,ax = plt.subplots(1,1,figsize=figsize)
    ax.set_xlabel("Distance [$km$]", fontsize = 14)
    
    ax.set_ylabel("Average power [$\mu W$]")
    for  indexf, f in enumerate(fdata):
        ax.plot(result[0,indexf,:]/1000,
                result[1,indexf,:],
                color=dictColor["Green"])

    '''ax2=ax.twinx()
    tck = scipy.interpolate.splrep(d, y=result[1,0,:], s=10)
    ax2.plot(result[0,0,:]/1000,
            result[1,0,:]*1000,
            color=dictColor["CarolinaBlue"],label ="Optimal Strategy")
    ax2.plot(result[0,0,:]/1000,
            scipy.interpolate.splev(d, tck, der=0)*1000,
            color=dictColor["DeepBlue"],label ="Interpolated",linestyle="dashed")'''

    #ax_ylim = np.max(result[1,:,:])*1100 
    #ax.set_ylim( ymin= 0, ymax =ax_ylim )
    #ax.legend()
    ax.set_title("Dnode and fdata : self-discharge rate = %.1f %%"%(Node.Battery.selfdischarge_p_year))

    #ax.vlines(np.array(SF_change) /1000,ymin = ax2_ylim*0.1, ymax = ax2_ylim    , color = "red" ,  linestyle = "dashed")
    #ax.vlines(np.array(Ptx_change)/1000,ymin = 0           , ymax = ax2_ylim*0.9, color = "black", linestyle = "dashed")
    if(filename != None):
        to_save= filename+".svg"
        plt.savefig(to_save, format="svg")  
# %%
if __name__ == '__main__':
    
    node_LDO = LDO(name = "Node LDO", v_out = 3.3, i_q = 1e-3, v_in = 3, module_list = module_List_3V3)
    node_Batt= Battery(name = "Node Battery", v = 3, capacity_mAh = 1800, i = 0, selfdischarge_p_year = 5)

    node = LoRa_node(module_list = module_List_3V3,  PMU_composition =[node_LDO], Battery = node_Batt, 
                    MCU_module   = apollo_module_3V3, MCU_active_state = apollo_state_active_3V3,
                    radio_module = radio_module_3V3,  radio_state_TX=radio_state_TX_3V3, radio_state_RX= radio_state_RX_3V3, Ptx = 2)
        
    node.set_radio_parameters(SF=7 ,Coding=1,Header=True,DE = None,BW = 125e3, Payload = 50) 
    node.set_TX_Power_config( P_TX= PTX_PABOOST_configured, I_TX=I_PABoost_3V3)  
    node.set_TX_Power(Ptx = 17)
    node.task_rx.task_rate= 0
    #node.change_RX_duration(0.5)
    node.task_tx.task_rate= 24
    task_TPHG_3V3.task_rate = 24*12

    #task_TPH_3V3.task_rate = 24*12
    node.add_task(task_TPHG_3V3)
    #node.add_task(task_TPH_3V3)

    def PL_model(d):
        return logPL.path_loss_PLd0(d=d, PLd0=94.40,d0=1, n=2.03)

    figsize = (6,5)
    node_power(Node=node, d= 1500 ,PL_model=PL_model, PTX=PTX_PABOOST_configured , I_PTX=I_PABoost_3V3, doPlot = True,verbose=True)
    #sweep_dnode(Node=node, dmax=1500, d_step=3 ,nAA = [1,3,5],PL_model=PL_model, PTX=PTX_PABOOST_3V3 , I_PTX=I_PABoost_3V3,filename =os.path.join(path_to_save_svg , "Lifetime_dnode_Ebatt"),figsize=figsize)
    #sweep_dnode(Node=node, dmax=10000, d_step=100 ,nAA = [1,3,5],PL_model=PL_model, PTX=PTX_PABOOST_configured[:15] , I_PTX=I_PABoost_3V3[:15] ,filename =os.path.join(path_to_save_svg , "Lifetime_dnode_Ebatt2"),figsize=figsize)
    #sweep_dnode_fdata(Node=node, dmax=10000, d_step=100,fdata = [24,24+3*24,24+6*24], Task_tx = node.task_tx,PL_model=PL_model, PTX=PTX_PABOOST_configured[:15] , I_PTX=I_PABoost_3V3[:15] ,filename =os.path.join(path_to_save_svg , "Lifetime_dnode_fdata"),figsize=figsize)
    #sweep_fdata(Node=node, fmax=24*10, f_step=1, Task_tx = node.task_tx,d = 8000,nAA = [1,3,5],PL_model=PL_model, PTX=PTX_PABOOST_3V3 , I_PTX=I_PABoost_3V3,filename =os.path.join(path_to_save_svg , "Lifetime_fdata_Ebatt"),figsize=figsize) 
    #sweep_ebatt(Node=node, nAAmax = 8,d = 8000,PL_model=PL_model, PTX=PTX_PABOOST_3V3 , I_PTX=I_PABoost_3V3)
    #figsize = (6,6)
    sweep_dnode_fdata_Ebatt(Node=node,dmin = 200, dmax=1500, d_step=2,f_batt = 24,fdata = [1,24, 24*4],nAA = [1,2], Task_tx = node.task_tx, PL_model=PL_model, PTX=PTX_PABOOST_3V3 , I_PTX=I_PABoost_3V3,filename =os.path.join(path_to_save_svg , "Lifetime_fdata_Ebatt_dnode"),figsize=figsize) 
    #sweep_dnode_fdata_Ebatt(Node=node,dmin = 3000, dmax=13000, d_step=100,f_batt = 24*7,fdata = [4,86,168],nAA = [1,2], Task_tx = node.task_tx, PL_model=PL_model, PTX=PTX_PABOOST_3V3 , I_PTX=I_PABoost_3V3,filename =os.path.join(path_to_save_svg , "Lifetime_fdata_Ebatt_dnode"),figsize=figsize) 

    plt.show()
# %%
