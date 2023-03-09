#%%
import scipy.interpolate
import numpy as np

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from IoT_node_models.Wireless_communication   import LoRa_library as LoRa
from IoT_node_models.Energy_model.Node import *



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
class LoRa_Node(Node):
    def __init__(self,name = "None", module_list=[], PMU_composition =[], Battery = None, MCU_module = None, radio_module = None): 
        super().__init__(name = name, module_list = module_list , PMU_composition = PMU_composition, Battery = Battery)
        self.MCU_module       = MCU_module
        self.radio_module     = radio_module

    def get_MCU(self) :
        return self.MCU_module
    
    def get_radio(self) :
        return self.radio_module




