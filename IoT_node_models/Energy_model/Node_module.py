
#%%
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from IoT_node_models.Energy_model.Node_module_state import *



#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# Given module of the node described by:
#   -Current consumption in sleep mode
#   -Operating voltage in sleep mode
#   -List of the different module state in which it can operate (sleep is referred a default state)
# Additional variables used:
#   -energy_day   : overall energy consumed by the module over the day
#   -t_active_day : overall time spent in active (not in sleep state) during the day
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
class Node_module:
    def __init__(self,name = "None", v=0, i_sleep =0): # constructor
        self.name          = name
        self.i_sleep       = i_sleep
        self.v             = v
        self.state_list    = []
        self.sleep_state   = Module_state("Sleep",v = v, i = i_sleep, duration = None)
        self.state_list.append(self.sleep_state)
        # Result of the model computation
        self.energy_day      = 0
        self.average_current = 0
        self.t_active_day    = 0
        
    def compute_energy_day(self):
        time = 24*60*60
        ##############################################
        # 1 ) Reset the different sleep variables
        ##############################################
        # Do not reset the t_active of each module state, as they have been update by the tasks
        self.energy_day               = 0
        self.sleep_state.duration     = 0
        self.sleep_state.t_active_day = 0
        self.sleep_state.energy       = 0

        ########################################################
        # 2 ) For each module state, compute the energy spent
        ########################################################
        for state in self.state_list:
            state.compute_energy_day()
            # Accumulate overall energy consumed by the module
            self.energy_day = self.energy_day + state.energy_day
            # Calculate time spent in standby/default/sleep mode
            time = time - state.t_active_day

        if time <0:
            raise Exception("Error : With task registered, the node is busy for more than a day")  
            return

        ########################################################
        # 3 ) Update the sleep data of the module
        ########################################################  
        sleep_energy = time*self.v*self.i_sleep
        self.sleep_state.duration     = time
        self.sleep_state.t_active_day = time
        self.sleep_state.energy_day   = sleep_energy
        self.t_active_day = 24*60*60 - time
        self.energy_day = self.energy_day + sleep_energy
        return self.energy_day

    
    def add_state(self, module_state):
        if isinstance(module_state,Module_state):
            for x in self.state_list:
                if x.name==module_state.name:
                    raise Exception("Error : Trying to add a state that is already part of the module states list") 
                    return
            module_state.v = self.v
            self.state_list.append(module_state)

    def reset_module(self):
        self.energy_day     = 0
        self.average_current = 0
        self.t_active_day    = 0
        self.sleep_state.duration   = 0
        self.sleep_state.energy_day = 0
        self.sleep_state.duration   = 0
        for module_state in self.state_list:
            module_state.t_active_day = 0
            module_state.energy_day = 0
