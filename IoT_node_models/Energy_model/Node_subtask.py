



#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# Given subtask : part of a task only impliying a single module
#   -Module and state used
#   -Time spent in this state
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
class Node_subtask:
    def __init__(self,name = "None", module = None, moduleState=None, stateDuration=0, useModuleDuration=False):
        self.name          = name
        self.module        = module
        self.moduleState   = moduleState
        self.stateDuration = stateDuration
        self.useModuleDuration = useModuleDuration
        self.energy        = 0
        self.paramVI       = [None,None] #Only required if the subtask changes the state info

    def reset_energy(self):
        self.energy = 0
    
    def get_module(self):
        return self.module
    
    def get_moduleState(self):
        return self.moduleState
    
    def get_stateDuration (self):
        if(self.useModuleDuration) :
            return self.module.get_duration()
        else:
            return self.stateDuration
    
    def get_useModuleDuration(self):
        return self.useModuleDuration
    
    def get_name(self):
        return self.name
    
    def get_energy(self):
        return self.energy
    
    def get_paramVI(self):
        return self.paramVI
    
    def set_module(self, module):
        self.module = module

    
    def set_moduleState(self, moduleState):
        self.moduleState = moduleState
    
    def set_stateDuration (self, stateDuration):
        self.stateDuration = stateDuration
    
    def set_useModuleDuration(self, useModuleDuration):
        self.useModuleDuration = useModuleDuration

    
    def set_param_i(self, i=0):
        self.paramVI[1] = i
    
    def set_param_v(self, v=0):
        self.paramVI[0] = v
    
    def set_name(self, name):
        self.name = name


    def compute_energy(self):
        self.energy = self.get_moduleState().compute_energy(duration = self.get_stateDuration(), paramVI = self.get_paramVI() )
        return self.energy
