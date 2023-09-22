


from Energy_model.Node_subtask import *

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# Given task of the node described by:
#   -The list of module used
#   -The list of all modules (to account for sleep power of unused modules)
#   -The list of substasks : different modules states used
#   -The overall task duration : should not exceed the sum all subtasks durations
#   -The task rate : how many times per day is the task performed
#   -List of the different module state in which it can operate (sleep is referred a default state)
# Additional variables used:
#   -energy_task   : energy consumed to perform the task once
#   -energy_task   : energy consumed over the day to perform at the given task rate
#   -moduleActiveTime : keeps track of the times spent by each module in active mode (not sleep)
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
class Node_task:
    def __init__(self,name = "None", node_modules= [], subtasks=[], taskDuration = 0):
        self.name = name
        self.node_modules  = node_modules
        self.moduleActiveTime = [0]*len(node_modules)
        self.subtasks = subtasks
        self.taskDuration  = taskDuration
        self.energy_task   = 0

    def get_energy_task(self):
        return self.energy_task
    
    def get_node_modules(self):
        return self.node_modules
    
    def get_name(self):
        return self.name
    
    def get_taskDuration(self):
        return self.taskDuration
    
    def get_moduleActiveTime(self):
        return self.moduleActiveTime
    

    def set_node_modules(self, node_modules):
        self.node_modules = node_modules
        self.reset_task()

    def set_name(self, name):
        self.name = name

    def set_taskDuration(self, taskDuration):
        self.taskDuration = taskDuration
        self.reset_task()


    def reset_task(self):
        self.energy_task   = 0
        self.moduleActiveTime = [0]*len(self.node_modules)

    def compute_energy_task(self):
        ##############################################
        # 1 ) Reset the different results variables
        ##############################################
        energy = 0
        self.reset_task()
        ##############################################
        # 2 ) For each subtask: compute energy
        ##############################################
        for subtask in self.subtasks:
            # Find related module
            index_module = self.node_modules.index(subtask.get_module())
            # If no subtask duration is specified, try to use the one of the state
            subtaskDuration = subtask.get_stateDuration() 
            if subtaskDuration == None:
                raise Exception("Error : No duration given for this substask (either specified or from module state)") 
            if self.taskDuration < subtaskDuration:
                raise Exception("Error : Duration specified for this task is smaller than active time of single subtask") 
            self.moduleActiveTime[index_module] = self.moduleActiveTime[index_module] + subtaskDuration
            # Update energy of the task 
            energy   = energy + subtask.get_moduleState().compute_energy(duration = subtaskDuration, paramVI = subtask.get_paramVI() )
            

        ##############################################
        # 2 ) For each module, add energy in sleep
        ##############################################
        for index, module in enumerate(self.node_modules):
            energy   = energy + module.get_i_sleep() * module.get_v() * (self.taskDuration - self.moduleActiveTime[index])

        self.energy_task = energy
        return energy


    def find_subtask(self,name):
        for subtask in self.subtasks:
            if subtask.get_name() == name:
                return subtask
        return None