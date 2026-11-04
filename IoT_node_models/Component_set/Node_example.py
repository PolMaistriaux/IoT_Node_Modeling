
import sys
import os

from ..Node_description import *
from .Apollo3  import *
from .RFM95    import *
from .BME680   import *





component_List_1V8 = [apollo_component_1V8,radio_component_1V8,bme_component_1V8]

task_tx_1V8 =  Task(  name = "Send Message", 
                        actions   = [   Action(name='Proc',
                                        componentState = apollo_state_active_1V8, stateDuration=MCU_RFM_duration),
                                         Action(name='TX'  ,    componentState = radio_state_TX_1V8     , stateDuration=TX_duration)], 
                        taskDuration = 500e-3, 
                         )

task_rx_1V8 =  Task(  name = "Receive Message", 
                        actions   = [   Action(name='Proc', componentState = apollo_state_active_1V8, stateDuration=100e-3),
                                         Action(name='RX'  ,    componentState = radio_state_RX_1V8     , stateDuration=RX_duration)], 
                        taskDuration = 500e-3, 
                         )
    

task_rxtx_1V8 =  Task(  name = "RXTX Message", 
                        actions   = [   Action(name='Proc', componentState=apollo_state_active_1V8, stateDuration=100e-3),
                                         Action(name='TX'  ,    componentState=radio_state_TX_1V8     , stateDuration=TX_duration),
                                         Action(name='RX'  ,    componentState=radio_state_RX_1V8     , stateDuration=RX_duration)], 
                        taskDuration = 500e-3, 
                         )

task_T_1V8   =  Task(   name = "T meas.", 
                        actions   = [   Action(name='Proc', componentState=apollo_state_active_1V8, stateDuration=T_duration+ MCU_BME_duration),
                                         Action(name='TPH' ,    componentState=bme_state_T_1V8     , stateDuration=T_duration)], 
                        taskDuration = T_duration+ MCU_BME_duration, 
                         )

task_P_1V8 =  Task(   name = "P meas.", 
                        actions   = [   Action(name='Proc', componentState=apollo_state_active_1V8, stateDuration=P_duration+ MCU_BME_duration),
                                         Action(name='TPH' ,    componentState=bme_state_P_1V8     , stateDuration=P_duration)], 
                        taskDuration = P_duration+ MCU_BME_duration, 
                         )

task_H_1V8 =  Task(   name = "H meas.", 
                        actions   = [   Action(name='Proc', componentState=apollo_state_active_1V8, stateDuration=H_duration+ MCU_BME_duration),
                                         Action(name='TPH' ,    componentState=bme_state_H_1V8     , stateDuration=H_duration)], 
                        taskDuration = H_duration+ MCU_BME_duration, 
                         )

task_G_1V8 =  Task(   name = "G meas.", 
                        actions   = [   Action(name='Proc', componentState=apollo_state_active_1V8, stateDuration=G_duration+ MCU_BME_duration),
                                         Action(name='TPH' ,    componentState=bme_state_G_1V8     , stateDuration=G_duration)], 
                        taskDuration = G_duration+ MCU_BME_duration, 
                         )


task_TPH_1V8 =  Task(   name = "TPH meas.", 
                        actions   = [   Action(name='Proc', componentState=apollo_state_active_1V8, stateDuration=TPH_duration+ MCU_BME_duration),
                                         Action(name='TPH' ,    componentState=bme_state_TPH_1V8     , stateDuration=TPH_duration)], 
                        taskDuration = TPH_duration+ MCU_BME_duration, 
                         )

task_TPHG_1V8 =  Task(  name = "TPHG meas.", 
                        actions   = [   Action(name='Proc', componentState=apollo_state_active_1V8, stateDuration=TPHG_duration+ MCU_BME_duration),
                                         Action(name='TPHG' ,   componentState=bme_state_TPHG_1V8     , stateDuration=TPHG_duration)], 
                        taskDuration = TPHG_duration+ MCU_BME_duration, 
                         )


