#%%
import numpy as np


from IoT_node_models.Energy_model.Node_module import *
from IoT_node_models.Energy_model.Node_task   import *
from IoT_node_models.Energy_model.Node        import *


import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from MyColors           import *

###################################################################################################
# INFORMATION
###################################################################################################
#
# The modeling done here is made over a day but it is purely arbitrary
#
###################################################################################################




#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# Given node profile described by:
#   -The list of module used
#   -The list of tasks performed
# Additional variables used:
#   -energy_day    : energy consumed over the day
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
class Node_profile:
    def __init__(self,name = "None",node = None, time_window=(24*60*60)): # constructor
        self.name = name
        self.node = node
        self.task_list      = []
        self.task_rate_list = []
        self.time_window   = time_window
        self.energy        = 0
        self.average_power = 0
        self.lifetime      = 0
        self.sleep_task = Node_task(name = "Sleep",node_modules = node.get_module_list())
        self.task_list.append(self.sleep_task)
        self.task_rate_list.append(1)

    def reset_node_profile(self):
        self.energy        = 0
        self.average_power = 0
        self.lifetime      = 0
        self.node.reset_Node()
        for task in self.task_list:
            task.reset_task()

        self.sleep_task.reset_task()
        self.sleep_task.set_taskDuration(0)

    def set_taskList(self,taskList,taskRates):
        self.task_list      = taskList
        self.task_rate_list = taskRates
        self.task_list.append(self.sleep_task)
        self.task_rate_list.append(1)
        self.reset_node_profile()

    def get_task_rate(self,node_task):
        try:
            index_task = self.task_list.index(node_task)
            return self.task_rate_list[index_task]
        except ValueError:
            raise Exception("Error: task for which task rate must be updated is not part of the node tasks")

    def change_task_rate(self,node_task,task_rate):
        try:
            index_task = self.task_list.index(node_task)
            self.task_rate_list[index_task] =task_rate
        except ValueError:
            raise Exception("Error: task for which task rate must be updated is not part of the node tasks")
        


    def add_task(self, node_task,task_rate):
        if isinstance(node_task,Node_task):
            for x in self.task_list:
                if x.name == node_task.get_name():
                    raise Exception("Error : Trying to add a task that is already part of the tasks list") 
            node_task.node_modules = self.node.get_module_list()
            self.task_list.append(node_task)
            self.task_rate_list.append(task_rate)
        else:
            raise TypeError("Error : a variable type different than Node_task was provided to add_task")


    def remove_task(self, node_task):
        if isinstance(node_task,Node_task):
            try:
                self.task_list.remove(node_task)
                self.reset_node_profile()
            except:
                raise Exception("Error : Trying to remove a task from the node that it does not perform") 
        else:
            raise TypeError("Error : a variable type different than Node_task was provided to add_task")


    #def set_moduleList(self,moduleList):
    #    self.module_list      = moduleList
    #    self.reset_node_profile()
