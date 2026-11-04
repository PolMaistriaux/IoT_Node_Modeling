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
# Additional variables used:
#   -energy_day    : energy consumed over the day
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
class Profile:
    def __init__(self,name = "None", time_window=(24*60*60)): # constructor
        self.name = name
        self.task_list      = []
        self.task_rate_list = []
        self.time_window   = time_window
        self.energy        = 0

    def reset_profile(self):
        self.energy        = 0
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
        # 2 ) For each task, compute the energy consumes to perform it over a single day
        #################################################################################
        for task_index, task in enumerate(self.task_list):
            task.compute_energy_task()
            #Accumulate the energy of each tasks to compute the total in active
            self.energy = self.energy + (task.get_energy_task() * self.task_rate_list[task_index])

            # Update the time spent in the different state for each component
            for action in task.actions:
                (action.get_componentState()).add_active_time(action.stateDuration,self.task_rate_list[task_index], paramVI = action.get_paramVI() )

        return self.energy


    def print_tasks(self, additional_tasks=None,additional_task_rates=None):
        if (additional_tasks is not None) and (additional_task_rates is not None):
            print_list = self.task_list      + additional_tasks
            task_rates = self.task_rate_list + additional_task_rates 
            energy = 0
            for task_index,task in enumerate(print_list):
                energy += task.get_energy_task() *task_rates[task_index]

        else :
            print_list=self.task_list
            energy = self.energy

        print("-------------------------------------------------")
        print("            Tasks summary                        ")
        print("-------------------------------------------------")
        print ("{:<12} {:<6} {:<2} ".format( "Task name"," "," :"), end="")
        for task in print_list:
            print("{:<15}".format(task.get_name()),end="")
        print("")
        print ("{:<12} {:<6} {:<2} ".format( "Times/day","[1/d]"," :"), end="")
        for task_index,task in enumerate(print_list):
            print("{:<15}".format(task_rates[task_index]),end="")
        print("")
        print ("{:<12} {:<6} {:<2} ".format("Tot. durat.", "[s]"," :"), end="")
        for task_index,task in enumerate(print_list):
            print("{:<15.4f}".format(task.get_taskDuration()*task_rates[task_index]),end="")
        print("")  
        print ("{:<12} {:<6} {:<2} ".format("Tot. en./d", "[mJ]"," :"), end="")
        for task_index,task in enumerate(print_list):
            print("{:<15.4f}".format(task.get_energy_task() *task_rates[task_index]),end="")
        print("")  
        print ("{:<12} {:<6} {:<2} {:<15.4f} ".format("Node en./d", "[mJ]"," :",energy))
        print("-------------------------------------------------")











        

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%    
  

