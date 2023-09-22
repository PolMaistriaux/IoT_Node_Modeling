




#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# Given state of a module described by:
#   -i : Current consumption of the module in the state
#   -v : Operating voltage of the module in the state
# Additional variables used:
#   -Duration if it has a fixed one (not mandatory)
#   -energy_day   : variable use to computes the overall energy consumed by employing this state in the current use phase scenario
#   -t_active_day : variable use to computes the overall time spent in this state in the current use phase scenario
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
class Module_state:
    def __init__(self,name = "None", i=0, v=0, duration=None): # constructor
        self.name           = name
        self.i              = i
        self.v              = v
        self.duration       = duration
        # Result of the model computation
        self.energy     = 0
        self.t_active   = 0

    def reset_Module_state (self):
        self.energy   = 0
        self.t_active = 0

    def compute_energy(self,duration, paramVI=[None,None]):
        return duration*(self.i if (paramVI[1] is None) else paramVI[1]) * (self.v if (paramVI[0] is None) else paramVI[0])
    
    def add_active_time(self,state_duration,occurence=1, paramVI=[None,None]):
        this_duration = state_duration *occurence
        self.t_active = self.t_active + this_duration
        self.energy   = self.energy   + self.compute_energy(duration=this_duration,paramVI=paramVI)


    def get_activeTime(self):
        return self.t_active
    
    def get_energy(self):
        return self.energy
    
    def get_i (self):
        return self.i
    
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

    
