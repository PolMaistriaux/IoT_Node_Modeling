#%%
import scipy.interpolate
import numpy as np

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Node_description.Wireless_communication   import LoRa_library as LoRa
from Node_description.Wireless_communication   import Optimal_strategy as optStrat
from Node_description.Hardware      import *
from Node_description.Task import *


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
class LoRa_Hardware(Hardware):
    def __init__(self,name = "None", component_list=[], PMU_composition =[], Battery = None, radio_component = None): 
        super().__init__(name = name, component_list = component_list , PMU_composition = PMU_composition, Battery = Battery)
        self.radio_component      = radio_component

    
    def get_radio(self) :
        return self.radio_component

##############################################################################################
