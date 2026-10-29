#%%
import numpy as np
from matplotlib import patches as mpatches


from Node_description.Component import *
from Node_description.Task   import *
from Node_description.Node        import *


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
#   -The list of component used
#   -The list of tasks performed
# Additional variables used:
#   -energy_day    : energy consumed over the day
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
class Profile:
    def __init__(self,name = "None",node = None, time_window=(24*60*60)): # constructor
        self.name = name
        self.node = node
        self.task_list      = []
        self.task_rate_list = []
        self.time_window   = time_window
        self.energy        = 0
        self.average_power = 0
        self.lifetime      = 0
        self.sleep_energy  = 0
        self.sleep_task = Sleep_Task(components = node.get_component_list())
        self.task_list.append(self.sleep_task)
        self.task_rate_list.append(1)

    def reset_Profile(self):
        self.energy        = 0
        self.sleep_energy  = 0
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
        self.reset_Profile()

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
            task.components = self.node.get_component_list()
            self.task_list.append(task)
            self.task_rate_list.append(task_rate)
        else:
            raise TypeError("Error : a variable type different than task was provided to add_task")


    def remove_task(self, task):
        if isinstance(task,Task):
            try:
                self.task_list.remove(task)
                self.reset_Profile()
            except:
                raise Exception("Error : Trying to remove a task from the node that it does not perform") 
        else:
            raise TypeError("Error : a variable type different than task was provided to add_task")


    def compute_energy_day(self):
        self.time_window = 24*60*60
        self.compute()


    def compute(self):
        time = self.time_window
        ####################################
        # 1 ) Reset the different variables
        ####################################
        self.reset_Profile()
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

                # Update the time spent in the different state for each component
                for action in task.actions:
                    (action.get_componentState()).add_active_time(action.stateDuration,self.task_rate_list[task_index], paramVI = action.get_paramVI() )

        if time <0:
            raise Exception("Error : With task registered, the node is busy for more than a day") 
            return

        #We now know the time spent in sleep mode and can update the different components accumulated energy accordingly
        #################################################################################
        # 3 ) For each component, compute the energy it consumes over a single day
        #################################################################################
        self.node.compute(self.time_window)

        #################################################################################
        # 4 ) Update the information regarding the sleep task and compute the total
        #################################################################################
        self.sleep_energy = self.sleep_task.compute_energy_task()
        #Compute the final total
        self.energy = self.energy + self.sleep_energy
        
        if (100*(self.node.get_energy() - self.energy)/self.energy) > 0.00001 :
            print(self.node.get_energy())
            print(self.energy)
            raise Exception("Result of energy calculation on Node components and tasks differ")
        
        self.average_power= self.energy/(self.time_window)
        self.lifetime = self.node.get_lifetime()
        return self.energy



    def get_Node(self):
            return self.node


    def plot_power(self,save=False,filename="test", plotSubtask = False):
        fig, ax = plt.subplots(2,1,figsize =(6, 10))

        task_energy = []
        task_label  = []
        colors_task = []
        patches_list = []
        colors = listColor
        i=0
        j=0

        if plotSubtask :
            for task_index,task in enumerate(self.task_list) :
                if (task.get_energy_task()* self.task_rate_list[task_index] != 0) :
                    patches_list.append( mpatches.Patch(color=colors[i], label=task.get_name()))
                    for action_index, action in enumerate (task.actions) :
                        task_energy.append(action.get_energy() * self.task_rate_list[task_index])
                        task_label.append(action.get_name())
                        colors_task.append(colors[i]) 
                        patches_list.append( mpatches.Patch(color='white', label=action.get_name()))
                        
                        j=j+1
                    i=i+1
        else :
            for task_index,task in enumerate(self.task_list) :
                task_energy.append(task.get_energy_task() * self.task_rate_list[task_index])
                task_label.append(task.get_name())
                colors_task.append(colors[i]) 
                i=i+1

        labels0 = [('{}'+'\n'*int(100*b>7)+'({:.1f}%)').format(a,100*b)*int(100*b>0.5) for a,b in zip(task_label,np.asarray(task_energy)/self.energy)]
        patches0, texts0 = ax[0].pie(task_energy, labels = labels0, 
                                            shadow=False, 
                                            startangle=0,   colors= colors_task, 
                                            wedgeprops={'linewidth': 1.0, 'edgecolor': 'white'},
                                        textprops={'size': 'x-large'},normalize=True)
        ax[0].set_title("tasks energy repartition",fontsize = 15)
        for i, patch in enumerate(patches0):
            texts0[i].set_color(patch.get_facecolor())
            texts0[i].set_fontsize(15)

        if plotSubtask :
            
            ax[0].legend(handles=patches_list,bbox_to_anchor=(1.5,0.5), bbox_transform=plt.gcf().transFigure, loc="lower right",fontsize = 12)
        else:
            ax[0].legend(task_label,bbox_to_anchor=(1.5,0.5), bbox_transform=plt.gcf().transFigure, loc="lower right",fontsize = 12)

        component_task_energy = []
        component_task_label  = []
        component_label       = []
        component_task_t_active = []
        colors_component_task = []
        colors = ( "blue", "green", "red","orange", "indigo", "beige")
        i=0
        j=0
        indexModuleSleep = []
        for component in self.node.get_component_list() :
            component_label.append(component.get_name())
            indexModuleSleep.append(j)
            for state in component.state_list:
                component_task_energy.append(state.get_energy())
                component_task_label.append(state.get_name())
                component_task_t_active.append(state.get_activeTime())
                colors_component_task.append(colors[i])  
                j=j+1
            i=i+1 
 
        labels1 = [('{}'+'\n'*int(100*b>7)+'({:.1f}%)').format(a,100*b)*int(100*b>0.5) for a,b in zip(component_task_label,np.asarray(component_task_energy)/self.energy)]
        patches1, texts1 = ax[1].pie(component_task_energy, labels = labels1, 
                                            shadow=False, 
                                            startangle=0, colors= colors_component_task,
                                            wedgeprops={'linewidth': 1.0, 'edgecolor': 'white'},
                                            textprops={'size': 'x-large'},)
        ax[1].set_title("Modules energy repartition",fontsize = 15)
        ax[1].legend([patches1[i] for i in indexModuleSleep],component_label, bbox_to_anchor=(1,0), bbox_transform=plt.gcf().transFigure, loc="lower right",fontsize = 12)
        for i, patch in enumerate(patches1):
            texts1[i].set_color(patch.get_facecolor())
            texts1[i].set_fontsize(11)

        fig.suptitle("Power consumption over 1 day : %s\nTotal = %8.3f [mW]" %(self.name,self.average_power),fontsize = 17,color='black')
        if(save):
            plt.savefig(filename+".svg", format="svg")






    def plot_Modules(self,save=False,filename="test"):
        fig, ax = plt.subplots(1,1,figsize =(6, 8))

        component_label       = []
        component_energy      = []
        colors = ( "blue", "green", "red","orange", "indigo", "beige")
        i=0
        j=0
        indexModuleSleep = []
        for component in self.node.get_component_list() :
            component_label.append(component.get_name())
            component_energy.append(component.get_energy())
            i=i+1 
 
        patches1, texts1 = ax.pie(component_energy, labels = component_label, 
                                            shadow=False, 
                                            startangle=0, colors= listColor,
                                            wedgeprops={'linewidth': 1.0, 'edgecolor': 'black'},
                                            textprops={'size': 'x-large'},)
        ax.set_title("Modules energy repartition",fontsize = 15)
        ax.legend([patches1[i] for i in indexModuleSleep],component_label, bbox_to_anchor=(1,0), bbox_transform=plt.gcf().transFigure, loc="lower right",fontsize = 12)
        for i, patch in enumerate(patches1):
            texts1[i].set_color(patch.get_facecolor())
            texts1[i].set_fontsize(11)

        fig.suptitle("Power consumption over 1 day : %s\nTotal = %8.3f [mW]" %(self.name,self.average_power),fontsize = 17,color='black')
        if(save):
            plt.savefig(filename+".svg", format="svg")

    def print_components(self):
        sum_energy = 0
        print("-----------------------------------------------------------------")
        print("                        Module summary                           ")
        print("-----------------------------------------------------------------") 
        print ("{:<12} {:<12} {:<12} {:<12} {:<12}  ".format("Module","State","Active [s]","Energy [mJ]","Av. Cur.[uA]"))
        for component in self.node.get_component_list():
            print ("{:<12} {:<12} {:<12.4f} {:<12.4f} {:<12.7f}  ".format(component.get_name()," ",component.get_activeTime(),component.get_energy(),component.get_average_current()*1000))
            for state in component.state_list:
                sum_energy = sum_energy + state.get_energy()
                print ("{:<12} {:<12} {:<12.4f} {:<12.4f} ".format("     -",state.get_name(),state.get_activeTime(),state.get_energy()))
        print("-----------------------------------------------------------------")      
        print ("{:<12} {:<12} {:<12} {:<12.4f}  {:<6.4f}  {:<4} ".format("Total"," "," ",sum_energy,sum_energy/self.time_window,"[mW]"))
        print("-----------------------------------------------------------------")
        if self.node.get_isPowered() :  
            print ("{:<12} {:<12} {:<12} {:<12} {:<12}  ".format("PMU","Vin[V]","Vout[V]","Energy [mJ]","Av. Cur.[uA]")) 
            for PMU in self.node.get_PMU_composition():
                print ("{:<12} {:<12} {:<12.4f} {:<12.4f} {:<12.4f}  ".format(PMU.get_name(),PMU.get_v_in(),PMU.get_v_out(),PMU.get_v_in()*PMU.get_i_in(),1000*PMU.get_i_in()))
            print("-----------------------------------------------------------------")
            print ("{:<12} {:<12} {:<12} {:<12} {:<12}  ".format("Battery","Vin[V]","C[mAh]","I [mJ]","Lifetime[years]")) 
            battery = self.node.get_Battery()
            print ("{:<12} {:<12} {:<12.4f} {:<12.4f} {:<12.4f}  ".format(battery.get_name(), battery.get_v(), battery.get_capacity_mAh(), battery.get_i(), battery.get_lifetime()))
            print("-----------------------------------------------------------------")

    def print_tasks(self):
        print("-------------------------------------------------")
        print("            Tasks summary                        ")
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
  

