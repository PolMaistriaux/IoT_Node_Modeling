#%%

from IoT_node_models.Energy_model.Energy_node import *

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
                print("Module connected to LDO with Vout %.1f as a power supply specified at %.1f"%(self.v_out,module._get_v()))

    def recompute(self):
        self.i_out          = 0
        for module in self.module_list:
            self.i_out = self.i_out + module.get_average_current()
        self.i_in = self.i_out +self.i_q
    
class Battery:
    def __init__(self,name = "None", v = 0, capacity_mAh = 0, i = 1, selfdischarge_p_year = 0): # constructor
        self.name           = name
        self.v              = v
        self.capacity_mAh   = capacity_mAh
        self.i              = i
        self.selfdischarge_p_year      = selfdischarge_p_year
        


    def recompute(self):

        selfdischarge_i = self.capacity_mAh * (self.selfdischarge_p_year /100) /(24*365)
        lifetime_hour = self.capacity_mAh/(self.i+selfdischarge_i)
        self.lifetime = lifetime_hour/(24*365)

################################

class Node(Node_profile):
    def __init__(self,name = "None", module_list = [], PMU_composition =[], Battery = None): 
        super().__init__(name = name, module_list = module_list)
        self.PMU_composition = PMU_composition
        self.Battery = Battery
        self.lifetime = 0

    def check_correctness(self):
        if not self.PMU_composition or self.Battery == None:
            print("Warning : PMU_composition is empty or Battery not specified")
            return False
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
                            print("Error : module registered multiples in a PMU or in multiple PMUs")
                            return False
                except:
                    print("Error : PMU module_list is not properly defined")
                    return False
            if found != 1:
                print("Error : module %s has no PMU"%module.get_name())
                return False
        return True

    def recompute(self,verbose= False):
        super().recompute()
        if not self.check_correctness() :
            return
        i_battery =0
        for PMU in self.PMU_composition:
            PMU.recompute()
            i_battery = i_battery + PMU.i_in
        
        self.Battery.i = i_battery
        self.Battery.recompute()
        self.lifetime =self.Battery.lifetime
        if verbose:
            print('Node lifetime is %.1f years. Average current drawn from battery : %.3f [mA]'%(self.Battery.lifetime,self.Battery.i ))


