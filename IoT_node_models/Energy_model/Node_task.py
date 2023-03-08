


from IoT_node_models.Energy_model.Node_subtask import *

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
    def __init__(self,name = "None", node_modules= [], subtasks=[], taskDuration = 0, task_rate =0):
        self.name = name
        self.node_modules  = node_modules
        self.moduleActiveTime = [0]*len(node_modules)
        self.subtasks = subtasks
        self.taskDuration  = taskDuration
        self.energy_task   = 0
        self.energy_day    = 0
        self.task_rate     = task_rate


    def compute_energy_task(self):
        ##############################################
        # 1 ) Reset the different results variables
        ##############################################
        energy = 0
        self.energy_task   = 0
        self.energy_day    = 0
        self.moduleActiveTime = [0]*len(self.node_modules)
        ##############################################
        # 2 ) For each subtask: compute energy
        ##############################################
        for subtask in self.subtasks:
            # Find related module
            index_module = self.node_modules.index(subtask.module)
            # If no subtask duration is specified, try to use the one of the state
            subtaskDuration = (subtask.stateDuration if subtask.stateDuration != None else subtask.moduleState.duration)
            if subtaskDuration == None:
                raise Exception("Error : No duration given for this substask (either specified or from module state)") 
            if self.taskDuration < subtaskDuration:
                raise Exception("Error : Duration specified for this task is smaller than active time of single subtask") 
            # Update module active time
            self.moduleActiveTime[index_module] = self.moduleActiveTime[index_module] + subtaskDuration
            # Update active time of the state
            subtask.moduleState.add_active_time_day(subtaskDuration,self.task_rate)
            # Update energy of the task 
            energy   = energy + subtask.module.v * subtask.moduleState.i *subtaskDuration

        ##############################################
        # 2 ) For each module, add energy in sleep
        ##############################################
        for index, module in enumerate(self.node_modules):
            energy   = energy + module.i_sleep*module.v*(self.taskDuration - self.moduleActiveTime[index])

        self.energy_task = energy
        return energy


    def compute_energy_day(self):
        self.compute_energy_task()
        self.energy_day = self.energy_task*self.task_rate

    def find_subtask(self,name):
        for subtask in self.subtasks:
            if subtask.name == name:
                return subtask
        return None