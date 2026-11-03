#%%
import numpy as np
from matplotlib import patches as mpatches


from Node_description.Component import *
from Node_description.Task   import *
from Node_description.Hardware        import *


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
class Node_description:
    def __init__(self,name = "None",hardware = None, profile=None,  time_window=(24*60*60)): # constructor
        self.name           = name
        self.hardware       = hardware
        self.profile        = profile
        self.time_window    = time_window
        self.energy         = 0
        self.average_power  = 0
        self.lifetime       = 0
        self.sleep_energy   = 0
        self.sleep_task     = Sleep_Task(components = hardware.get_component_list())

    def reset_node(self):
        self.energy        = 0
        self.sleep_energy  = 0
        self.average_power = 0
        self.lifetime      = 0
        self.hardware.reset_hardware()
        self.profile.reset_profile()

        self.sleep_task.reset_task()
        self.sleep_task.set_taskDuration(0)


    def compute(self):
        time = self.time_window
        ####################################
        # 1 ) Reset the different variables
        ####################################
        self.reset_node()
        #################################################################################
        # 2 ) For each task, compute the energy consumes to perform it over a single day
        #################################################################################
        self.energy = self.profile.compute()
        
        #################################################################################
        # 3 ) For each component, compute the energy it consumes over a single day
        #################################################################################
        self.hardware.compute(self.time_window)

        #################################################################################
        # 4 ) Update the information regarding the sleep task and compute the total
        #################################################################################
        self.sleep_energy = self.sleep_task.compute_energy_task()
        #Compute the final total
        self.energy = self.energy + self.sleep_energy
        
        if (100*(self.hardware.get_energy() - self.energy)/self.energy) > 0.00001 :
            print(self.hardware.get_energy())
            print(self.energy)
            raise Exception("Result of energy calculation on Node components and tasks differ")
        
        self.average_power= self.energy/(self.time_window)
        self.lifetime = self.hardware.get_lifetime()
        return self.energy



    def get_hardware(self):
            return self.hardware


    def plot_power(self,save=False,filename="test", plotAction = False):
        fig, ax = plt.subplots(2,1,figsize =(6, 10))

        task_energy = []
        task_label  = []
        colors_task = []
        patches_list = []
        colors = listColor
        i=0
        j=0

        plot_task_list      =  self.profile.task_list      + [self.sleep_task]
        plot_task_rate_list =  self.profile.task_rate_list + [1]

        if plotAction :
            for task_index,task in enumerate(plot_task_list) :
                if (task.get_energy_task()* plot_task_rate_list[task_index] != 0) :
                    patches_list.append( mpatches.Patch(color=colors[i], label=task.get_name()))
                    for action_index, action in enumerate (task.actions) :
                        task_energy.append(action.get_energy() * plot_task_rate_list[task_index])
                        task_label.append(action.get_name())
                        colors_task.append(colors[i]) 
                        patches_list.append( mpatches.Patch(color='white', label=action.get_name()))
                        
                        j=j+1
                    i=i+1
        else :
            for task_index,task in enumerate(plot_task_list) :
                task_energy.append(task.get_energy_task() * plot_task_rate_list[task_index])
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

        if plotAction :
            
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
        for component in self.hardware.get_component_list() :
            component_label.append(component.get_name())
            
            if component.state_list and component.sleep_state.get_i() > 0:
                indexModuleSleep.append(j)
                for state in component.state_list:
                    component_task_energy.append(state.get_energy())
                    component_task_label.append(state.get_name())
                    component_task_t_active.append(state.get_activeTime())
                    colors_component_task.append(colors[i])  
                    j=j+1
                if component.get_i_sleep() > 0:
                    component_task_energy.append(component.sleep_state.get_energy())
                    component_task_label.append(component.sleep_state.get_name())
                    component_task_t_active.append(component.sleep_state.get_activeTime())
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


    def print_tasks(self):
        self.profile.print_tasks(additional_tasks=[self.sleep_task], additional_task_rates=[1])

    def print_components(self):
        self.hardware.print_components()










        

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%    
  