#
#
    #def add_module(self, module):
    #    if isinstance(module,Node_module):
    #        self.module_list.append(module)
    #        self.reset_node_profile()
    #    else:
    #        raise TypeError("Error : a variable type different than Node_module was provided to add_module")
        
    def compute_energy_day(self):
        self.time_window = 24*60*60
        self.compute_energy(self.time_window)


    def compute(self):
        time = self.time_window
        ####################################
        # 1 ) Reset the different variables
        ####################################
        self.reset_node_profile()
        #################################################################################
        # 2 ) For each task, compute the energy consumes to perform it over a single day
        #################################################################################
        for task_index, task in enumerate(self.task_list):
            if task != self.sleep_task:
                task.compute_energy_task()
                #Accumulate the energy of each tasks to compute the total in active
                self.energy = self.energy + (task.get_energy_task() * self.task_rate_list[task_index])
                #Compute the time spent in standby/default/sleep mode
                time = time - (task.get_taskDuration()*self.task_rate_list[task_index])

                # Update the time spent in the different state for each module
                for subtask in task.subtasks:
                    (subtask.get_moduleState()).add_active_time(subtask.stateDuration,self.task_rate_list[task_index])

        if time <0:
            raise Exception("Error : With task registered, the node is busy for more than a day") 
            return

        #We now know the time spent in sleep mode and can update the different modules accumulated energy accordingly

        #################################################################################
        # 3 ) For each module, compute the energy it consumes over a single day
        #################################################################################
        self.node.compute(self.time_window)

        #################################################################################
        # 4 ) Update the information regarding the sleep task and compute the total
        #################################################################################
        #Update the information regarding the sleep task
        self.sleep_task.set_taskDuration( time )
        sleep_energy = self.sleep_task.compute_energy_task()
        
        #Compute the final total
        self.energy = self.energy + sleep_energy
        if (100*(self.node.get_energy() - self.energy)/self.energy) > 0.00001 :
            print(self.node.get_energy())
            print(self.energy)
            raise Exception("Result of energy calculation on Node modules and Tasks differ")
        
        self.average_power= self.energy/(self.time_window)
        self.lifetime = self.node.get_lifetime()
        return self.energy



    def get_Node(self):
            return self.node


    def plot_Power(self,save=False,filename="test"):
        fig, ax = plt.subplots(2,1,figsize =(6, 10))

        task_energy = []
        task_label  = []
        task_duration = []
        colors_task = []
        colors = listColor
        i=0
        for task_index,task in enumerate(self.task_list) :
            task_energy.append(task.get_energy_task() * self.task_rate_list[task_index])
            task_label.append(task.get_name())
            task_duration.append(task.get_taskDuration()*self.task_rate_list[task_index])
            colors_task.append(colors[i]) 
            i=i+1

        labels0 = [('{}'+'\n'*int(100*b>7)+'({:.1f}%)').format(a,100*b)*int(100*b>0.5) for a,b in zip(task_label,np.asarray(task_energy)/self.energy)]
        patches0, texts0 = ax[0].pie(task_energy, labels = labels0, 
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
        for module in self.node.get_module_list() :
            module_label.append(module.get_name())
            indexModuleSleep.append(j)
            for state in module.state_list:
                module_task_energy.append(state.get_energy())
                module_task_label.append(state.get_name())
                module_task_t_active.append(state.get_activeTime())
                colors_module_task.append(colors[i])  
                j=j+1
            i=i+1 
 
        labels1 = [('{}'+'\n'*int(100*b>7)+'({:.1f}%)').format(a,100*b)*int(100*b>0.5) for a,b in zip(module_task_label,np.asarray(module_task_energy)/self.energy)]
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
        for module in self.node.get_module_list() :
            module_label.append(module.get_name())
            module_energy.append(module.get_energy())
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
        for module in self.node.get_module_list():
            print ("{:<12} {:<12} {:<12.4f} {:<12.4f} {:<12.4f}  ".format(module.get_name()," ",module.get_activeTime(),module.get_energy(),module.get_average_current()*1000))
            for state in module.state_list:
                print ("{:<12} {:<12} {:<12.4f} {:<12.4f} ".format("     -",state.get_name(),state.get_activeTime(),state.get_energy()))
        print("-----------------------------------------------------------------")      
        print ("{:<12} {:<12} {:<12} {:<12.4f}  {:<6.4f}  {:<4} ".format("Total"," "," ",self.energy,self.average_power,"[mW]"))
        print("-----------------------------------------------------------------")

    def print_Tasks(self):
        print("-------------------------------------------------")
        print("            Tasks summary (1 Day)            ")
        print("-------------------------------------------------")
        print ("{:<12} {:<6} {:<2} ".format( "Task name"," "," :"), end="")
        for task in self.task_list:
            print("{:<15}".format(task.get_name()),end="")
        print("")
        print ("{:<12} {:<6} {:<2} ".format( "Times/day","[1/d]"," :"), end="")
        for task_index,task in enumerate(self.task_list):
            print("{:<15}".format(self.task_rate_list[task_index]),end="")
        print("")
        print ("{:<12} {:<6} {:<2} ".format("Tot. durat.", "[s]"," :"), end="")
        for task_index,task in enumerate(self.task_list):
            print("{:<15.4f}".format(task.get_taskDuration()*self.task_rate_list[task_index]),end="")
        print("")  
        print ("{:<12} {:<6} {:<2} ".format("Tot. en./d", "[mJ]"," :"), end="")
        for task_index,task in enumerate(self.task_list):
            print("{:<15.4f}".format(task.get_energy_task() *self.task_rate_list[task_index]),end="")
        print("")  
        print ("{:<12} {:<6} {:<2} {:<15.4f} ".format("Node en./d", "[mJ]"," :",self.energy))
        print ("{:<12} {:<6} {:<2} {:<15.4f} ".format("Average pow.", "[mW]"," :",self.average_power))
        print("-------------------------------------------------")










        

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%    
  

