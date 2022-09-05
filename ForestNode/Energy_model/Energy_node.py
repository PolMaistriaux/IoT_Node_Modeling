#%%
from matplotlib import pyplot as plt
import matplotlib.pyplot as plt
plt.rcParams['figure.facecolor'] = 'white'
import math
import numpy as np
import inspect
import plotly.graph_objects as go
import plotly.express as px
import plotly.io as pio
pio.renderers.default = "svg"
from plotly.offline import plot

import sys
import os
file_path = os.path.abspath(__file__)
parent_dir_path         = os.path.dirname(os.path.dirname(file_path))
path_to_import_mainDir  = os.path.dirname(parent_dir_path)

sys.path.append(path_to_import_mainDir)
from MyColors           import *



#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
class Module_state:
    def __init__(self,name = "None", i=0, v=0, duration=None): # constructor
        self.name           = name
        self.i_active       = i
        self.v              = v
        self.duration       = duration
        self.energy_day     = 0
        self.t_active_day   = 0

    def compute_energy_day(self):
        self.energy_day = self.t_active_day * self.i_active * self.v
    
    def add_active_time_day(self,state_duration,task_rate):
        self.t_active_day = self.t_active_day +state_duration*task_rate

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
class Node_module:
    def __init__(self,name = "None", v=0, i_sleep =0): # constructor
        self.name       = name
        self.i_sleep    = i_sleep
        self.v          = v
        self.state_list = []
        self.sleep_state= Module_state("Sleep",v = v, i = i_sleep, duration = None)
        self.state_list.append(self.sleep_state)
        self.energy_day      = 0
        self.average_current = 0
        self.t_active_day    = 0
        
    def compute_energy_day(self):
        time = 24*60*60
        self.energy = 0
        self.sleep_state.duration     = 0
        self.sleep_state.t_active_day = 0
        self.sleep_state.energy       = 0

        for state in self.state_list:
            state.compute_energy_day()
            self.energy_day = self.energy_day + state.energy_day
            time = time - state.t_active_day

        if time <0:
            print("With tasks registered, the module is occupied for more than an hour")  
            return

        sleep_energy = time*self.v*self.i_sleep
        self.sleep_state.duration     = time
        self.sleep_state.t_active_day = time
        self.sleep_state.energy_day   = sleep_energy
        self.t_active_day = 24*60*60 - time
        self.energy_day = self.energy_day + sleep_energy
        return self.energy_day

    
    def add_state(self, module_state):
        if isinstance(module_state,Module_state):
            for x in self.state_list:
                if x.name==module_state.name:
                    return
            module_state.v = self.v
            self.state_list.append(module_state)

    def reset_module(self):
        self.energy_day   = 0
        self.t_active_day = 0
        self.sleep_state.energy_day = 0
        self.sleep_state.duration   = 0
        for module_state in self.state_list:
            module_state.t_active_day = 0
            module_state.energy_day = 0


#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
class Node_subtask:
    def __init__(self,name = "None", module = None, moduleState=None, stateDuration=0):
        self.name = name
        self.module  = module
        self.moduleState = moduleState
        self.stateDuration = stateDuration



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

            energy   = energy + subtask.module.v * subtask.moduleState.i_active *subtaskDuration
            
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


