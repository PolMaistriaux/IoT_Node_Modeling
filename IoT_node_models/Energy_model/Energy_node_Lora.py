#%%
import scipy.interpolate
import numpy as np

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from IoT_node_models.Wireless_communication   import LoRa_library as LoRa
from IoT_node_models.Energy_model.Energy_node import *
from IoT_node_models.Energy_model.Power_Unit  import *


################################
# LoRa_node contains a - radio module
#                      - mcu
#                      - one or multiple other peripherals
#
# Other peripherals have to be registered as done with Node_profile
# LoRa_node handles calculation of transmission duration and energy based on communication parameters:
#       * SF
#       * CR
#       * P_TX
#       * Header
################################
class LoRa_node(Node):
    def __init__(self,name = None, module_list = [], PMU_composition =[], Battery = None,MCU_module = None, radio_module = None, MCU_active_state =None, MCU_active_duration_tx = 0.3, MCU_active_duration_rx = 0.3,radio_state_TX = None, radio_state_RX =None,Ptx = 2): 
        super().__init__(name = name, module_list = module_list , PMU_composition = PMU_composition, Battery =Battery)
        self.MCU_module       = MCU_module
        self.MCU_active_state = MCU_active_state
        self.radio_module     = radio_module
        self.radio_state_TX   = radio_state_TX
        self.radio_state_RX   = radio_state_RX
        
        self.TX_duration = 0
        self.MCU_active_duration_tx = MCU_active_duration_tx
        self.task_tx_duration = self.MCU_active_duration_tx + self.TX_duration
        self.mcu_subtask_Tx   = Node_subtask( name='Proc',module=self.MCU_module,
                                                    moduleState=self.MCU_active_state, stateDuration=self.MCU_active_duration_tx)
        self.radio_subtask_Tx = Node_subtask( name='TX'    ,module=self.radio_module ,
                                                    moduleState=self.radio_state_TX ,stateDuration=self.TX_duration)
        self.task_tx = Node_task( name = "TX", 
                                        node_modules= module_list,                                         #moduleUsed = [  self.MCU_module,     self.radio_module], 
                                        subtasks   = [  self.mcu_subtask_Tx, self.radio_subtask_Tx], 
                                        taskDuration = self.task_tx_duration, 
                                        #task_rate =1
                                        )
        

        self.RX_duration = 0
        self.MCU_active_duration_rx = MCU_active_duration_rx 
        self.task_rx_duration = self.MCU_active_duration_rx + self.RX_duration
        self.mcu_subtask_Rx   = Node_subtask( name='Proc',module=self.MCU_module,
                                                    moduleState=self.MCU_active_state, stateDuration=self.MCU_active_duration_rx)
        self.radio_subtask_Rx = Node_subtask( name='RX'    ,module=self.radio_module ,
                                                     moduleState=self.radio_state_RX ,stateDuration=self.RX_duration)
        self.task_rx = Node_task( name = "RX", 
                                        node_modules= module_list,                                         #moduleUsed = [  self.MCU_module,     self.radio_module], 
                                        subtasks   = [  self.mcu_subtask_Rx, self.radio_subtask_Rx ], 
                                        taskDuration = self.task_rx_duration, 
                                         #task_rate =1
                                        )
        
        self.SF = 7
        self.Payload = 100
        self.Header = True
        self.DE = None
        self.Coding = 1
        self.BW = 125e3
        self.Ptx = Ptx
        self.P_TX_interpolator = None
        self.TX_duration  = LoRa.time_on_air(Payload=self.Payload,Coding=self.Coding,Header=self.Header,DE = self.DE,B = self.BW,SF=self.SF, Bytes=True)
        self.add_task(self.task_tx,1)
        self.add_task(self.task_rx,1)

    def set_TX_Power_config(self, P_TX, I_TX ):
        if np.size(I_TX)==0 or np.size(P_TX)==0 :
            print("Error: array provided to set_TX_Power_config is empty")
        elif len(P_TX) != len(I_TX):
            print("Error: arrays provided to set_TX_Power_config have different lengths")
        else : 
            self.I_TX = I_TX
            self.P_TX  = P_TX
            self.P_TX_interpolator = scipy.interpolate.interp1d(self.P_TX,self.I_TX )
            self.set_TX_Power(Ptx=self.Ptx)

    def set_TX_Power(self, Ptx=0, Itx=0):
        if Itx==0 and self.P_TX_interpolator == None: 
            print("Error : No power config. made and no Itx specified")
        if np.size(self.I_TX)==0 or np.size(self.P_TX)==0 :
            self.Ptx = Ptx
            self.radio_state_TX.i = Itx
        else : 
            if(Ptx < np.min(self.P_TX)):
                Ptx = np.min(self.P_TX)
            elif (Ptx > np.max(self.P_TX)):
                Ptx = np.max(self.P_TX)
            self.Ptx = Ptx
            self.radio_state_TX.i = self.P_TX_interpolator(Ptx)


    #Typical :SF=7,Coding=1,Header=True,DE = None,BW = 125e3, Payload = 100, Ptx = 0, Rx_duration = 0.250
    def set_radio_parameters(self, SF=None,Coding=None,Header=None,DE = None,BW = None, Payload = None):
        if SF != None:
            self.SF = SF
        if Payload != None:
            self.Payload = Payload
        if Header != None:
            self.Header = Header
        if DE != None:
            self.DE = DE
        if Coding != None:
            self.Coding = Coding
        if BW != None:
            self.BW = BW
        self.compute_tx_time()

    def compute_tx_time(self):
        durationTX =  LoRa.time_on_air(Payload=self.Payload,Coding=self.Coding,Header=self.Header,DE = self.DE,B = self.BW,SF=self.SF, Bytes=True)
        self.change_TX_duration(durationTX)

    def change_TX_duration(self,duration):
        self.TX_duration                    = duration
        self.radio_subtask_Tx.stateDuration = duration
        self.task_tx_duration               = duration + self.MCU_active_duration_tx
        self.task_tx.taskDuration           = self.task_tx_duration

    def change_MCU_TX_duration(self,duration):
        self.MCU_active_duration_Tx         = duration
        self.mcu_subtask_Tx.stateDuration   = duration
        self.task_tx_duration               = duration + self.TX_duration
        self.task_tx.taskDuration           = self.task_tx_duration

    def change_RX_duration(self,duration):
        self.RX_duration                    = duration
        self.radio_subtask_Rx.stateDuration = duration
        self.task_rx_duration               = duration + self.MCU_active_duration_rx
        self.task_rx.taskDuration           = self.task_rx_duration

    def change_MCU_RX_duration(self,duration):
        self.MCU_active_duration_Rx         = duration
        self.mcu_subtask_Rx.stateDuration   = duration
        self.task_rx_duration               = duration + self.RX_duration
        self.task_rx.taskDuration           = self.task_rx_duration

    def recompute(self):
        super().recompute()



