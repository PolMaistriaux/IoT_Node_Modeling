


from .Action import *

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# Given task of the node described by:
#   -The list of component used
#   -The list of all components (to account for sleep power of unused components)
#   -The list of substasks : different components states used
#   -The overall task duration : should not exceed the sum all actions durations
#   -The task rate : how many times per day is the task performed
#   -List of the different component state in which it can operate (sleep is referred a default state)
# Additional variables used:
#   -energy_task   : energy consumed to perform the task once
#   -energy_task   : energy consumed over the day to perform at the given task rate
#   -componentActiveTime : keeps track of the times spent by each component in active mode (not sleep)
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
class Task:
    def __init__(self,name = "None", actions=[], taskDuration = 0):
        self.name = name
        self.actions = actions
        self.taskDuration_isSet    = (taskDuration!=0)
        self.taskDuration_set      = taskDuration
        self.taskDuration_computed = 0
        self.energy_task   = 0

    def get_energy_task(self):
        return self.energy_task
    
    def get_name(self):
        return self.name
    
    def get_taskDuration(self):
        if self.taskDuration_isSet:
            return self.taskDuration_set
        else:
            return self.taskDuration_computed
    
    def set_name(self, name):
        self.name = name

    def set_taskDuration(self, taskDuration):
        self.taskDuration_set      = taskDuration
        self.taskDuration_isSet    = True
        self.reset_task()
    
    def set_compute_taskDuration(self):
        self.taskDuration_set      = 0
        self.taskDuration_isSet    = False
        self.taskDuration_computed = 0
        self.reset_task()


    def reset_task(self):
        for action in self.actions:
            action.reset_energy()
        self.energy_task   = 0
        self.taskDuration_computed = 0

    def compute_energy_task(self):
        ##############################################
        # 1 ) Reset the different results variables
        ##############################################
        energy = 0
        self.reset_task()
        ##############################################
        # 2 ) For each action: compute energy
        ##############################################
        for action in self.actions:
            # If no action duration is specified, try to use the one of the state
            actionDuration = action.get_stateDuration() 
            if actionDuration == None:
                raise Exception("Error : No duration given for this substask (either specified or from component state)") 
            if self.taskDuration_isSet and (self.taskDuration_set < actionDuration):
                raise Exception("Error : Duration specified for this task is smaller than active time of single action") 
            self.taskDuration_computed = self.taskDuration_computed + actionDuration
            # Update energy of the task 
            energy   = energy + action.compute_energy( )
            

        self.energy_task = energy
        return energy


    def find_action(self,name):
        for action in self.actions:
            if action.get_name() == name:
                return action
        return None


class Sleep_Task(Task):
    def __init__(self, components= []):
        self.components = components
        super().__init__(name = "Sleep")


    def compute_energy_task(self):
        for i, comp in enumerate(self.components):
            self.energy_task += comp.sleep_state.get_energy()
        return self.energy_task

