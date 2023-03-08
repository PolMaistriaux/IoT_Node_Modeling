



#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# Given subtask : part of a task only impliying a single module
#   -Module and state used
#   -Time spent in this state
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
class Node_subtask:
    def __init__(self,name = "None", module = None, moduleState=None, stateDuration=0):
        self.name = name
        self.module  = module
        self.moduleState = moduleState
        self.stateDuration = stateDuration

