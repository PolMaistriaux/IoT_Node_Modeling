#%%
import scipy.interpolate
import numpy as np

import sys
import os

from .Wireless_communication    import LoRa_library as LoRa
from .Wireless_communication    import Optimal_strategy as optStrat
from .Profile     import *
from .Transceiver_task import *


################################
# LoRa_node contains a - radio component
#                      - mcu
#                      - one or multiple other peripherals
#
# Other peripherals have to be registered as done with Profile
# LoRa_node handles calculation of transmission duration and energy based on communication parameters:
#       * SF
#       * CR
#       * P_TX
#       * Header
################################
class LoRa_Profile(Profile):
    def __init__(self,name = "None", time_window=(24*60*60), Proc_action_tx=[], Proc_action_rx=[],RX_state=None,TX_state=None, I_TX=None, P_TX=None): 
        super().__init__(name = name, time_window=time_window)
        self.radio_RX_state         = RX_state
        self.radio_TX_state         = TX_state
        self.proc_action_tx        = Proc_action_tx
        self.proc_action_rx        = Proc_action_rx
        self.I_TX  = I_TX
        self.P_TX  = P_TX

    def create_task_tx(self, name="None", Ptx=0, SF = 7 ,Payload = 100 ,Header = True ,DE = None ,Coding = 1 ,BW = 125e3, TX_rate=1):
        task_tx = LoRa_TX_task(name = name, proc_actions=self.proc_action_tx, state_TX=self.radio_TX_state , I_TX=self.I_TX, P_TX=self.P_TX, Ptx=Ptx, SF = SF ,Payload = Payload ,Header = Header ,DE = DE ,Coding = Coding ,BW = BW  )
        self.add_task(task_tx,TX_rate)
        return task_tx
    
    def create_task_rx(self, name="None", RX_rate=0, RX_duration=0):
        task_rx = RX_task(name = name, proc_actions=self.proc_action_rx, state_RX=self.radio_RX_state, RX_duration=RX_duration)
        self.add_task(task_rx,RX_rate)
        return task_rx



#################################################################################################################################

    ###########################################
    #           TESTING
    ###########################################

if __name__ == '__main__':
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'Component_set'))
    from Component_set.Node_example import *
    node = LoRa_Hardware(name= "IoT Node", component_list= component_List_3V3, MCU_component   = apollo_component_3V3, radio_component = radio_component_3V3)

    node_prof= LoRa_Profile("Profile", node, MCU_active_state = apollo_state_active_3V3, RX_state=radio_state_RX_3V3,TX_state=radio_state_TX_3V3,
                    P_TX= PTX_PABOOST_3V3, I_TX=I_PABoost_3V3, )

    #LoRa_TX_task(name="1st_TX", radio = radio_component_3V3, processor=apollo_component_3V3, state_Processing=apollo_state_active_3V3, I_TX=I_PABoost_3V3, P_TX= PTX_PABOOST_3V3, Ptx = 17,SF=12 ,Coding=1,Header=True,DE = 1,BW = 125e3, Payload = 50)          
    this_task_tx = node_prof.create_task_tx(name="1st_TX",Ptx = 17,SF=12 ,Coding=1,Header=True,DE = 1,BW = 125e3, Payload = 50, TX_rate=24*1)
    this_task_tx.set_radio_parameters(SF=9 ,Coding=1,Header=True,DE = 1,BW = 125e3, Payload = 50) 
    

    this_task_rx = node_prof.create_task_rx(name="1st_RX", RX_rate=2, RX_duration=0.250, i_rx = I_RX_3V3 )

    node_prof.change_task_rate(this_task_rx,10)
    node_prof.change_task_rate(this_task_tx,24*4)
    node_prof.add_task(task_TPHG_3V3,24*12)
    # %%
    node_prof.compute()
    node_prof.print_tasks()
    node_prof.print_components()
    node_prof.plot_power()