#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
class Node_profile:
    def __init__(self,name = "None",module_list = []): # constructor
        self.name = name
        self.module_list = module_list
        self.task_list   = []
        self.energy_day    = 0
        self.average_power = 0
        self.sleep_task = Node_task("Sleep",module_list,task_rate = 1)
        self.task_list.append(self.sleep_task)

    def reset_node(self):
        for module in self.module_list:
            module.reset_module()
        for task in self.task_list:
            task.energy_day  = 0
            task.energy_task =0

    def set_taskList(self,taskList):
        self.taskList = taskList
    
    def add_task(self, node_task):
        if isinstance(node_task,Node_task):
            for x in self.task_list:
                if x.name == node_task.name:
                    return
            node_task.node_modules = self.module_list
            self.task_list.append(node_task)

    def remove_task(self, node_task):
        if isinstance(node_task,Node_task):
            try:
                self.task_list.remove(node_task)
            except:
                print("Removing task error : task not registered")
    
    def add_module(self, module):
        if isinstance(module,Node_module):
            self.module_list.append(module)

    def compute_energy_day(self):
        time = 24*60*60
        self.energy_day = 0
        self.sleep_task.taskDuration = 0
        self.sleep_task.energy_day   = 0
        for task in self.task_list:
            task.compute_energy_day()
            self.energy_day = self.energy_day + task.energy_day
            time = time - (task.taskDuration*task.task_rate)
        if time <0:
            print("With task registered, the node is occupied for more than a day")  
            return

        sleep_energy =0
        for module in self.module_list:
            module.compute_energy_day()
            module.average_current = module.energy_day/(module.v*(24*60*60))
            sleep_energy = sleep_energy + time*module.v*module.i_sleep
        self.sleep_task.taskDuration     = time
        self.sleep_task.energy_day   = sleep_energy
  
        self.energy_day = self.energy_day + sleep_energy
        return self.energy_day


    def compute_average_power(self):
        self.average_power= self.energy_day/(24*60*60)
        return self.average_power

    def recompute(self):
        self.reset_node()
        self.compute_energy_day()
        self.compute_average_power()


    def plot_Power(self,save=False,filename="test"):
        fig, ax = plt.subplots(2,1,figsize =(6, 10))

        task_energy_day = []
        task_label  = []
        task_duration = []
        colors_task = []
        colors = listColor
        i=0
        for task in self.task_list :
            task_energy_day.append(task.energy_day)
            task_label.append(task.name)
            task_duration.append(task.taskDuration*task.task_rate)
            colors_task.append(colors[i]) 
            i=i+1

        labels0 = [('{}'+'\n'*int(100*b>7)+'({:.1f}%)').format(a,100*b)*int(100*b>0.5) for a,b in zip(task_label,np.asarray(task_energy_day)/self.energy_day)]
        patches0, texts0 = ax[0].pie(task_energy_day, labels = labels0, 
                                            shadow=False, 
                                            startangle=0,   colors= colors_task, 
                                            wedgeprops={'linewidth': 1.0, 'edgecolor': 'white'},
                                        textprops={'size': 'x-large'},normalize=True)
        ax[0].set_title("Tasks energy repartition",fontsize = 15)
        for i, patch in enumerate(patches0):
            texts0[i].set_color(patch.get_facecolor())
            texts0[i].set_fontsize(15)
        ax[0].legend(task_label,bbox_to_anchor=(1,0.5), bbox_transform=plt.gcf().transFigure, loc="lower right",fontsize = 12)

        module_task_energy = []
        module_task_label  = []
        module_label       = []
        module_task_t_active = []
        colors_module_task = []
        colors = ( "blue", "green", "red","orange", "indigo", "beige")
        i=0
        j=0
        indexModuleSleep = []
        for module in self.module_list :
            module_label.append(module.name)
            indexModuleSleep.append(j)
            for state in module.state_list:
                module_task_energy.append(state.energy_day)
                module_task_label.append(state.name)
                module_task_t_active.append(state.t_active_day)
                colors_module_task.append(colors[i])  
                j=j+1
            i=i+1 
 
        labels1 = [('{}'+'\n'*int(100*b>7)+'({:.1f}%)').format(a,100*b)*int(100*b>0.5) for a,b in zip(module_task_label,np.asarray(module_task_energy)/self.energy_day)]
        patches1, texts1 = ax[1].pie(module_task_energy, labels = labels1, 
                                            shadow=False, 
                                            startangle=0, colors= colors_module_task,
                                            wedgeprops={'linewidth': 1.0, 'edgecolor': 'white'},
                                            textprops={'size': 'x-large'},)
        ax[1].set_title("Modules energy repartition",fontsize = 15)
        ax[1].legend([patches1[i] for i in indexModuleSleep],module_label, bbox_to_anchor=(1,0), bbox_transform=plt.gcf().transFigure, loc="lower right",fontsize = 12)
        for i, patch in enumerate(patches1):
            texts1[i].set_color(patch.get_facecolor())
            texts1[i].set_fontsize(11)

        fig.suptitle("Power consumption over 1 day : %s\nTotal = %8.3f [mW]" %(self.name,self.average_power),fontsize = 17,color='black')
        if(save):
            plt.savefig(filename+".svg", format="svg")




    def plot_Modules(self,save=False,filename="test"):
        fig, ax = plt.subplots(1,1,figsize =(6, 8))

        module_label       = []
        module_energy      = []
        colors = ( "blue", "green", "red","orange", "indigo", "beige")
        i=0
        j=0
        indexModuleSleep = []
        for module in self.module_list :
            module_label.append(module.name)
            module_energy.append(module.energy_day)
            i=i+1 
 
        patches1, texts1 = ax.pie(module_energy, labels = module_label, 
                                            shadow=False, 
                                            startangle=0, colors= listColor,
                                            wedgeprops={'linewidth': 1.0, 'edgecolor': 'black'},
                                            textprops={'size': 'x-large'},)
        ax.set_title("Modules energy repartition",fontsize = 15)
        ax.legend([patches1[i] for i in indexModuleSleep],module_label, bbox_to_anchor=(1,0), bbox_transform=plt.gcf().transFigure, loc="lower right",fontsize = 12)
        for i, patch in enumerate(patches1):
            texts1[i].set_color(patch.get_facecolor())
            texts1[i].set_fontsize(11)

        fig.suptitle("Power consumption over 1 day : %s\nTotal = %8.3f [mW]" %(self.name,self.average_power),fontsize = 17,color='black')
        if(save):
            plt.savefig(filename+".svg", format="svg")

    def print_Modules(self):
        print("-----------------------------------------------------------------")
        print("                        Module summary (1 Day)                   ")
        print("-----------------------------------------------------------------") 
        print ("{:<12} {:<12} {:<12} {:<12} {:<12}  ".format("Module","State","Active [s]","Energy [mJ]","Av. Cur.[uA]"))
        for module in self.module_list:
            print ("{:<12} {:<12} {:<12.4f} {:<12.4f} {:<12.4f}  ".format(module.name," ",module.t_active_day,module.energy_day,module.average_current*1000))
            for state in module.state_list:
                print ("{:<12} {:<12} {:<12.4f} {:<12.4f} ".format("     -",state.name,state.t_active_day,state.energy_day))
        print("-----------------------------------------------------------------")      
        print ("{:<12} {:<12} {:<12} {:<12.4f}  {:<6.4f}  {:<4} ".format("Total"," "," ",self.energy_day,self.average_power,"[mW]"))
        print("-----------------------------------------------------------------")

    def print_Tasks(self):
        print("-------------------------------------------------")
        print("            Tasks summary (1 Day)            ")
        print("-------------------------------------------------")
        print ("{:<12} {:<6} {:<2} ".format( "Task name"," "," :"), end="")
        for task in self.task_list:
            print("{:<15}".format(task.name),end="")
        print("")
        print ("{:<12} {:<6} {:<2} ".format( "Times/day","[1/d]"," :"), end="")
        for task in self.task_list:
            print("{:<15}".format(task.task_rate),end="")
        print("")
        print ("{:<12} {:<6} {:<2} ".format("Tot. durat.", "[s]"," :"), end="")
        for task in self.task_list:
            print("{:<15.4f}".format(task.taskDuration*task.task_rate),end="")
        print("")  
        print ("{:<12} {:<6} {:<2} ".format("Tot. en./d", "[mJ]"," :"), end="")
        for task in self.task_list:
            print("{:<15.4f}".format(task.energy_day),end="")
        print("")  
        print ("{:<12} {:<6} {:<2} {:<15.4f} ".format("Node en./d", "[mJ]"," :",self.energy_day))
        print ("{:<12} {:<6} {:<2} {:<15.4f} ".format("Average pow.", "[mW]"," :",self.average_power))
        print("-------------------------------------------------")

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%    
  

