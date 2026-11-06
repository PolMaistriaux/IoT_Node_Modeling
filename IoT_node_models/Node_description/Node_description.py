#%%
import numpy as np
from matplotlib import patches as mpatches

from .Hardware.Component import *
from .Profile.Task   import *
from .Hardware        import *
from .Deployment_strategy        import *



import sys
import os
from ..MyColors           import *

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
    def __init__(self,name = "None",hardware = None, profile=None,deployment_strategy=None,  time_window=(24*60*60)): # constructor
        self.name           = name
        self.hardware       = hardware
        self.profile        = profile
        self.time_window    = time_window
        self.energy         = 0
        self.average_power  = 0
        self.lifetime       = 0
        self.sleep_energy   = 0
        self.sleep_task     = Sleep_Task(components = hardware.get_component_list())

        self.deployment_strategy = deployment_strategy if deployment_strategy is not None else DeploymentStrategy()

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

        
        #################################################################################
        # 5 ) Calculate footprint of node deployment
        #################################################################################
        if self.hardware.compute_footprint() is not None:
            self.deployment_strategy.compute_footprint(self.hardware, self.lifetime)
        
    
    def set_deployment_strategy(self, deployment_strategy):
        self.deployment_strategy = deployment_strategy

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


    def plot_footprint(self, label=None, cumulated_replacement=False, filename=None, figsize=(14, 6)):
        """Hardware-category bars on the left + deployment-phase bars on the right.

        The right section shows placement, a single replacement, cumulated replacements and
        decommissioning as stacked bars split between hardware (blue) and overhead such as
        transport (sandy).  A shared y-axis links both halves."""
        if self.hardware.compute_footprint() is None:
            return
        if self.deployment_strategy.placement is None:
            print("No deployment footprint computed. Call compute() first.")
            return

        labels = self.hardware.footprintStructure.labels
        label  = labels[0] if label is None else label
        unit   = self.hardware.footprintStructure.units[labels.index(label)]
        ylabel = f"{label} [{unit}]" if unit else label

        # ---- Hardware section (mirrors hardware.plot_footprint) ----------------
        rows = [(cat, *v[label]) for cat, v in self.hardware.footprint_by_category.items() if any(v[label])]
        if not rows:
            print(f"No {label} footprint to plot.")
            return
        rows.sort(key=lambda row: row[2])

        total_low, total, total_high = self.hardware.footprint_total[label]
        battery = 0
        battery_cat = None
        if self.hardware.Battery is not None:
            battery_cat = self.hardware.Battery.category
            if self.hardware.Battery.factors is not None:
                battery = self.hardware.Battery.factors[label][MID]

        hw_cats  = [row[0] for row in rows] + ["HW Total"]
        hw_low   = np.array([row[1] for row in rows] + [total_low])
        hw_mid   = np.array([row[2] for row in rows] + [total])
        hw_high  = np.array([row[3] for row in rows] + [total_high])
        hw_color = [dictColor["UnitedBlue"] if cat == battery_cat else dictColor["CarolinaBlue"] for cat in hw_cats]

        # ---- Deployment section ------------------------------------------------
        def _mid(fp, lbl):
            return fp[lbl][MID] if isinstance(fp, FootprintVector) else 0.0
        def _low(fp, lbl):
            return fp[lbl][LOW] if isinstance(fp, FootprintVector) else 0.0
        def _high(fp, lbl):
            return fp[lbl][HIGH] if isinstance(fp, FootprintVector) else 0.0

        ds = self.deployment_strategy
        n  = ds.n_replacements

        # per-phase: total, hardware share, overhead share
        if cumulated_replacement:
            phases = [
                ("Placement",             ds.placement,            ds.overhead_placement),
                (f"1 Replacement",        ds.replacement,          ds.overhead_replacement),
                (f"Cumul. Replacements\n(×{n:.4g})",
                                          ds.replacement * n,      ds.overhead_replacement if not isinstance(ds.overhead_replacement, FootprintVector) else ds.overhead_replacement * n),
                ("Decommissioning",       ds.decom,                ds.overhead_decom),
            ]
        else : 
            phases = [
                ("Placement",             ds.placement,            ds.overhead_placement),
                (f"1 Replacement",        ds.replacement,          ds.overhead_replacement),
                ("Decommissioning",       ds.decom,                ds.overhead_decom),
            ]

        dep_labels  = [p[0] for p in phases]
        dep_hw_mid  = np.array([_mid(p[1] , label) - _mid(p[2], label) for p in phases])
        dep_oh_mid  = np.array([_mid(p[2] , label)                     for p in phases])
        dep_low     = np.array([_low(p[1] , label)                     for p in phases])
        dep_high    = np.array([_high(p[1], label)                     for p in phases])
        dep_total   = dep_hw_mid + dep_oh_mid

        # ---- Figure ------------------------------------------------------------
        barWidth = 0.6
        ratio    = [max(len(hw_cats), 1), max(len(dep_labels), 1)]
        fig, (ax_hw, ax_dep) = plt.subplots(
            1, 2, figsize=figsize,
            gridspec_kw={"width_ratios": ratio, "wspace": 0.04},
        )

        all_max = max(np.max(hw_high), np.max(dep_high) if dep_high.size else 0) * 1.3
        if all_max == 0:
            all_max = 1

        # --- left panel: hardware categories ---
        hw_e_up  = hw_high - hw_mid
        hw_e_do  = hw_mid  - hw_low
        bars_hw  = ax_hw.bar(hw_cats, height=hw_mid, width=barWidth,
                             yerr=[hw_e_do, hw_e_up], color=hw_color, capsize=5, edgecolor="black")
        ax_hw.bar(hw_cats[-1:], height=[battery], width=barWidth,
                  color=dictColor["UnitedBlue"], edgecolor="black")
        ax_hw.set_ylabel(ylabel)
        ax_hw.set_ylim(0, all_max)
        ax_hw.tick_params(axis='x', labelrotation=45)
        plt.setp(ax_hw.get_xticklabels(), ha='right')
        ax_hw.set_title("Hardware")
        for rect in bars_hw:
            h = rect.get_height()
            if h > 0 and total > 0:
                ax_hw.text(rect.get_x() + rect.get_width() / 2, h,
                           f'{100*h/total:.1f}%', fontsize=10, ha='right', va='bottom', clip_on=True)
        if battery > 0:
            rect   = bars_hw[-1]
            side_x = rect.get_x() + rect.get_width() * 1.1
            ax_hw.text(side_x, (battery + min(total, all_max)) / 2,
                       f'{100*(total-battery)/total:.1f}%', fontsize=10, ha='left', va='center', rotation=-90)
            ax_hw.text(side_x, battery / 2,
                       f'{100*battery/total:.1f}%',         fontsize=10, ha='left', va='center', rotation=-90)

        # vertical separator: thicken adjacent spines
        ax_hw.spines['right'].set_linewidth(2)
        ax_dep.spines['left'].set_linewidth(2)

        # --- right panel: deployment phases ---
        bars_dep_hw = ax_dep.bar(dep_labels, height=dep_hw_mid, width=barWidth,
                                  color=dictColor["CerulBlue"], edgecolor="black", label="Hardware")
        bars_dep_oh = ax_dep.bar(dep_labels, height=dep_oh_mid, bottom=dep_hw_mid, width=barWidth,
                                  color=dictColor["Olivine"], edgecolor="black", label="Overhead")
        dep_e_up = np.maximum(dep_high - dep_total, 0)
        dep_e_do = np.maximum(dep_total - dep_low,  0)
        ax_dep.errorbar(np.arange(len(dep_labels)), dep_total,
                        yerr=[dep_e_do, dep_e_up], fmt='none', color='black', capsize=5)
        ax_dep.set_ylim(0, all_max)
        ax_dep.set_yticklabels([])
        ax_dep.tick_params(axis='x', labelrotation=45)
        plt.setp(ax_dep.get_xticklabels(), ha='right')
        ax_dep.set_title(f"Deployment ({ds.Nyears} yr)")
        ax_dep.legend(fontsize=10, loc="upper left")

        fig.tight_layout()
        if filename is not None:
            fig.savefig(filename + ".svg", format="svg")

    def print_tasks(self):
        self.profile.print_tasks(additional_tasks=[self.sleep_task], additional_task_rates=[1])

    def print_components(self):
        self.hardware.print_components()










        

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%    
  

