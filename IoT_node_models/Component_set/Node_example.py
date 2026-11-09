
import sys
import os

from ..Node_description import *
from .Apollo3  import *
from .RFM95    import *
from .BME680   import *


########################################################################################
##
#       Node tasks (supply voltage selected with set_node_voltage, default 3.3V)
##
########################################################################################

component_List = [apollo_component,radio_component,bme_component]

task_tx =  Task(  name = "Send Message", 
                        actions   = [   Action(name='Proc', componentState = apollo_state_active, stateDuration=MCU_RFM_duration),
                                         Action(name='TX'  ,    componentState = radio_state_TX     , stateDuration=TX_duration)], 
                        taskDuration = 500e-3, 
                         )

task_rx =  Task(  name = "Receive Message", 
                        actions   = [   Action(name='Proc', componentState = apollo_state_active, stateDuration=100e-3),
                                         Action(name='RX'  ,    componentState = radio_state_RX     , stateDuration=RX_duration)], 
                        taskDuration = 500e-3, 
                         )
    

task_rxtx =  Task(  name = "RXTX Message", 
                        actions   = [   Action(name='Proc', componentState=apollo_state_active, stateDuration=100e-3),
                                         Action(name='TX'  ,    componentState=radio_state_TX     , stateDuration=TX_duration),
                                         Action(name='RX'  ,    componentState=radio_state_RX     , stateDuration=RX_duration)], 
                        taskDuration = 500e-3, 
                         )

task_T   =  Task(   name = "T meas.", 
                        actions   = [   Action(name='Proc', componentState=apollo_state_active, stateDuration=T_duration+ MCU_BME_duration),
                                         Action(name='TPH' ,    componentState=bme_state_T     , stateDuration=T_duration)], 
                        taskDuration = T_duration+ MCU_BME_duration, 
                         )

task_P =  Task(   name = "P meas.", 
                        actions   = [   Action(name='Proc', componentState=apollo_state_active, stateDuration=P_duration+ MCU_BME_duration),
                                         Action(name='TPH' ,    componentState=bme_state_P     , stateDuration=P_duration)], 
                        taskDuration = P_duration+ MCU_BME_duration, 
                         )

task_H =  Task(   name = "H meas.", 
                        actions   = [   Action(name='Proc', componentState=apollo_state_active, stateDuration=H_duration+ MCU_BME_duration),
                                         Action(name='TPH' ,    componentState=bme_state_H     , stateDuration=H_duration)], 
                        taskDuration = H_duration+ MCU_BME_duration, 
                         )

task_G =  Task(   name = "G meas.", 
                        actions   = [   Action(name='Proc', componentState=apollo_state_active, stateDuration=G_duration+ MCU_BME_duration),
                                         Action(name='TPH' ,    componentState=bme_state_G     , stateDuration=G_duration)], 
                        taskDuration = G_duration+ MCU_BME_duration, 
                         )


task_TPH =  Task(   name = "TPH meas.", 
                        actions   = [   Action(name='Proc', componentState=apollo_state_active, stateDuration=TPH_duration+ MCU_I2C),
                                         Action(name='TPH' ,    componentState=bme_state_TPH     , stateDuration=TPH_duration)], 
                        taskDuration = TPH_duration+ MCU_BME_duration, 
                         )

task_TPHG =  Task(  name = "TPHG meas.", 
                        actions   = [   Action(name='Proc', componentState=apollo_state_active, stateDuration=TPHG_duration+ MCU_I2C),
                                         Action(name='TPHG' ,   componentState=bme_state_TPHG     , stateDuration=TPHG_duration)], 
                        taskDuration = TPHG_duration+ MCU_BME_duration, 
                         )

# Backward-compatible aliases
component_List_3V3 = component_List_1V8 = component_List
task_tx_3V3 = task_tx_1V8 = task_tx
task_rx_3V3 = task_rx_1V8 = task_rx
task_rxtx_3V3 = task_rxtx_1V8 = task_rxtx
task_T_3V3 = task_T_1V8 = task_T
task_P_3V3 = task_P_1V8 = task_P
task_H_3V3 = task_H_1V8 = task_H
task_G_3V3 = task_G_1V8 = task_G
task_TPH_3V3 = task_TPH_1V8 = task_TPH
task_TPHG_3V3 = task_TPHG_1V8 = task_TPHG


def set_node_voltage(v):
    """Switch every component of the example node to supply voltage v (e.g. 1.8 or 3.3)."""
    for c in component_List:
        c.set_v(v)

# %%

########################################################################################
##
#
#       3.3V Node tasks DATASHEET
# 
#
########################################################################################


component_List_Data = [apollo_component_Data,radio_component_Data,bme_component_Data]

task_tx_Data =  Task(  name = "Send Message", 
                        actions   = [   Action(name='Proc', componentState = apollo_state_active_Data, stateDuration=MCU_RFM_duration),
                                         Action(name='TX'  ,    componentState = radio_state_TX_Data     , stateDuration=TX_duration)], 
                        taskDuration = 500e-3, 
                         )

task_rx_Data =  Task(  name = "Receive Message", 
                        actions   = [   Action(name='Proc', componentState = apollo_state_active_Data, stateDuration=100e-3),
                                         Action(name='RX'  ,    componentState = radio_state_RX_Data     , stateDuration=RX_duration)], 
                        taskDuration = 500e-3, 
                         )
    

task_rxtx_Data =  Task(  name = "RXTX Message", 
                        actions   = [   Action(name='Proc', componentState=apollo_state_active_Data, stateDuration=100e-3),
                                         Action(name='TX'  ,    componentState=radio_state_TX_Data     , stateDuration=TX_duration),
                                         Action(name='RX'  ,    componentState=radio_state_RX_Data     , stateDuration=RX_duration)], 
                        taskDuration = 500e-3, 
                         )



task_TPHG_Data =  Task(  name = "TPHG meas.", 
                        actions   = [   Action(name='Proc', componentState=apollo_state_active_Data, stateDuration=TPHG_duration+ MCU_BME_duration),
                                         Action(name='TPHG' ,   componentState=bme_state_TPHG_Data     , stateDuration=TPHG_duration)], 
                        taskDuration = TPHG_duration+ MCU_BME_duration, 
                         )
