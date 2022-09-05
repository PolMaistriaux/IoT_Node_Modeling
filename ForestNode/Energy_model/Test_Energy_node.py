#%%
from matplotlib import pyplot as plt
import matplotlib.pyplot as plt

plt.rcParams['figure.facecolor'] = 'white'
plt.rcParams['figure.facecolor'] = 'white'
plt.rcParams['mathtext.fontset'] = 'stix'
plt.rcParams['font.family'] = 'STIXGeneral'
plt.rcParams['font.size'] = 16
import math
import numpy as np
import inspect
import plotly.graph_objects as go
import plotly.express as px
import plotly.io as pio
pio.renderers.default = "svg"
from plotly.offline import plot
import sys
import os
file_path = os.path.abspath(__file__)
parent_dir_path         = os.path.dirname(os.path.dirname(file_path))
path_to_import_mainDir  = os.path.dirname(parent_dir_path)
path_to_import          = os.path.join(parent_dir_path,"Characterization")
path_to_import_LoRa    = os.path.join(os.path.dirname(parent_dir_path),"LoRa")

sys.path.append(path_to_import_mainDir)
sys.path.append(path_to_import)
sys.path.append(path_to_import_LoRa)

from Energy_node_Lora   import *
from MyColors           import *
from Node_task          import*
from Energy_node        import *
from Power_Unit         import *

path_to_save_svg = "D:/Pol/Documents/Research/Paper/ForestMe_Node/Figures/Generated_SVG"

###########################################################################################

