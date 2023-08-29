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

import IoT_node_models
from IoT_node_models.Energy_model                        import *
from IoT_node_models.Energy_model.Wireless_communication import *
from IoT_node_models.Hardware_Modules import *
#from IoT_node_models.Node_examples import *



path_to_save_svg = "SavedFiles"

####################################################

def node_power(Node, d= 10 ,PL_model=None, PTX=[] , I_PTX=[], doPlot = False, verbose = False):

    PL = PL_model(d)    
    [opt_SF,opt_PTX,dummy] = find_Opti_SF_PTX(PTX_possible = PTX, PL = PL , I_PTX=I_PTX,verbose=verbose)
    if opt_SF == 0:
        raise Exception("Error : Out of range for d = %.2f"%(d)) 
        return [0,0]
    Node.SF =opt_SF
    Node.set_radio_parameters(SF=opt_SF)
    Node.set_TX_Power(Ptx = opt_PTX) 
    Node.compute()
    if verbose:
        Node.print_Tasks()
        Node.print_Modules()
        print("Radio parameter : SF = %d and PTx = %.1f dBm"%(opt_SF,opt_PTX))
    if doPlot:
        Node.plot_Power()
    return [Node.average_power,Node.lifetime]



def sweep_dnode(Node, dmax, d_step ,nAA = [], PL_model=None, PTX=[] , I_PTX=[], doPlot = False,filename =None,figsize=(7,6)):  

    capa_1AA = Node.get_Node().get_Battery().get_capacity_mAh()

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
            result[1:,indexAA,index]=node_power(Node=Node, d= dist ,PL_model=PL_model, PTX=PTX , I_PTX=I_PTX, doPlot = False)
            if i ==0 :
                if Node.SF != SF :
                    SF = Node.SF
                    SF_change = SF_change + [dist]   
                if Node.Ptx != Ptx:
                    Ptx = Node.Ptx
                    Ptx_change = Ptx_change + [dist] 
        i=1


    Node.get_Node().get_Battery().set_capacity_mAh( capa_1AA ) 

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
    
####################################################
def sweep_fdata(Node, fmax, f_step, Task_tx = None,nAA=[],d = 1000,PL_model=None, PTX=[] , I_PTX=[], doPlot = False,filename =None,figsize=(7,6)):   

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
            #Task_tx.task_rate= f
            [av_power,lifetime]=node_power(Node=Node, d= d ,PL_model=PL_model, PTX=PTX , I_PTX=I_PTX, doPlot = False)
            result[1:3,indexAA,index]= [av_power,lifetime]
            result[3,indexAA,index]=(Node.get_Node().get_Battery().get_capacity_mAh())/(24*365*(Node.get_Node().get_Battery().get_i()))

    Node.get_Node().get_Battery().set_capacity_mAh( capa_1AA )
    #Task_tx.task_rate= f_initial
    Node.change_task_rate(Task_tx,f_initial)

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

    ax.set_title("Fdata and Ebatt : self-discharge rate = %.1f %% \n dnode = %.1f m"%(Node.get_Node().get_Battery().get_selfdischarge_p_year(),d))

    if(filename != None):
        to_save= filename+".svg"
        plt.savefig(to_save, format="svg")  

####################################################
def sweep_ebatt(Node, nAAmax,d = 1000,PL_model=None, PTX=[] , I_PTX=[], doPlot = False,filename =None,figsize=(7,6)):   

    capa_1AA = Node.get_Node().get_Battery().get_capacity_mAh()
    nAA= np.arange(1,nAAmax,1)
    result = np.zeros((3,len(nAA)))
    for index,AA in enumerate(nAA):
        result[0,index] = capa_1AA*AA
        Node.get_Node().get_Battery().set_capacity_mAh( capa_1AA*AA )
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

    f_initial = Node.get_task_rate(Task_tx)
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
            result_fdata[1:,indexf,index]=node_power(Node=Node, d= dist ,PL_model=PL_model, PTX=PTX , I_PTX=I_PTX, doPlot = False)
            if i ==0 :
                if Node.SF != SF :
                    SF = Node.SF
                    SF_change = SF_change + [dist]   
                if Node.Ptx != Ptx:
                    Ptx = Node.Ptx
                    Ptx_change = Ptx_change + [dist] 
        i=1

    #Task_tx.task_rate = f_batt 
    Node.change_task_rate(Task_tx,f_batt)

    result_nAA  = np.zeros((4,len(nAA),len(d)))
    for indexAA, AA in  enumerate(nAA):
        Node.get_Node().get_Battery().set_capacity_mAh( capa_1AA*AA )
        for index,dist in enumerate(d):
            result_nAA[0,indexAA,index] = dist
            [av_power,lifetime]=node_power(Node=Node, d= dist ,PL_model=PL_model, PTX=PTX , I_PTX=I_PTX, doPlot = False)
            result_nAA[1:3,indexAA,index]= [av_power,lifetime]
            result_nAA[3,indexAA,index]=(Node.get_Node().get_Battery().get_capacity_mAh())/(24*365*(Node.get_Node().get_Battery().get_i()))

    #Task_tx.task_rate = f_initial 
    Node.change_task_rate(Task_tx,f_initial)
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

####################################################
def sweep_dnode_fdata(Node, dmax, d_step ,fdata = [], Task_tx = None, PL_model=None, PTX=[] , I_PTX=[],filename =None,figsize=(7,6)):  

    d= np.arange(10,dmax,d_step)
    result = np.zeros((3,len(fdata),len(d)))
    f_initial = Node.get_task_rate(Task_tx)

    SF = 0
    Ptx = 0
    SF_change = []
    Ptx_change = []
    i = 0
    for indexf, f in  enumerate(fdata):
        Node.change_task_rate(Task_tx,f)
        #Task_tx.task_rate = f
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

    #Task_tx.task_rate = f_initial 
    Node.change_task_rate(Task_tx,f_initial)
    
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
    ax.set_title("Dnode and fdata : self-discharge rate = %.1f %%"%(Node.get_Node().get_Battery().get_selfdischarge_p_year()))

    #ax.vlines(np.array(SF_change) /1000,ymin = ax2_ylim*0.1, ymax = ax2_ylim    , color = "red" ,  linestyle = "dashed")
    #ax.vlines(np.array(Ptx_change)/1000,ymin = 0           , ymax = ax2_ylim*0.9, color = "black", linestyle = "dashed")
    if(filename != None):
        to_save= filename+".svg"
        plt.savefig(to_save, format="svg")  
