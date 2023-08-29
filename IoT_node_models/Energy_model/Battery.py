#%%

from Energy_model.Node_module import *

################################


class Battery:
    def __init__(self,name = "None", v = 0, capacity_mAh = 0, i = 1, selfdischarge_p_year = 0): # constructor
        self.name           = name
        self.v              = v
        self.capacity_mAh   = capacity_mAh
        self.i              = i
        self.selfdischarge_p_year      = selfdischarge_p_year
        self.lifetime = 0
        

    def compute(self):

        selfdischarge_i = self.capacity_mAh * (self.selfdischarge_p_year /100) /(24*365)
        lifetime_hour = self.capacity_mAh/(self.i+selfdischarge_i)
        self.lifetime = lifetime_hour/(24*365)

    def get_i(self):
        return self.i
    
    def get_v(self):
        return self.v
    
    def get_capacity_mAh(self):
        return self.capacity_mAh
    
    def get_selfdischarge_p_year(self):
        return self.selfdischarge_p_year
    
    def get_name(self):
        return self.name
    
    def get_lifetime(self):
        return self.lifetime
    
    
    def set_i(self, i):
        self.i = i

    def set_v(self, v):
        self.v = v

    def set_capacity_mAh(self, capacity_mAh):
        self.capacity_mAh = capacity_mAh
    
    def set_selfdischarge_p_year(self, selfdischarge_p_year):
        self.selfdischarge_p_year = selfdischarge_p_year
    
    def set_name(self, name):
        self.name = name