def compare_results(Node_charac = None, Node_datasheet = None, trace_RFM = 0, trace_BME =0, trace_MCU = 0,duration_trace_min = 0,filename=None,figsize=(6,5)):
    Node_charac.recompute()   
    Node_charac_RFM = 0 
    Node_charac_BME = 0
    Node_charac_MCU = 0
    for module in Node_charac.module_list:
        if module.name == "LoRa radio":
            Node_charac_RFM = 1000*module.energy_day /(24*60*60)
            print(Node_charac_RFM)
        if module.name == "BME680":
            Node_charac_BME = 1000*module.energy_day /(24*60*60)
        if module.name == "Apollo3":
            Node_charac_MCU = 1000*module.energy_day /(24*60*60)

    Node_datasheet.recompute()
    Node_datasheet_RFM = 0 
    Node_datasheet_BME = 0
    Node_datasheet_MCU = 0
    for module in Node_datasheet.module_list:
        if module.name == "LoRa radio":
            Node_datasheet_RFM = 1000*module.energy_day /(24*60*60)
            print(Node_datasheet_RFM)
        if module.name == "BME680":
            Node_datasheet_BME = 1000*module.energy_day /(24*60*60)
        if module.name == "Apollo3":
            Node_datasheet_MCU = 1000*module.energy_day /(24*60*60)

    print(trace_RFM)
    Datasheet_RFM = np.array([0,0,0,Node_datasheet_RFM])
    Datasheet_BME = np.array([0,0,0,Node_datasheet_BME])
    Datasheet_MCU = np.array([0,0,0,Node_datasheet_MCU])
    
    Charac_RFM    = np.array([0,0,0,Node_charac_RFM])
    Charac_BME    = np.array([0,0,0,Node_charac_BME])
    Charac_MCU    = np.array([0,0,0,Node_charac_MCU])

    Trace_RFM     = np.array([0,0,0,trace_RFM])
    Trace_BME     = np.array([0,0,0,trace_BME])
    Trace_MCU     = np.array([0,0,0,trace_MCU])

    Result_RFM = np.array([Node_datasheet_RFM,Node_charac_RFM,trace_RFM])
    Result_BME = np.array([Node_datasheet_BME,Node_charac_BME,trace_BME])
    Result_MCU = np.array([Node_datasheet_MCU,Node_charac_MCU,trace_MCU])
    Result_Tot = Result_RFM + Result_BME + Result_MCU
    Results    = np.array([Result_MCU,Result_BME,Result_RFM,[0,0,0]])
    
    Result_label = ["Apollo3","BME680","RFM95", "Total"]
    index = np.arange(4)

    fig,ax = plt.subplots(1,1,figsize=figsize )
    bar_width = 0.2
    bar_space = 0.2
    linewidth = 0.9

    ax.bar(index            ,Results[:,0]  ,bar_width,color = dictColor["Sandy"],edgecolor='black',linewidth=linewidth,label =    "Model based on datasheet")
    ax.bar(index            ,Datasheet_RFM ,bar_width,color = dictColor["Sandy"],edgecolor='black',linewidth=linewidth)
    ax.bar(index            ,Datasheet_BME ,bar_width,color = dictColor["Sandy"],edgecolor='black',linewidth=linewidth, bottom=Datasheet_RFM)
    ax.bar(index            ,Datasheet_MCU ,bar_width,color = dictColor["Sandy"],edgecolor='black',linewidth=linewidth, bottom=Datasheet_RFM+Datasheet_BME)

    ax.bar(index+  bar_space,Results[:,1],bar_width,color = dictColor["Olivine"],edgecolor='black',linewidth=linewidth,label = "Model based on characterization")
    ax.bar(index+  bar_space,Charac_RFM  ,bar_width,color = dictColor["Olivine"],edgecolor='black',linewidth=linewidth)
    ax.bar(index+  bar_space,Charac_BME  ,bar_width,color = dictColor["Olivine"],edgecolor='black',linewidth=linewidth, bottom=Charac_RFM)
    ax.bar(index+  bar_space,Charac_MCU  ,bar_width,color = dictColor["Olivine"],edgecolor='black',linewidth=linewidth, bottom=Charac_RFM+Charac_BME)

    ax.bar(index+2*bar_space,Results[:,2],bar_width,color = dictColor["CarolinaBlue"],edgecolor='black',linewidth=linewidth,label = "Computed from trace captured")
    ax.bar(index+2*bar_space,Trace_RFM  ,bar_width,color =  dictColor["CarolinaBlue"],edgecolor='black',linewidth=linewidth)
    ax.bar(index+2*bar_space,Trace_BME  ,bar_width,color =  dictColor["CarolinaBlue"],edgecolor='black',linewidth=linewidth, bottom=Trace_RFM)
    ax.bar(index+2*bar_space,Trace_MCU  ,bar_width,color =  dictColor["CarolinaBlue"],edgecolor='black',linewidth=linewidth, bottom=Trace_RFM+Trace_BME)

    ax.set_xticks(index + bar_space,Result_label)
    ax.legend()
    ax.set_ylabel("Power [$\mu W$]",fontsize =20)
    ax.set_ylim(ymin = 0, ymax = np.max(Result_Tot)*1.13)

    if(filename != None):
        to_save = filename+".svg"
        plt.savefig(to_save, format="svg")

    TotalTrace   = trace_RFM+trace_MCU+trace_BME
    TotalCharac = Node_charac_RFM+Node_charac_MCU+Node_charac_BME
    TotalData   = Node_datasheet_RFM+Node_datasheet_MCU+Node_datasheet_BME
    ErrorCharac = (TotalCharac)/TotalTrace -1
    ErrorData   = (TotalData)/TotalTrace   -1
    print("Error experimental/charac model : %.1f %%"%(ErrorCharac*100))
    print("Error experimental/data   model : %.1f %%"%(ErrorData*100))
    print("Repartition Model Charac. : %.1f %%, %.1f %%, %.1f %%"%(100*Node_charac_MCU/TotalCharac ,100*Node_charac_BME/TotalCharac ,100*Node_charac_RFM/TotalCharac ))
    print("Apollo :  %.1f uW, %.1f uW, %.1f uW"%(Node_datasheet_MCU ,Node_charac_MCU ,trace_MCU ))
    plt.show()
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

