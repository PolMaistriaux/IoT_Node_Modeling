#%%

from .Component import *
from .Footprint import *


#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# Battery, modeled as a Component with a single (Sleep) state:
#   -v                    : battery voltage
#   -capacity_mAh         : battery capacity
#   -i                    : average current drawn from the battery (sum of the PMUs i_in)
#   -selfdischarge_p_year : self-discharge rate [% of capacity per year]
# The Sleep state current is not a fixed parameter: it is set to i, the current drawn
# by the PMUs, so that its power reflects the consumption of the supplied hardware.
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
class Battery(Component):
    def __init__(self,name = "None", v = 0, capacity_mAh = 0, i_load = 1, selfdischarge_p_year = 0, factors=None, category=None): # constructor
        
        self.capacity_mAh           = capacity_mAh
        self.selfdischarge_p_year   = selfdischarge_p_year
        self.selfdischarge_current  = self.capacity_mAh* (self.selfdischarge_p_year /100) /(24*365)
        self.i_load                 = i_load

        super().__init__(name = name, v = v, i_sleep = self.selfdischarge_current , factors = factors, category = category)
        
        self.lifetime               = 0

    def compute_lifetime(self):
        """Battery lifetime [years] from the drawn current and the self-discharge."""
        lifetime_hour = self.capacity_mAh/(self.drawn_current)
        self.lifetime = lifetime_hour/(24*365)
        return self.lifetime

    def compute_power(self):
        """Average power delivered by the battery: it stays in its single Sleep state,
        whose current is i (drawn by the PMUs). Also updates the lifetime."""
        self.sleep_state.reset_state()
        self.sleep_state.add_duty_cycle(1)

        self.duty_cycle      = 0
        self.average_power   = self.sleep_state.get_average_power()
        self.average_current = self.i_sleep 
        
        self.drawn_power   = (self.i_load+self.i_sleep)*self.v
        self.drawn_current = (self.i_load+self.i_sleep)

        self.compute_lifetime()

        return self.drawn_power

    def add_state(self, state):
        raise Exception("Error : Battery only has a Sleep state, additional states cannot be added")

    def reset_component(self):
        super().reset_component()
        self.lifetime = 0

    def get_i_load(self):
        return self.i_load

    def get_capacity_mAh(self):
        return self.capacity_mAh

    def get_selfdischarge_p_year(self):
        return self.selfdischarge_p_year

    def get_lifetime(self):
        return self.lifetime

    def set_i_load(self, i_load):
        """Set the current drawn from the battery (also the Sleep state current)."""
        self.i_load = i_load
        self.drawn_current = self.i_load + self.selfdischarge_current

    def set_capacity_mAh(self, capacity_mAh):
        self.capacity_mAh = capacity_mAh
        self.selfdischarge_current  = self.capacity_mAh* (self.selfdischarge_p_year /100) /(24*365)
        self.set_i_sleep(self.selfdischarge_current)
        self.drawn_current = self.i_load + self.selfdischarge_current

    def set_selfdischarge_p_year(self, selfdischarge_p_year):
        self.selfdischarge_p_year = selfdischarge_p_year
        self.selfdischarge_current  = self.capacity_mAh* (self.selfdischarge_p_year /100) /(24*365)
        self.set_i_sleep(self.selfdischarge_current)
        self.drawn_current = self.i_load + self.selfdischarge_current