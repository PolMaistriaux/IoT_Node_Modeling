#%%
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Energy_model.Node_module_state import *
from Energy_model.Battery           import *
from Energy_model.PMU               import *




#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# Given module of the node described by:
#   -Current consumption in sleep mode
#   -Operating voltage in sleep mode
#   -List of the different module state in which it can operate (sleep is referred a default state)
# Additional variables used:
#   -energy_day   : overall energy consumed by the module over the day
#   -t_active_day : overall time spent in active (not in sleep state) during the day
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
class Node:
    def __init__(self,name = "None", module_list=[], PMU_composition =[], Battery = None): # constructor
        self.name = name
        self.energy = 0
        self.average_power = 0
        self.module_list = module_list

        # Powered node
        self.isPowered = False
        self.PMU_composition = PMU_composition
        self.Battery = Battery
        self.lifetime = 0 
        if not self.check_correctness() :
            return
    
    def get_module_list(self):
        return self.module_list
    
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

    def set_module_list(self, module_list):
        self.module_list = module_list


    def reset_Node(self):
        self.energy = 0
        self.average_power = 0
        for module in self.module_list:
            module.reset_module()



    def compute(self, time_window, verbose = False):
        #################################################################################
        #  For each module, compute the energy it consumes over a single day
        #################################################################################
        self.energy = 0
        for module in self.module_list:
            #Compute the module energy for a single day, considering sleep mode.
            energy = module.compute_energy(time_window)
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

        for module in self.module_list:
            found = 0
            for PMU in self.PMU_composition:
                if (PMU.v_in != self.Battery.v):
                    print("Error : PMU supply voltage is different from battery voltage")
                    return False
                try:
                    for PMU_module in PMU.module_list:
                        if PMU_module == module :
                            found = 1
                        if found>1:
                            raise Exception("Error : module registered multiples in a PMU or in multiple PMUs")
                            return False
                except:
                    raise Exception("Error : PMU module_list is not properly defined")
                    return False
            if found != 1:
                raise Exception("Error : module %s has no PMU"%module.get_name())
                return False
        return True