#%%
import numpy as np
from matplotlib import patches as mpatches


from ..Hardware.Component import *
from .Task   import *
from ..Hardware        import *


import sys
import os
from ...MyColors           import *

###################################################################################################
# INFORMATION
###################################################################################################
#
# The modeling done here is made over a day but it is purely arbitrary
#
###################################################################################################




#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# Given node profile described by:
#   -The list of component used
#   -The list of tasks performed
#   -The time window over which the task rates are expressed (executions per time window)
# Additional variables used:
#   -average_power : power consumed by performing the tasks, averaged over time
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
class Profile:
    def __init__(self,name = "None", time_window=(24*60*60)): # constructor
        if not isinstance(time_window, (int, float)) or time_window <= 0:
            raise TypeError("Error : time_window must be a positive number of seconds, got %s"%type(time_window))
        self.name = name
        self.task_list      = []
        self.task_rate_list = []
        self.time_window   = time_window
        self.average_power = 0

    def reset_profile(self):
        self.average_power = 0
        for task in self.task_list:
            task.reset_task()


    def set_taskList(self,taskList,taskRates):
        self.task_list      = taskList
        self.task_rate_list = taskRates
        self.reset_profile()

    def get_task_rate(self,task):
        try:
            index_task = self.task_list.index(task)
            return self.task_rate_list[index_task]
        except ValueError:
            raise Exception("Error: task for which task rate must be found  is not part of the node tasks")

    def change_task_rate(self,task,task_rate):
        try:
            index_task = self.task_list.index(task)
            self.task_rate_list[index_task] =task_rate
        except ValueError:
            raise Exception("Error: task for which task rate must be updated is not part of the node tasks")
        


    def add_task(self, task,task_rate):
        if isinstance(task,Task):
            for x in self.task_list:
                if x.name == task.get_name():
                    raise Exception("Error : Trying to add a task that is already part of the tasks list") 
            self.task_list.append(task)
            self.task_rate_list.append(task_rate)
        else:
            raise TypeError("Error : a variable type different than task was provided to add_task")


    def remove_task(self, task):
        if isinstance(task,Task):
            try:
                self.task_list.remove(task)
                self.reset_profile()
            except:
                raise Exception("Error : Trying to remove a task from the node that it does not perform") 
        else:
            raise TypeError("Error : a variable type different than task was provided to add_task")



    def compute(self):

        ####################################
        # 1 ) Reset the different variables
        ####################################
        self.reset_profile()
        #################################################################################
        # 2 ) For each task, compute the energy consumed to perform it once and convert
        #     it into an average power using the task rate (executions per time window)
        #################################################################################
        for task_index, task in enumerate(self.task_list):
            task_rate = self.task_rate_list[task_index]
            task.compute_energy_task()
            self.average_power = self.average_power + task.get_energy_task() * task_rate / self.time_window

            # Update the duty cycle of the component states used by each action
            for action in task.actions:
                duty_cycle = action.get_stateDuration() * task_rate / self.time_window
                (action.get_componentState()).add_duty_cycle(duty_cycle, paramVI = action.get_paramVI() )

        return self.average_power

    def get_average_power(self):
        return self.average_power

    def get_time_window(self):
        return self.time_window

    def set_time_window(self, time_window):
        self.time_window = time_window
        self.reset_profile()


    def print_tasks(self, additional_tasks=None,additional_task_rates=None):
        if (additional_tasks is not None) and (additional_task_rates is not None):
            print_list = self.task_list      + additional_tasks
            task_rates = self.task_rate_list + additional_task_rates 
            average_power = 0
            for task_index,task in enumerate(print_list):
                average_power += task.get_energy_task() *task_rates[task_index] / self.time_window

        else :
            print_list=self.task_list
            task_rates =self.task_rate_list
            average_power = self.average_power

        print("-------------------------------------------------")
        print("            Tasks summary                        ")
        print("-------------------------------------------------")
        print ("{:<12} {:<8} {:<2} ".format( "Task name"," "," :"), end="")
        for task in print_list:
            print("{:<15}".format(task.get_name()),end="")
        print("")
        print ("{:<12} {:<8} {:<2} ".format( "Rate","[1/tw]"," :"), end="")
        for task_index,task in enumerate(print_list):
            print("{:<15}".format(task_rates[task_index]),end="")
        print("")
        print ("{:<12} {:<8} {:<2} ".format("Energy", "[mJ/t]"," :"), end="")
        for task_index,task in enumerate(print_list):
            print("{:<15}".format(task.get_energy_task()),end="")
        print("")  
        print ("{:<12} {:<8} {:<2} ".format("Tot. en./tw", "[mJ]"," :"), end="")
        for task_index,task in enumerate(print_list):
            print("{:<15.4f}".format(task.get_energy_task() *task_rates[task_index]),end="")
        print("")
        print ("{:<12} {:<8} {:<2} ".format("Tot. durat.", "[s]"," :"), end="")
        for task_index,task in enumerate(print_list):
            print("{:<15.4f}".format(task.get_taskDuration()*task_rates[task_index]),end="")
        print("")  
        print ("{:<12} {:<8} {:<2} {:<15.6f} ".format("Av. power", "[mW]"," :",average_power))
        print("-------------------------------------------------")











        

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%    
  

