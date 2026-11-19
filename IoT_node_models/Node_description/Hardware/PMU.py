#%%

from .Component import *
from .Footprint import *


#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# Power Management Unit, modeled as a Component with a single (Sleep) state:
#   -v (input voltage, v_in) : supplied by the battery
#   -v_out                   : output voltage, must match the voltage of every supplied component
#   -i_in                    : current drawn at the input, derived from the supplied components
# The Sleep state current is not a fixed parameter: it is set to i_in each time the
# PMU power is computed, so that its power reflects the consumption of its components.
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
class PMU(Component):
    def __init__(self,name = "None", v_out = 0, v_in = 0, component_list = None, factors=None, category=None): # constructor
        super().__init__(name = name, v = v_in, i_sleep = 0, factors = factors, category = category)
        self.v_out          = v_out
        self.i_in           = 0
        self.i_out          = 0
        self.component_list = component_list if component_list is not None else []
        for component in self.component_list:
            if component.get_v() != v_out:
                raise Exception("Module connected to PMU with Vout %.1f as a power supply specified at %.1f"%(self.v_out,component.get_v()))

    def compute_i_out(self):
        """Output current: sum of the average currents of the supplied components."""
        self.i_out = 0
        for component in self.component_list:
            self.i_out = self.i_out + component.get_average_current()
        return self.i_out

    def compute_i_in(self):
        """Input current as a function of the output current (ideal pass-through)."""
        return self.i_out

    def compute_power(self):
        """Average power drawn at the PMU input. The supplied components power must have
        been computed beforehand. The PMU stays in its single Sleep state, at i_in."""
        self.compute_i_out()
        self.i_in = self.compute_i_in()

        p_load = self.i_out * self.v_out
        p_in   = self.i_in  * self.v

        self.sleep_state.reset_state()
        self.sleep_state.add_duty_cycle(1, power=p_in-p_load)

        self.duty_cycle      = 0

        self.average_power   = self.sleep_state.get_average_power()
        self.average_current = self.average_power/ self.v

        self.drawn_power   = self.i_in*self.v
        self.drawn_current = self.i_in

        return self.drawn_power

    def add_state(self, state):
        raise Exception("Error : PMU only has a Sleep state, additional states cannot be added")

    def reset_component(self):
        super().reset_component()
        self.i_in  = 0
        self.i_out = 0

    def get_i_in(self):
        return self.i_in

    def get_v_in(self):
        return self.v

    def get_i_out(self):
        return self.i_out

    def get_v_out(self):
        return self.v_out

    def set_v_in(self, v_in):
        self.set_v(v_in)


################################
class LDO(PMU):
    def __init__(self,name = "None", v_out = 0, i_q = 0, v_in = 0, component_list = None, factors=None, category=None): # constructor
        self.i_q            = i_q
        super().__init__(name = name, v_out = v_out,  v_in = v_in, component_list = component_list, factors=factors, category=category)

    def compute_i_in(self):
        """LDO: input current is the output current plus the quiescent current."""
        return self.i_out + self.i_q

    def get_i_q(self):
        return self.i_q

    def set_i_q(self, i_q):
        self.i_q = i_q
