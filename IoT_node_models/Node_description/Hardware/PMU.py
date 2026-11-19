#%%

from .Component import *
from .Footprint import *


#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# Power Management Unit, modeled as a Component with two always-on states:
#   -Sleep : quiescent consumption of the PMU (i_q at v_in), independent of the load
#   -Loss  : conversion losses, i.e. the input power not delivered to the load nor
#            consumed as quiescent power (p_in - p_load - p_quiescent)
# Parameters:
#   -v (input voltage, v_in) : supplied by the battery
#   -v_out                   : output voltage, must match the voltage of every supplied component
#   -i_q                     : quiescent current, drawn at the input
#   -i_in                    : current drawn at the input, derived from the supplied components
# The Loss state power is not a fixed parameter: it is updated each time the PMU power
# is computed, so that it reflects the consumption of the supplied components.
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
class PMU(Component):
    def __init__(self,name = "None", v_out = 0, v_in = 0, i_q = 0, component_list = None, factors=None, category=None): # constructor
        super().__init__(name = name, v = v_in, i_sleep = i_q, factors = factors, category = category)
        self.i_q            = i_q
        self.v_out          = v_out
        self.i_in           = 0
        self.i_out          = 0
        self.quiescent_power = 0
        self.loss_power      = 0
        self.drawn_power     = 0
        self.drawn_current   = 0
        # Conversion losses state (the Sleep state holds the quiescent consumption)
        self.loss_state     = State("Loss", v = v_in, i = 0, duration = None)
        self.state_list.append(self.loss_state)

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
        """Input current as a function of the output current (ideal pass-through + quiescent)."""
        return self.i_out + self.i_q

    def compute_power(self):
        """Average power drawn at the PMU input. The supplied components power must have
        been computed beforehand. The PMU is always in both its Sleep (quiescent) and
        Loss (conversion losses) states."""
        self.compute_i_out()
        self.i_in = self.compute_i_in()

        p_load = self.i_out * self.v_out
        p_in   = self.i_in  * self.v

        # Quiescent consumption: Sleep state, always on
        self.sleep_state.reset_state()
        self.sleep_state.add_duty_cycle(1)
        self.quiescent_power = self.sleep_state.get_average_power()

        # Conversion losses: Loss state, always on
        self.loss_state.reset_state()
        self.loss_state.add_duty_cycle(1, power = max(0,p_in - p_load - self.quiescent_power))
        self.loss_power = self.loss_state.get_average_power()

        self.duty_cycle      = 0

        # Overall PMU overhead (quiescent + losses)
        self.average_power   = self.quiescent_power + self.loss_power
        self.average_current = self.average_power / self.v if self.v != 0 else 0

        self.drawn_power   = p_in
        self.drawn_current = self.i_in

        return self.drawn_power

    def add_state(self, state):
        raise Exception("Error : PMU only has a Sleep (quiescent) and a Loss state, additional states cannot be added")

    def reset_component(self):
        super().reset_component()
        self.i_in  = 0
        self.i_out = 0
        self.quiescent_power = 0
        self.loss_power      = 0

    def get_i_in(self):
        return self.i_in

    def get_v_in(self):
        return self.v

    def get_i_out(self):
        return self.i_out

    def get_v_out(self):
        return self.v_out

    def get_i_q(self):
        return self.i_q

    def get_quiescent_power(self):
        return self.quiescent_power

    def get_loss_power(self):
        return self.loss_power

    def set_v_in(self, v_in):
        self.set_v(v_in)

    def set_i_q(self, i_q):
        self.i_q = i_q
        self.set_i_sleep(i_q)


################################
class LDO(PMU):
    def __init__(self,name = "None", v_out = 0, i_q = 0, v_in = 0, component_list = None, factors=None, category=None): # constructor
        super().__init__(name = name, v_out = v_out,  v_in = v_in, i_q = i_q, component_list = component_list, factors=factors, category=category)

    def compute_i_in(self):
        """LDO: input current is the output current plus the quiescent current."""
        return self.i_out + self.i_q