if __name__ == '__main__':
    Payload   = 50
    SF_used   = 12
    P_tx_used = 17
    message_duration = LoRa.time_on_air(Payload=Payload,Coding=1,Header=1,DE = None,B = 125e3,SF=SF_used, Bytes=True)


    tphg_per_hour = 12 
    send_per_hour = 4

    tphg_per_day = tphg_per_hour*24
    send_per_day = send_per_hour*24

    task_TPHG_3V3.task_rate = tphg_per_day
    task_T_3V3.task_rate    = tphg_per_day
    task_P_3V3.task_rate    = tphg_per_day
    task_H_3V3.task_rate    = tphg_per_day
    task_G_3V3.task_rate    = tphg_per_day
    task_tx_3V3.task_rate   = send_per_day

    if(False):
        task_tx_3V3.taskDuration = message_duration 
        task_tx_3V3.find_subtask("TX").stateDuration   = message_duration
        #task_tx_3V3.find_subtask("Proc").stateDuration = 0
        #task_tx_3V3.find_subtask("TX").moduleState.i_active = 11.6

        task_Proc =  Node_task(   name = "MCU processing", 
                            node_modules= module_List_3V3, 
                            moduleUsed = [apollo_module_3V3], 
                            subtasks   = [   Node_subtask(name='Proc',module=apollo_module_3V3,
                                            moduleState=apollo_state_active_3V3, stateDuration= MCU_BME_duration)], 
                            taskDuration = MCU_BME_duration, 
                            task_rate =tphg_per_day)
        
        task_T_3V3.find_subtask("Proc").stateDuration = T_duration
        task_P_3V3.find_subtask("Proc").stateDuration = P_duration
        task_H_3V3.find_subtask("Proc").stateDuration = H_duration
        task_G_3V3.find_subtask("Proc").stateDuration = G_duration

    # %%
    ############################
    #3.3V From charac
    ############################
    node = LoRa_node(module_list = module_List_3V3,  PMU_composition =None, Battery = None, 
                    MCU_module   = apollo_module_3V3, MCU_active_state = apollo_state_active_3V3,
                    radio_module = radio_module_3V3,  radio_state_TX=radio_state_TX_3V3, radio_state_RX= radio_state_RX_3V3, Ptx = 2)


    
    node.task_tx.task_rate = send_per_day
    node.set_radio_parameters(SF=SF_used ,Coding=1,Header=True,DE = None,BW = 125e3, Payload = Payload) 
    #node.change_TX_duration(308.18304/1000)
    node.set_TX_Power_config( P_TX= PTX_PABOOST_configured, I_TX=I_PABoost_3V3)  
    node.set_TX_Power(Ptx = P_tx_used)

    node.add_task(task_TPHG_3V3)

    node.recompute()
    node.print_Tasks()
    node.print_Modules()
    node.plot_Modules(save=True,filename=os.path.join(path_to_save_svg , "Module_repartition"))
    node.plot_Power(save=False,filename = "Verification_charac")

    ############################
    #3.3V from datasheet
    ############################

    nodeData = LoRa_node(module_list = module_List_Data,  PMU_composition =None, Battery = None, 
                    MCU_module   = apollo_module_Data, MCU_active_state = apollo_state_active_Data,
                    radio_module = radio_module_Data,  radio_state_TX=radio_state_TX_Data, radio_state_RX= radio_state_RX_Data, Ptx = 2)

    nodeData.task_tx.task_rate = send_per_day
    nodeData.set_radio_parameters(SF=SF_used ,Coding=1,Header=True,DE = None,BW = 125e3, Payload = Payload) 
    #nodeData.change_TX_duration(308.18304/1000)
    nodeData.set_TX_Power_config( P_TX= PTX_Data, I_TX=I_Data)  
    nodeData.set_TX_Power(Ptx = P_tx_used)

    task_TPHG_Data.task_rate = tphg_per_day
    nodeData.add_task(task_TPHG_Data)
    nodeData.recompute()
    nodeData.print_Tasks()
    nodeData.print_Modules()

    compare_results(Node_charac = node, Node_datasheet = nodeData, 
                    trace_BME = 0.10988588055661144*1000*3.3,
                    trace_RFM = 0.22111193436646373*1000*3.3,
                    trace_MCU = 0.00653395090325724*1000*3.3,
                    duration_trace_min = 10,filename = os.path.join(path_to_save_svg , "Model_validation"))
    # %%

# %%
