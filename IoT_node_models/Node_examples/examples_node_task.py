
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from IoT_node_models.Energy_model.Node_profile import *

from IoT_node_models.Hardware_Modules.Apollo3 import *
from IoT_node_models.Hardware_Modules.RFM95   import *
from IoT_node_models.Hardware_Modules.BME680  import *





module_List_1V8 = [apollo_module_1V8,radio_module_1V8,bme_module_1V8]

task_tx_1V8 =  Node_task(  name = "Send Message", 
                        node_modules= module_List_1V8, 
                        #moduleUsed = [  apollo_module_1V8,
                        #                radio_module_1V8], 
                        subtasks   = [   Node_subtask(name='Proc',module=apollo_module_1V8,
                                        moduleState = apollo_state_active_1V8, stateDuration=MCU_RFM_duration),
                                         Node_subtask(name='TX'  ,module=radio_module_1V8 ,
                                        moduleState = radio_state_TX_1V8     , stateDuration=TX_duration)], 
                        taskDuration = 500e-3, 
                         )

task_rx_1V8 =  Node_task(  name = "Receive Message", 
                        node_modules= module_List_1V8, 
                        #moduleUsed = [  apollo_module_1V8,
                        #                radio_module_1V8], 
                        subtasks   = [   Node_subtask(name='Proc',module=apollo_module_1V8,
                                        moduleState = apollo_state_active_1V8, stateDuration=100e-3),
                                         Node_subtask(name='RX'  ,module=radio_module_1V8 ,
                                        moduleState = radio_state_RX_1V8     , stateDuration=RX_duration)], 
                        taskDuration = 500e-3, 
                         )
    

task_rxtx_1V8 =  Node_task(  name = "RXTX Message", 
                        node_modules= module_List_1V8, 
                        #moduleUsed = [  apollo_module_1V8,
                        #                radio_module_1V8], 
                        subtasks   = [   Node_subtask(name='Proc',module=apollo_module_1V8,
                                        moduleState=apollo_state_active_1V8, stateDuration=100e-3),
                                         Node_subtask(name='TX'  ,module=radio_module_1V8 ,
                                        moduleState=radio_state_TX_1V8     , stateDuration=TX_duration),
                                         Node_subtask(name='RX'  ,module=radio_module_1V8 ,
                                        moduleState=radio_state_RX_1V8     , stateDuration=RX_duration)], 
                        taskDuration = 500e-3, 
                         )

task_T_1V8   =  Node_task(   name = "T meas.", 
                        node_modules= module_List_1V8, 
                        #moduleUsed = [  apollo_module_1V8,
                        #                bme_module_1V8], 
                        subtasks   = [   Node_subtask(name='Proc',module=apollo_module_1V8,
                                        moduleState=apollo_state_active_1V8, stateDuration=T_duration+ MCU_BME_duration),
                                         Node_subtask(name='TPH' ,module=bme_module_1V8 ,
                                        moduleState=bme_state_T_1V8     , stateDuration=T_duration)], 
                        taskDuration = T_duration+ MCU_BME_duration, 
                         )

task_P_1V8 =  Node_task(   name = "P meas.", 
                        node_modules= module_List_1V8, 
                        #moduleUsed = [  apollo_module_1V8,
                        #                bme_module_1V8], 
                        subtasks   = [   Node_subtask(name='Proc',module=apollo_module_1V8,
                                        moduleState=apollo_state_active_1V8, stateDuration=P_duration+ MCU_BME_duration),
                                         Node_subtask(name='TPH' ,module=bme_module_1V8 ,
                                        moduleState=bme_state_P_1V8     , stateDuration=P_duration)], 
                        taskDuration = P_duration+ MCU_BME_duration, 
                         )

task_H_1V8 =  Node_task(   name = "H meas.", 
                        node_modules= module_List_1V8, 
                        #moduleUsed = [  apollo_module_1V8,
                        #                bme_module_1V8], 
                        subtasks   = [   Node_subtask(name='Proc',module=apollo_module_1V8,
                                        moduleState=apollo_state_active_1V8, stateDuration=H_duration+ MCU_BME_duration),
                                         Node_subtask(name='TPH' ,module=bme_module_1V8 ,
                                        moduleState=bme_state_H_1V8     , stateDuration=H_duration)], 
                        taskDuration = H_duration+ MCU_BME_duration, 
                         )

task_G_1V8 =  Node_task(   name = "G meas.", 
                        node_modules= module_List_1V8, 
                        #moduleUsed = [  apollo_module_1V8,
                        #                bme_module_1V8], 
                        subtasks   = [   Node_subtask(name='Proc',module=apollo_module_1V8,
                                        moduleState=apollo_state_active_1V8, stateDuration=G_duration+ MCU_BME_duration),
                                         Node_subtask(name='TPH' ,module=bme_module_1V8 ,
                                        moduleState=bme_state_G_1V8     , stateDuration=G_duration)], 
                        taskDuration = G_duration+ MCU_BME_duration, 
                         )


