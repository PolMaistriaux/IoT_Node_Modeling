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

from IoT_node_models.Node_description                        import *
from IoT_node_models.Node_description.Wireless_communication import *
from IoT_node_models.Component_set                    import *
from IoT_node_models.Analysis                            import *

path_to_save_svg = "Saved_Data"



if __name__ == '__main__':


    footprintStructure = FootprintStructure(("GWP", "Money"))

    RX_component_3V3 = Component(name="LoRa radio",category = "IC",
                            v=3.3,
                            i_sleep=6e-3,
                            factors = footprintStructure.vector(GWP=1.2, Money=0.02))
    
    RX_state_TX_3V3 = State("TX",i = 52,duration = None)
    RX_state_RX_3V3 = State("RX",i = 22,duration = None)
    RX_component_3V3.add_state(RX_state_TX_3V3)
    RX_component_3V3.add_state(RX_state_RX_3V3)


    bme_component_3V3   = Component(name="this_BME680",category = "IC",
                                v=BME_voltage_3V3,
                                i_sleep=BME_sleepCur_3V3)
    bme_state_T_3V3    = State("T", i = T_activCur_3V3,   duration = T_duration)
    bme_state_P_3V3    = State("P", i = P_activCur_3V3,   duration = P_duration)
    bme_state_H_3V3    = State("H", i = H_activCur_3V3,   duration = H_duration)
    bme_state_G_3V3    = State("G", i = G_activCur_3V3,   duration = G_duration)
    bme_state_TPH_3V3  = State("TPH", i = TPH_activCur_3V3, duration = TPH_duration)
    bme_state_TPHG_3V3 = State("TPHG",i = TPHG_activCur_3V3,duration = TPHG_duration)

    bme_component_3V3.add_state(bme_state_T_3V3)
    bme_component_3V3.add_state(bme_state_P_3V3)
    bme_component_3V3.add_state(bme_state_H_3V3)
    bme_component_3V3.add_state(bme_state_G_3V3)
    bme_component_3V3.add_state(bme_state_TPH_3V3)
    bme_component_3V3.add_state(bme_state_TPHG_3V3)

    MCU_component_3V3 = Component(name="Apollo3",category = "IC",
                                v      =3.3,
                                i_sleep=0.005,
                            factors = footprintStructure.vector(GWP=1))
    
    MCU_state_active_3V3  = State("Active",i = 5,duration = None)
    MCU_component_3V3.add_state(MCU_state_active_3V3)
    
    component_List = [RX_component_3V3,MCU_component_3V3, bme_component_3V3]

    this_LDO = LDO(name = "Node LDO", category = "PMU", v_out = 3.3, i_q = 1e-3, v_in = 3.3, component_list = component_List)
    
    this_Batt= Battery(name = "Node Batt.", category = "Battery", v = 3.3, capacity_mAh = 1800, i = 0, selfdischarge_p_year = 5)

    this_hw = Hardware(name= "IoT Node",footprintStructure=footprintStructure, categories=("IC","PMU","Battery","Casing"))
    for comp in component_List:
        this_hw.add(comp)
    this_hw.add(this_LDO)
    this_hw.add(this_Batt)

    
    Casing = Component(name="Casing", category = "Casing",factors = footprintStructure.vector(GWP=0.5, Money=0.3))
    this_hw.add(Casing)     
    
    this_profile= LoRa_Profile("Profile", this_hw,  RX_state=RX_state_TX_3V3,TX_state=RX_state_TX_3V3,
                        P_TX= PTX_PABOOST_3V3, I_TX=I_PABoost_3V3 ) 
                
    this_task_tx0 = this_profile.create_task_tx(name="TX-0", Ptx = 17,SF=7 ,Coding=1,Header=True,DE = 0,BW = 125e3, Payload = 50, TX_rate=24*1)
    this_task_rx0 = this_profile.create_task_rx(name="RX-0", RX_rate=2, RX_duration=0.250 )


    task_TPHG_3V3 =  Task(  name = "TPHG meas.", 
                            actions   = [   Action(name='Proc', componentState=MCU_state_active_3V3, stateDuration=TPHG_duration+ MCU_I2C),
                                            Action(name='TPHG' ,   componentState=bme_state_TPHG_3V3     , stateDuration=TPHG_duration)], 
                            taskDuration = TPHG_duration+ MCU_BME_duration, 
                            )

    this_profile.add_task(task_TPHG_3V3,24*12)

    this_node = Node_description(name="My_node",hardware=this_hw,profile=this_profile)

    def PL_model(d):
        return path_loss_PLd0(d=d, PLd0=94.40,d0=1, n=2.03)

    this_task_tx0.set_Path_loss_model(PL_model)
    this_task_tx0.set_distance( d= 1500)
    this_node.compute()
    this_node.print_tasks()
    this_node.print_components()
    this_node.plot_power()
    this_hw.compute_footprint()
    this_hw.report_footprint()
    plt.show()
