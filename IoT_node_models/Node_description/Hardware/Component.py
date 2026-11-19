
#%%
import sys
import os

from .State     import *
from .Footprint import *


#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# Given component of the node described by:
#   -Current consumption in sleep mode
#   -Operating voltage in sleep mode
#   -List of the different component state in which it can operate (sleep is referred a default state)
# Additional variables used:
#   -average_power   : power consumed by the component, averaged over time
#   -average_current : current drawn by the component, averaged over time
#   -duty_cycle      : fraction of time spent in active (not in sleep state)
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
class Component:
    def __init__(self,name = "None", v=0, i_sleep =0, factors=None, category=None): # constructor
        self.name          = name
        self.i_sleep       = i_sleep
        self.v             = v
        self.state_list    = []
        self.sleep_state   = State("Sleep",v = v, i = i_sleep, duration = None)
        # Result of the model computation
        self.average_power   = 0
        self.average_current = 0
        self.duty_cycle      = 0

        self.set_factors(factors)

        self.category = category 
    
    def get_average_power(self):
        return self.average_power
    
    def get_average_current(self):
        return self.average_current
    
    def get_duty_cycle(self):
        return self.duty_cycle
    
    def get_i_sleep(self):
        return self.i_sleep
    
    def get_v(self):
        return self.v
    
    def get_name(self):
        return self.name

    def search_state_name(self,name):
        for state in self.state_list:
            if state.name == name:
                return state

    def set_i_sleep (self, i_sleep):
        self.i_sleep = i_sleep
        self.sleep_state.set_i(i_sleep)
    
    def set_v(self, v):
        """Set the supply voltage and propagate it to the sleep state and all states
        (their current is looked up in the {voltage: current} dictionary if any)."""
        self.v = v
        self.sleep_state.set_v(v)
        for state in self.state_list:
            state.set_v(v)

    def set_name(self, name):
        self.name = name

    def set_factors(self, factors):
        if factors is not None and not isinstance(factors, FootprintVector):
            raise TypeError("factors must be an ImpactVector or None")
        self.factors = factors

    def compute_power(self):
        """Average power of the component. The duty cycle of each state must have been
        registered beforehand (by the Profile); the component sleeps the rest of the time."""
        ##############################################
        # 1 ) Reset the sleep variables
        ##############################################
        # Do not reset the duty cycle of each component state, as they have been updated by the tasks
        self.average_power = 0
        self.sleep_state.reset_state()

        ########################################################
        # 2 ) For each component state, accumulate the power
        ########################################################
        duty_cycle = 0
        for state in self.state_list:
            self.average_power = self.average_power + state.get_average_power()
            duty_cycle         = duty_cycle + state.get_duty_cycle()

        if duty_cycle > 1:
            raise Exception("Error : With task registered, the component %s is busy for more than the time window"%(self.name))

        ########################################################
        # 3 ) Sleep the remaining of the time
        ########################################################
        self.sleep_state.add_duty_cycle(1 - duty_cycle)

        self.duty_cycle      = duty_cycle
        self.average_power   = self.average_power + self.sleep_state.get_average_power()
        self.average_current = self.average_power / self.v if self.v != 0 else 0

        return self.average_power

    
    def add_state(self, state):
        if isinstance(state,State):
            for i,x in enumerate(self.state_list):
                if id(x)==id(state):
                    self.state_list[i]=state
                    return
            state.v = self.v
            self.state_list.append(state)

    def reset_component(self):
        self.average_current = 0
        self.average_power   = 0
        self.duty_cycle      = 0
        self.sleep_state.reset_state()
        for state in self.state_list:
            state.reset_state()
