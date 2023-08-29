
#%%
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Energy_model.Node_module_state import *



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
        self.energy          = 0
        self.average_power   = 0
        self.average_current = 0
        self.t_active        = 0
    
    def get_energy(self):
        return self.energy
    
    def get_average_power(self):
        return self.average_power
    
    def get_average_current(self):
        return self.average_current
    
    def get_activeTime(self):
        return self.t_active
    
    def get_i_sleep(self):
        return self.i_sleep
    
    def get_v(self):
        return self.v
    
    def get_name(self):
        return self.name
    

    def set_i_sleep (self, i_sleep):
        self.i_sleep = i_sleep
    
    def set_v(self, v):
        self.v = v
    
    def set_name(self, name):
        self.name = name
    
        
    def compute_energy(self, time_window):
        time = time_window
        ##############################################
        # 1 ) Reset the different sleep variables
        ##############################################
        # Do not reset the t_active of each module state, as they have been update by the tasks
        self.energy                   = 0
        self.sleep_state.reset_Module_state()

        ########################################################
        # 2 ) For each module state, compute the energy spent
        ########################################################
        for state in self.state_list:
            state.compute_energy()
            # Accumulate overall energy consumed by the module
            self.energy = self.energy + state.get_energy()
            # Calculate time spent in standby/default/sleep mode
            time = time - state.get_activeTime()

        if time <0:
            raise Exception("Error : With task registered, the node is busy for more than a day")  
            return

        ########################################################
        # 3 ) Update the sleep data of the module
        ########################################################  
        self.sleep_state.set_duration(   time)
        self.sleep_state.add_active_time(time)
        sleep_energy = self.sleep_state.compute_energy()

        self.t_active        = time_window - time
        self.energy          = self.energy + sleep_energy
        self.average_power   = self.energy/time_window
        self.average_current = self.energy /(self.v * time_window)

        return self.energy

    
    def add_state(self, module_state):
        if isinstance(module_state,Module_state):
            for x in self.state_list:
                if x.name==module_state.get_name():
                    raise Exception("Error : Trying to add a state that is already part of the module states list") 
                    return
            module_state.v = self.v
            self.state_list.append(module_state)

    def reset_module(self):
        self.energy          = 0
        self.average_current = 0
        self.average_power   = 0
        self.t_active        = 0
        self.sleep_state.reset_Module_state()
        self.sleep_state.set_duration(0)
        for module_state in self.state_list:
            module_state.reset_Module_state()
