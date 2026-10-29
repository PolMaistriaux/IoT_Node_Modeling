#%%
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Node_description.State import *
from Node_description.Battery           import *
from Node_description.PMU               import *




#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# Given component of the node described by:
#   -Current consumption in sleep mode
#   -Operating voltage in sleep mode
#   -List of the different component state in which it can operate (sleep is referred a default state)
# Additional variables used:
#   -energy_day   : overall energy consumed by the component over the day
#   -t_active_day : overall time spent in active (not in sleep state) during the day
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
class Node:
    def __init__(self,name = "None", component_list=[], PMU_composition =[], Battery = None): # constructor
        self.name = name
        self.energy = 0
        self.average_power = 0
        self.component_list = component_list

        # Powered node
        self.isPowered = False
        self.PMU_composition = PMU_composition
        self.Battery = Battery
        self.lifetime = 0 
        if not self.check_correctness() :
            return
    
    def get_component_list(self):
        return self.component_list
    
    def get_name(self):
        return self.name
    
    def get_energy(self):
        return self.energy
    
    def get_lifetime(self):
        return self.lifetime
    
    def get_Battery(self):
        return self.Battery
    
    def get_isPowered(self):
        return self.isPowered
    
    def get_PMU_composition(self):
        return self.PMU_composition
    
    def get_Battery(self):
        return self.Battery

    def set_name(self, name):
        self.name = name

    def set_component_list(self, component_list):
        self.component_list = component_list


    def reset_Node(self):
        self.energy = 0
        self.average_power = 0
        for component in self.component_list:
            component.reset_component()



    def compute(self, time_window, verbose = False):
        #################################################################################
        #  For each component, compute the energy it consumes over a single day
        #################################################################################
        self.energy = 0
        for component in self.component_list:
            #Compute the component energy for a single day, considering sleep mode.
            energy = component.compute_energy(time_window)
            self.energy = self.energy + energy
        self.average_power = self.energy/time_window

        if self.isPowered:
            i_battery =0
            for PMU in self.PMU_composition:
                PMU.compute()
                i_battery = i_battery + PMU.get_i_in()
            
            self.Battery.set_i(i_battery)
            self.Battery.compute()
            self.lifetime =self.Battery.get_lifetime()
            if verbose:
                print('Node lifetime is %.1f years. Average current drawn from battery : %.3f [mA]'%(self.Battery.get_lifetime(), self.Battery.get_i() ))




    def check_correctness(self):
        if not self.PMU_composition and self.Battery == None:
            print("Warning : Node is considered not powered")
            self.isPowered = False
            return False
        elif not self.PMU_composition or self.Battery == None:
            raise Exception("Error : : PMU_composition is empty or Battery not specified")
            return False
        
        self.isPowered = True

        for component in self.component_list:
            found = 0
            for PMU in self.PMU_composition:
                if (PMU.v_in != self.Battery.v):
                    print("Error : PMU supply voltage is different from battery voltage")
                    return False
                try:
                    for PMU_component in PMU.component_list:
                        if PMU_component == component :
                            found = 1
                        if found>1:
                            raise Exception("Error : component registered multiples in a PMU or in multiple PMUs")
                            return False
                except:
                    raise Exception("Error : PMU component_list is not properly defined")
                    return False
            if found != 1:
                raise Exception("Error : component %s has no PMU"%component.get_name())
                return False
        return True