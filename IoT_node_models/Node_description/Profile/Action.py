



#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# Given action : part of a task only impliying a single component
#   -Module and state used
#   -Time spent in this state
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
class Action:
    def __init__(self,name = "None",  componentState=None, stateDuration=0):
        self.name          = name
        self.componentState   = componentState
        self.stateDuration = stateDuration
        self.energy        = 0
        self.param_i       = None

    def reset_energy(self):
        self.energy = 0
    
    def get_componentState(self):
        return self.componentState
    
    def get_stateDuration (self):
        return self.stateDuration
    
    def get_name(self):
        return self.name
    
    def get_energy(self):
        return self.energy
    
    def get_param_i(self):
        return self.param_i
    
    def set_componentState(self, componentState):
        self.componentState = componentState
    
    def set_stateDuration (self, stateDuration):
        self.stateDuration = stateDuration
        
    def set_param_i(self, i=0):
        self.param_i = i
    
    def set_name(self, name):
        self.name = name

    def compute_energy(self):
        """Energy of the action: power of the component state (with optional [v, i] override) times the action duration."""
        self.energy = self.get_componentState().compute_power(current = self.param_i) * self.stateDuration
        return self.energy



class Digital_Processing_Action(Action):
    def __init__(self,name = "None", componentState=None, cycle_count= 0): # constructor
        self.cycle_count     = cycle_count
        try:
            get_cycle = componentState.cycle
        except AttributeError:
            raise Exception("Error: State linked to a Digital_Processing_Action is not a Digital_Processing State")

        super().__init__(name = name, componentState=componentState, stateDuration=self.cycle_count/(componentState.get_freq_MHz()*1e6))


    def set_cycle_count (self, cycle_count):
        self.cycle_count  = cycle_count
        self.stateDuration = self.cycle_count/(self.componentState.get_freq_MHz()*1e6)