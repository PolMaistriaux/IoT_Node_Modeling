


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
    def __init__(self,name = "None", node_modules= [], moduleUsed = [], subtasks=[], taskDuration = 0, task_rate =0):
        self.name = name
        self.node_modules  = node_modules
        self.moduleUsed  = moduleUsed
        self.moduleActiveTime = [0]*len(moduleUsed)
        self.subtasks = subtasks
        self.taskDuration = taskDuration
        self.energy_task   = 0
        self.energy_day    = 0
        self.task_rate = task_rate


    def compute_energy_task(self):
        energy = 0
        self.moduleActiveTime = [0]*len(self.moduleUsed)
        for subtask in self.subtasks:
            index_module = self.moduleUsed.index(subtask.module)
            subtaskDuration = (subtask.stateDuration if subtask.stateDuration != None else subtask.moduleState.duration)
            self.moduleActiveTime[index_module] = self.moduleActiveTime[index_module] + subtaskDuration
            subtask.moduleState.add_active_time_day(subtaskDuration,self.task_rate)

            energy   = energy + subtask.module.v * subtask.moduleState.i *subtaskDuration

            if self.taskDuration < subtaskDuration:
                print("Duration specified for this task is smaller than active time of single subtask : duration = %.2f, subtask active time = %.2f"%(subtaskDuration,self.taskDuration))
        for module in self.node_modules:
            try:
                index_module = self.moduleUsed.index(module)
                energy   = energy + module.i_sleep*module.v*(self.taskDuration - self.moduleActiveTime[index_module])
            except ValueError:
                energy = energy+ module.i_sleep*module.v*self.taskDuration

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