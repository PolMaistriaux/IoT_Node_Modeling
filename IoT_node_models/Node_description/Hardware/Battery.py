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
    def __init__(self,name = "None", v = 0, capacity_mAh = 0, i = 1, selfdischarge_p_year = 0, factors=None, category=None): # constructor
        super().__init__(name = name, v = v, i_sleep = i, factors = factors, category = category)
        self.capacity_mAh           = capacity_mAh
        self.selfdischarge_p_year   = selfdischarge_p_year
        self.lifetime               = 0
        self.set_i(i)

    def compute_lifetime(self):
        """Battery lifetime [years] from the drawn current and the self-discharge."""
        selfdischarge_i = self.capacity_mAh * (self.selfdischarge_p_year /100) /(24*365)
        lifetime_hour = self.capacity_mAh/(self.i+selfdischarge_i)
        self.lifetime = lifetime_hour/(24*365)
        return self.lifetime

    def compute_power(self):
        """Average power delivered by the battery: it stays in its single Sleep state,
        whose current is i (drawn by the PMUs). Also updates the lifetime."""
        self.sleep_state.reset_state()
        self.sleep_state.add_duty_cycle(1)

        self.duty_cycle      = 0
        self.average_power   = self.sleep_state.get_average_power()
        self.average_current = self.i
        self.compute_lifetime()
        return self.average_power

    def add_state(self, state):
        raise Exception("Error : Battery only has a Sleep state, additional states cannot be added")

    def reset_component(self):
        super().reset_component()
        self.lifetime = 0

    def get_i(self):
        return self.i

    def get_capacity_mAh(self):
        return self.capacity_mAh

    def get_selfdischarge_p_year(self):
        return self.selfdischarge_p_year

    def get_lifetime(self):
        return self.lifetime

    def set_i(self, i):
        """Set the current drawn from the battery (also the Sleep state current)."""
        self.i = i
        self.set_i_sleep(i)

    def set_capacity_mAh(self, capacity_mAh):
        self.capacity_mAh = capacity_mAh

    def set_selfdischarge_p_year(self, selfdischarge_p_year):
        self.selfdischarge_p_year = selfdischarge_p_year