task_TPH_1V8 =  Node_task(   name = "TPH meas.", 
                        node_modules= module_List_1V8, 
                        #moduleUsed = [  apollo_module_1V8,
                        #                bme_module_1V8], 
                        subtasks   = [   Node_subtask(name='Proc',module=apollo_module_1V8,
                                        moduleState=apollo_state_active_1V8, stateDuration=TPH_duration+ MCU_BME_duration),
                                         Node_subtask(name='TPH' ,module=bme_module_1V8 ,
                                        moduleState=bme_state_TPH_1V8     , stateDuration=TPH_duration)], 
                        taskDuration = TPH_duration+ MCU_BME_duration, 
                         )

task_TPHG_1V8 =  Node_task(  name = "TPHG meas.", 
                        node_modules= module_List_1V8, 
                        #moduleUsed = [  apollo_module_1V8,
                        #                bme_module_1V8], 
                        subtasks   = [   Node_subtask(name='Proc',module=apollo_module_1V8,
                                        moduleState=apollo_state_active_1V8, stateDuration=TPHG_duration+ MCU_BME_duration),
                                         Node_subtask(name='TPHG' ,module=bme_module_1V8 ,
                                        moduleState=bme_state_TPHG_1V8     , stateDuration=TPHG_duration)], 
                        taskDuration = TPHG_duration+ MCU_BME_duration, 
                         )


########################################################################################
##
#
#       3.3V Node tasks
#
#
########################################################################################


module_List_3V3 = [apollo_module_3V3,radio_module_3V3,bme_module_3V3]

task_tx_3V3 =  Node_task(  name = "Send Message", 
                        node_modules= module_List_3V3, 
                        #moduleUsed = [  apollo_module_3V3,
                        #                radio_module_3V3], 
                        subtasks   = [   Node_subtask(name='Proc',module=apollo_module_3V3,
                                        moduleState = apollo_state_active_3V3, stateDuration=MCU_RFM_duration),
                                         Node_subtask(name='TX'  ,module=radio_module_3V3 ,
                                        moduleState = radio_state_TX_3V3     , stateDuration=TX_duration)], 
                        taskDuration = 500e-3, 
                         )

task_rx_3V3 =  Node_task(  name = "Receive Message", 
                        node_modules= module_List_3V3, 
                        #moduleUsed = [  apollo_module_3V3,
                        #                radio_module_3V3], 
                        subtasks   = [   Node_subtask(name='Proc',module=apollo_module_3V3,
                                        moduleState = apollo_state_active_3V3, stateDuration=100e-3),
                                         Node_subtask(name='RX'  ,module=radio_module_3V3 ,
                                        moduleState = radio_state_RX_3V3     , stateDuration=RX_duration)], 
                        taskDuration = 500e-3, 
                         )
    

task_rxtx_3V3 =  Node_task(  name = "RXTX Message", 
                        node_modules= module_List_3V3, 
                        #moduleUsed = [  apollo_module_3V3,
                        #                radio_module_3V3], 
                        subtasks   = [   Node_subtask(name='Proc',module=apollo_module_3V3,
                                        moduleState=apollo_state_active_3V3, stateDuration=100e-3),
                                         Node_subtask(name='TX'  ,module=radio_module_3V3 ,
                                        moduleState=radio_state_TX_3V3     , stateDuration=TX_duration),
                                         Node_subtask(name='RX'  ,module=radio_module_3V3 ,
                                        moduleState=radio_state_RX_3V3     , stateDuration=RX_duration)], 
                        taskDuration = 500e-3, 
                         )

task_T_3V3   =  Node_task(   name = "T meas.", 
                        node_modules= module_List_3V3, 
                        #moduleUsed = [  apollo_module_3V3,
                        #                bme_module_3V3], 
                        subtasks   = [   Node_subtask(name='Proc',module=apollo_module_3V3,
                                        moduleState=apollo_state_active_3V3, stateDuration=T_duration+ MCU_BME_duration),
                                         Node_subtask(name='TPH' ,module=bme_module_3V3 ,
                                        moduleState=bme_state_T_3V3     , stateDuration=T_duration)], 
                        taskDuration = T_duration+ MCU_BME_duration, 
                         )

task_P_3V3 =  Node_task(   name = "P meas.", 
                        node_modules= module_List_3V3, 
                        #moduleUsed = [  apollo_module_3V3,
                        #                bme_module_3V3], 
                        subtasks   = [   Node_subtask(name='Proc',module=apollo_module_3V3,
                                        moduleState=apollo_state_active_3V3, stateDuration=P_duration+ MCU_BME_duration),
                                         Node_subtask(name='TPH' ,module=bme_module_3V3 ,
                                        moduleState=bme_state_P_3V3     , stateDuration=P_duration)], 
                        taskDuration = P_duration+ MCU_BME_duration, 
                         )

