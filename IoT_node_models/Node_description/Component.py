
#%%
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Node_description.State import *



#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# Given component of the node described by:
#   -Current consumption in sleep mode
#   -Operating voltage in sleep mode
#   -List of the different component state in which it can operate (sleep is referred a default state)
# Additional variables used:
#   -energy_day   : overall energy consumed by the component over the day
#   -t_active_day : overall time spent in active (not in sleep state) during the day
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
class Component:
    def __init__(self,name = "None", v=0, i_sleep =0): # constructor
        self.name          = name
        self.i_sleep       = i_sleep
        self.v             = v
        self.state_list    = []
        self.sleep_state   = State("Sleep",v = v, i = i_sleep, duration = None)
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
        # Do not reset the t_active of each component state, as they have been update by the tasks
        self.energy                   = 0
        self.sleep_state.reset_state()

        ########################################################
        # 2 ) For each component state, compute the energy spent
        ########################################################
        for state in self.state_list:
            # Accumulate overall energy consumed by the component
            self.energy = self.energy + state.get_energy()
            # Calculate time spent in standby/default/sleep mode
            time = time - state.get_activeTime()

        if time <0:
            raise Exception("Error : With task registered, the node is busy for more than a day")  
            return

        ########################################################
        # 3 ) Update the sleep data of the component
        ########################################################  
        self.sleep_state.set_duration(   time)
        self.sleep_state.add_active_time(time)
        sleep_energy = self.sleep_state.get_energy()

        self.t_active        = time_window - time
        self.energy          = self.energy + sleep_energy
        self.average_power   = self.energy/time_window
        self.average_current = self.energy /(self.v * time_window)

        return self.energy

    
    def add_state(self, state):
        if isinstance(state,State):
            for i,x in enumerate(self.state_list):
                if id(x)==id(state):
                    self.state_list[i]=state
                    return
            state.v = self.v
            self.state_list.append(state)

    def reset_component(self):
        self.energy          = 0
        self.average_current = 0
        self.average_power   = 0
        self.t_active        = 0
        self.sleep_state.reset_state()
        self.sleep_state.set_duration(0)
        for state in self.state_list:
            state.reset_state()
