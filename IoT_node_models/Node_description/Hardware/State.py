




#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# Given state of a component described by:
#   -i : Current consumption of the component in the state
#   -v : Operating voltage of the component in the state
# Additional variables used:
#   -Duration if it has a fixed one (not mandatory)
#   -energy_day   : variable use to computes the overall energy consumed by employing this state in the current use phase scenario
#   -t_active_day : variable use to computes the overall time spent in this state in the current use phase scenario
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
class State:
    def __init__(self,name = "None", i=0, v=0, duration=None): # constructor
        self.name           = name
        self.i              = i
        self.v              = v
        self.duration       = duration
        # Result of the model computation
        self.energy     = 0
        self.t_active   = 0

    def reset_state (self):
        self.energy   = 0
        self.t_active = 0

    def _resolve_i(self, v=None):
        """Return scalar current. If self.i is a LUT {voltage: current}, look up v
        (defaults to self.v). Raises KeyError when v is not a key in the LUT."""
        if not isinstance(self.i, dict):
            return self.i
        lookup_v = self.v if v is None else v
        if lookup_v not in self.i:
            raise KeyError( f"State '{self.name}': voltage {lookup_v} V not found in current LUT (available voltages: {sorted(self.i)})" )
        return self.i[lookup_v]

    def compute_energy(self,duration, paramVI=[None,None]):
        v_eff = self.v   if paramVI[0] is None else paramVI[0]
        i_eff = self._resolve_i(v_eff) if paramVI[1] is None else paramVI[1]
        return duration * i_eff * v_eff

    def add_active_time(self,state_duration,occurence=1, paramVI=[None,None]):
        this_duration = state_duration *occurence
        self.t_active = self.t_active + this_duration
        self.energy   = self.energy   + self.compute_energy(duration=this_duration,paramVI=paramVI)


    def get_activeTime(self):
        return self.t_active

    def get_energy(self):
        return self.energy

    def get_i(self):
        return self._resolve_i()
    
    def get_v(self):
        return self.v
    
    def get_name(self):
        return self.name
    
    def get_duration(self):
        return self.duration


    def set_activeTime(self, t_active):
        self.t_active = t_active
    
    def set_i (self, i):
        self.i = i
    
    def set_v(self, v):
        self.v = v
    
    def set_name(self, name):
        self.name = name
    
    def set_duration(self, duration):
        self.duration = duration






class Digital_Processing_State(State):
    def __init__(self,name = "None", i_per_MHz=0, freq_MHz=0, v=0, cycle=None): # constructor
        self.freq_MHz  = freq_MHz
        self.i_per_MHz = i_per_MHz
        self.cycle     = cycle
        i_computed = self._compute_i_from_i_per_mhz()
        super().__init__(name = name, i=i_computed, v=v, duration= cycle/(freq_MHz*1e6) if cycle is not None else None)

    def _compute_i_from_i_per_mhz(self):
        """Compute self.i from self.i_per_MHz * self.freq_MHz.
        If i_per_MHz is a dict, return a dict with each value scaled by freq_MHz."""
        if isinstance(self.i_per_MHz, dict):
            return {v: i_per_mhz_val * self.freq_MHz for v, i_per_mhz_val in self.i_per_MHz.items()}
        return self.i_per_MHz * self.freq_MHz

    def set_i_per_MHz (self, i_per_MHz):
        self.i_per_MHz = i_per_MHz
        self.i = self._compute_i_from_i_per_mhz()

    def set_freq_MHz (self, freq_MHz):
        self.freq_MHz = freq_MHz
        self.i = self._compute_i_from_i_per_mhz()

    def set_cycle (self, cycle):
        self.cycle = cycle
        self.duration = self.cycle/(self.freq_MHz*1e6)

    def get_i_per_MHz (self):
        return self.i_per_MHz

    def get_freq_MHz (self):
        return self.freq_MHz

    def get_cycle (self):
        return self.cycle