



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
    

    def set_module(self, module):
        self.module = module
    
    def set_moduleState(self, moduleState):
        self.moduleState = moduleState
    
    def set_stateDuration (self, stateDuration):
        self.stateDuration = stateDuration
    
    def set_useModuleDuration(self, useModuleDuration):
        self.useModuleDuration = useModuleDuration
    
    def set_name(self, name):
        self.name = name


