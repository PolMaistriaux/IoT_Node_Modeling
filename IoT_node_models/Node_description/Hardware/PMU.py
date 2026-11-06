#%%

from .Component import *
from .Footprint import *

################################
class PMU:
    def __init__(self,name = "None", v_out = 0, v_in = 0, component_list = [], factors=None, category=None): # constructor
        self.name           = name
        self.v_out          = v_out
        self.v_in           = v_in
        self.i_in           = 0
        self.i_out          = 0
        self.component_list = component_list
        for component in self.component_list:
            if component.get_v() != v_out:
                raise Exception("Module connected to PMU with Vout %.1f as a power supply specified at %.1f"%(self.v_out,component._get_v()))

        self.set_factors(factors)
        
        self.category = category

    def compute(self):
        self.i_out          = 0
        for component in self.component_list:
            self.i_out = self.i_out + component.get_average_current()
        self.i_in = self.i_out 
        
    
    def set_factors(self, factors):
        if factors is not None and not isinstance(factors, FootprintVector):
            raise TypeError("factors must be an ImpactVector or None")
        self.factors = factors

    def get_i_in(self):
        return self.i_in
    
    def get_v_in(self):
        return self.v_in
    
    def get_i_out(self):
        return self.i_out
    
    def get_v_out(self):
        return self.v_out
    
    def get_name(self):
        return self.name


################################
class LDO(PMU):
    def __init__(self,name = "None", v_out = 0, i_q = 0, v_in = 0, component_list = [], factors=None, category=None): # constructor
        self.i_q            = i_q
        super().__init__(name = name, v_out = v_out,  v_in = v_in, component_list = component_list, factors=factors, category=category)

    def compute(self):
        self.i_out          = 0
        for component in self.component_list:
            self.i_out = self.i_out + component.get_average_current()
        self.i_in = self.i_out +self.i_q
        
    

