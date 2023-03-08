




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
        self.energy_day     = 0
        self.t_active_day   = 0

    def compute_energy_day(self):
        self.energy_day = self.t_active_day * self.i * self.v
    
    def add_active_time_day(self,state_duration,occurence):
        self.t_active_day = self.t_active_day +state_duration *occurence