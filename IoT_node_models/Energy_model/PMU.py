#%%

from Energy_model.Node_module import *

################################
class LDO:
    def __init__(self,name = "None", v_out = 0, i_q = 0, v_in = 0, module_list = []): # constructor
        self.name           = name
        self.i_q            = i_q
        self.v_out          = v_out
        self.v_in           = v_in
        self.i_in           = 0
        self.i_out          = 0
        self.module_list = module_list
        for module in self.module_list:
            if module.get_v() != v_out:
                raise Exception("Module connected to LDO with Vout %.1f as a power supply specified at %.1f"%(self.v_out,module._get_v()))

    def compute(self):
        self.i_out          = 0
        for module in self.module_list:
            self.i_out = self.i_out + module.get_average_current()
        self.i_in = self.i_out +self.i_q
        
    
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

