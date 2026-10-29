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
class Hardware:
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


    def reset_hardware(self):
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


    def print_components(self):
        sum_energy = 0
        print("-----------------------------------------------------------------")
        print("                        Module summary                           ")
        print("-----------------------------------------------------------------") 
        print ("{:<12} {:<12} {:<12} {:<12} {:<12}  ".format("Component","State","Active [s]","Energy [mJ]","Av. Cur.[uA]"))
        for component in self.get_component_list():
            print ("{:<12} {:<12} {:<12.4f} {:<12.4f} {:<12.7f}  ".format(component.get_name()," ",component.get_activeTime(),component.get_energy(),component.get_average_current()*1000))
            for state in component.state_list:
                sum_energy = sum_energy + state.get_energy()
                print ("{:<12} {:<12} {:<12.4f} {:<12.4f} ".format("     -",state.get_name(),state.get_activeTime(),state.get_energy()))
        print("-----------------------------------------------------------------")      
        print ("{:<12} {:<12} {:<12} {:<12.4f}  {:<6.4f}  {:<4} ".format("Total"," "," ",sum_energy,self.average_power,"[mW]"))
        print("-----------------------------------------------------------------")
        if self.get_isPowered() :  
            print ("{:<12} {:<12} {:<12} {:<12} {:<12}  ".format("PMU","Vin[V]","Vout[V]","Energy [mJ]","Av. Cur.[uA]")) 
            for PMU in self.get_PMU_composition():
                print ("{:<12} {:<12} {:<12.4f} {:<12.4f} {:<12.4f}  ".format(PMU.get_name(),PMU.get_v_in(),PMU.get_v_out(),PMU.get_v_in()*PMU.get_i_in(),1000*PMU.get_i_in()))
            print("-----------------------------------------------------------------")
            print ("{:<12} {:<12} {:<12} {:<12} {:<12}  ".format("Battery","Vin[V]","C[mAh]","I [mJ]","Lifetime[years]")) 
            battery = self.get_Battery()
            print ("{:<12} {:<12} {:<12.4f} {:<12.4f} {:<12.4f}  ".format(battery.get_name(), battery.get_v(), battery.get_capacity_mAh(), battery.get_i(), battery.get_lifetime()))
            print("-----------------------------------------------------------------")



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