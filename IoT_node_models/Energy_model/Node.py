#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# Given node profile described by:
#   -The list of module used
# Additional variables used:
#   -energy_day    : energy consumed over the day
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
class Node_profileazeraze:
    def __init__(self,name = "None",module_list = []): # constructor
        self.name = name
        self.module_list = module_list
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
        self.task_list.append(self.sleep_task)
        self.reset_node()

    def add_task(self, node_task):
        if isinstance(node_task,Node_task):
            for x in self.task_list:
                if x.name == node_task.name:
                    raise Exception("Error : Trying to add a task that is already part of the tasks list") 
            node_task.node_modules = self.module_list
            self.task_list.append(node_task)

    def remove_task(self, node_task):
        if isinstance(node_task,Node_task):
            try:
                self.task_list.remove(node_task)
                self.reset_node()
            except:
                print("Removing task error : task not registered")
    
    def add_module(self, module):
        if isinstance(module,Node_module):
            self.module_list.append(module)
            self.reset_node()

    def compute_energy_day(self):
        time = 24*60*60
        ####################################
        # 1 ) Reset the different variables
        ####################################
        self.energy_day = 0
        self.sleep_task.taskDuration = 0
        self.sleep_task.energy_day   = 0

        #################################################################################
        # 2 ) For each task, compute te energy consumes to perform it over a single day
        #################################################################################
        for task in self.task_list:
            task.compute_energy_day()
            #Accumulate the energy of each tasks to compute the total in active
            self.energy_day = self.energy_day + task.energy_day
            #Compute the time spent in standby/default/sleep mode
            time = time - (task.taskDuration*task.task_rate)
        if time <0:
            raise Exception("Error : With task registered, the node is busy for more than a day") 
            return

        #We now know the time spent in sleep mode and can update the different modules accumulated energy accordingly

        #################################################################################
        # 3 ) For each module, compute the energy it consumes over a single day
        #################################################################################
        sleep_energy =0
        for module in self.module_list:
            #Compute the module energy for a single day, considering sleep mode.
            module.compute_energy_day()
            module.average_current = module.energy_day/(module.v*(24*60*60))
            #Add the energy of the given module in sleep mode to the overall energy consumption
            sleep_energy = sleep_energy + time*module.v*module.i_sleep

        #################################################################################
        # 4 ) Update the information regarding the sleep task and compute the total
        #################################################################################
        #Update the information regarding the sleep task
        self.sleep_task.taskDuration     = time
        self.sleep_task.energy_day   = sleep_energy
        
        #Compute the final total
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