########################################################################################
##
#
#       3.3V Node tasks
#
#
########################################################################################


component_List_3V3 = [apollo_component_3V3,radio_component_3V3,bme_component_3V3]

task_tx_3V3 =  Task(  name = "Send Message", 
                        actions   = [   Action(name='Proc', componentState = apollo_state_active_3V3, stateDuration=MCU_RFM_duration),
                                         Action(name='TX'  ,    componentState = radio_state_TX_3V3     , stateDuration=TX_duration)], 
                        taskDuration = 500e-3, 
                         )

task_rx_3V3 =  Task(  name = "Receive Message", 
                        actions   = [   Action(name='Proc', componentState = apollo_state_active_3V3, stateDuration=100e-3),
                                         Action(name='RX'  ,    componentState = radio_state_RX_3V3     , stateDuration=RX_duration)], 
                        taskDuration = 500e-3, 
                         )
    

task_rxtx_3V3 =  Task(  name = "RXTX Message", 
                        actions   = [   Action(name='Proc', componentState=apollo_state_active_3V3, stateDuration=100e-3),
                                         Action(name='TX'  ,    componentState=radio_state_TX_3V3     , stateDuration=TX_duration),
                                         Action(name='RX'  ,    componentState=radio_state_RX_3V3     , stateDuration=RX_duration)], 
                        taskDuration = 500e-3, 
                         )

task_T_3V3   =  Task(   name = "T meas.", 
                        actions   = [   Action(name='Proc', componentState=apollo_state_active_3V3, stateDuration=T_duration+ MCU_BME_duration),
                                         Action(name='TPH' ,    componentState=bme_state_T_3V3     , stateDuration=T_duration)], 
                        taskDuration = T_duration+ MCU_BME_duration, 
                         )

task_P_3V3 =  Task(   name = "P meas.", 
                        actions   = [   Action(name='Proc', componentState=apollo_state_active_3V3, stateDuration=P_duration+ MCU_BME_duration),
                                         Action(name='TPH' ,    componentState=bme_state_P_3V3     , stateDuration=P_duration)], 
                        taskDuration = P_duration+ MCU_BME_duration, 
                         )

task_H_3V3 =  Task(   name = "H meas.", 
                        actions   = [   Action(name='Proc', componentState=apollo_state_active_3V3, stateDuration=H_duration+ MCU_BME_duration),
                                         Action(name='TPH' ,    componentState=bme_state_H_3V3     , stateDuration=H_duration)], 
                        taskDuration = H_duration+ MCU_BME_duration, 
                         )

task_G_3V3 =  Task(   name = "G meas.", 
                        actions   = [   Action(name='Proc', componentState=apollo_state_active_3V3, stateDuration=G_duration+ MCU_BME_duration),
                                         Action(name='TPH' ,    componentState=bme_state_G_3V3     , stateDuration=G_duration)], 
                        taskDuration = G_duration+ MCU_BME_duration, 
                         )


task_TPH_3V3 =  Task(   name = "TPH meas.", 
                        actions   = [   Action(name='Proc', componentState=apollo_state_active_3V3, stateDuration=TPH_duration+ MCU_I2C),
                                         Action(name='TPH' ,    componentState=bme_state_TPH_3V3     , stateDuration=TPH_duration)], 
                        taskDuration = TPH_duration+ MCU_BME_duration, 
                         )

task_TPHG_3V3 =  Task(  name = "TPHG meas.", 
                        actions   = [   Action(name='Proc', componentState=apollo_state_active_3V3, stateDuration=TPHG_duration+ MCU_I2C),
                                         Action(name='TPHG' ,   componentState=bme_state_TPHG_3V3     , stateDuration=TPHG_duration)], 
                        taskDuration = TPHG_duration+ MCU_BME_duration, 
                         )
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