task_H_3V3 =  Node_task(   name = "H meas.", 
                        node_modules= module_List_3V3, 
                        #moduleUsed = [  apollo_module_3V3,
                        #                bme_module_3V3], 
                        subtasks   = [   Node_subtask(name='Proc',module=apollo_module_3V3,
                                        moduleState=apollo_state_active_3V3, stateDuration=H_duration+ MCU_BME_duration),
                                         Node_subtask(name='TPH' ,module=bme_module_3V3 ,
                                        moduleState=bme_state_H_3V3     , stateDuration=H_duration)], 
                        taskDuration = H_duration+ MCU_BME_duration, 
                         )

task_G_3V3 =  Node_task(   name = "G meas.", 
                        node_modules= module_List_3V3, 
                        #moduleUsed = [  apollo_module_3V3,
                        #                bme_module_3V3], 
                        subtasks   = [   Node_subtask(name='Proc',module=apollo_module_3V3,
                                        moduleState=apollo_state_active_3V3, stateDuration=G_duration+ MCU_BME_duration),
                                         Node_subtask(name='TPH' ,module=bme_module_3V3 ,
                                        moduleState=bme_state_G_3V3     , stateDuration=G_duration)], 
                        taskDuration = G_duration+ MCU_BME_duration, 
                         )


task_TPH_3V3 =  Node_task(   name = "TPH meas.", 
                        node_modules= module_List_3V3, 
                        #moduleUsed = [  apollo_module_3V3,
                        #                bme_module_3V3], 
                        subtasks   = [   Node_subtask(name='Proc',module=apollo_module_3V3,
                                        moduleState=apollo_state_active_3V3, stateDuration=TPH_duration+ MCU_I2C),
                                         Node_subtask(name='TPH' ,module=bme_module_3V3 ,
                                        moduleState=bme_state_TPH_3V3     , stateDuration=TPH_duration)], 
                        taskDuration = TPH_duration+ MCU_BME_duration, 
                         )

task_TPHG_3V3 =  Node_task(  name = "TPHG meas.", 
                        node_modules= module_List_3V3, 
                        #moduleUsed = [  apollo_module_3V3,
                        #                bme_module_3V3], 
                        subtasks   = [   Node_subtask(name='Proc',module=apollo_module_3V3,
                                        moduleState=apollo_state_active_3V3, stateDuration=TPHG_duration+ MCU_I2C),
                                         Node_subtask(name='TPHG' ,module=bme_module_3V3 ,
                                        moduleState=bme_state_TPHG_3V3     , stateDuration=TPHG_duration)], 
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


module_List_Data = [apollo_module_Data,radio_module_Data,bme_module_Data]

task_tx_Data =  Node_task(  name = "Send Message", 
                        node_modules= module_List_Data, 
                        #moduleUsed = [  apollo_module_Data,
                        #                radio_module_Data], 
                        subtasks   = [   Node_subtask(name='Proc',module=apollo_module_Data,
                                        moduleState = apollo_state_active_Data, stateDuration=MCU_RFM_duration),
                                         Node_subtask(name='TX'  ,module=radio_module_Data ,
                                        moduleState = radio_state_TX_Data     , stateDuration=TX_duration)], 
                        taskDuration = 500e-3, 
                         )

task_rx_Data =  Node_task(  name = "Receive Message", 
                        node_modules= module_List_Data, 
                        #moduleUsed = [  apollo_module_Data,
                        #                radio_module_Data], 
                        subtasks   = [   Node_subtask(name='Proc',module=apollo_module_Data,
                                        moduleState = apollo_state_active_Data, stateDuration=100e-3),
                                         Node_subtask(name='RX'  ,module=radio_module_Data ,
                                        moduleState = radio_state_RX_Data     , stateDuration=RX_duration)], 
                        taskDuration = 500e-3, 
                         )
    

task_rxtx_Data =  Node_task(  name = "RXTX Message", 
                        node_modules= module_List_Data, 
                        #moduleUsed = [  apollo_module_Data,
                        #                radio_module_Data], 
                        subtasks   = [   Node_subtask(name='Proc',module=apollo_module_Data,
                                        moduleState=apollo_state_active_Data, stateDuration=100e-3),
                                         Node_subtask(name='TX'  ,module=radio_module_Data ,
                                        moduleState=radio_state_TX_Data     , stateDuration=TX_duration),
                                         Node_subtask(name='RX'  ,module=radio_module_Data ,
                                        moduleState=radio_state_RX_Data     , stateDuration=RX_duration)], 
                        taskDuration = 500e-3, 
                         )



task_TPHG_Data =  Node_task(  name = "TPHG meas.", 
                        node_modules= module_List_Data, 
                        #moduleUsed = [  apollo_module_Data,
                        #                bme_module_Data], 
                        subtasks   = [   Node_subtask(name='Proc',module=apollo_module_Data,
                                        moduleState=apollo_state_active_Data, stateDuration=TPHG_duration+ MCU_BME_duration),
                                         Node_subtask(name='TPHG' ,module=bme_module_Data ,
                                        moduleState=bme_state_TPHG_Data     , stateDuration=TPHG_duration)], 
                        taskDuration = TPHG_duration+ MCU_BME_duration, 
                         )
