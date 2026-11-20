#%%
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib import patches as mpatches

from ..MyColors import *
from ..Node_description.Hardware.Footprint import FootprintVector, LOW, MID, HIGH



fontsize        = 14
fontsize_perc   = 12
fontsize_ytick  = 14
fontsize_legend = 14

def get_total_cycle_count(task):
    total = 0

    for action in task.actions:
        if hasattr(action, 'cycle_count') and action.cycle_count is not None:
            total+=action.cycle_count
    return total

import matplotlib.gridspec as gridspec

def breakdown_cycle_count(task,figAppend=None,printBreakdown=False,figsize=(10, 8), norm_factor=1, keep_total=False):
    action_names = []
    cycle_counts = []

    normalize = not keep_total

    for action in task.actions:
        if hasattr(action, 'cycle_count') and action.cycle_count is not None:
            action_names.append(action.name)
            cycle_counts.append(action.cycle_count/norm_factor)
        

    labels = [('{}'+'\n'*int(100*b>7)+'({:.1f}%)').format(a,100*b)*int(100*b>0.5) for a,b in zip(action_names,np.asarray(cycle_counts)/np.sum(cycle_counts))]
    # Create figure
    if not figAppend:
        fig, ax = plt.subplots(figsize=figsize)
    else:
        fig, ax = figAppend

        n = len(fig.axes) + 1
        cols = n
        rows = math.ceil(n / cols)

        # 2. Create a new GridSpec with the updated dimensions
        gs = gridspec.GridSpec(1, cols, figure=fig)

        # 3. Reposition all existing axes to fit the new grid
        for i, existing_ax in enumerate(fig.axes):
            existing_ax.set_subplotspec(gs[i])

        ax = fig.add_subplot(gs[n - 1])

    colors = plt.cm.Set3(np.linspace(0, 1, len(action_names)))
    wedges, texts, = ax.pie(cycle_counts, labels=labels,  radius = 0.8,
                                        colors=colors, startangle=90, shadow=False, 
                                        wedgeprops={'linewidth': 1.0, 'edgecolor': 'white'},
                                        textprops={'size': 'x-large'}, normalize=normalize)

    for text in texts:
        text.set_fontsize(fontsize)

    # Add total cycles in center or as legend
    total_cycles = sum(cycle_counts)*norm_factor
    ax.text(0.0, -1, f'Total: {total_cycles/1e6:.2f}M cycles', 
            ha='center', fontsize=fontsize_perc, style='italic')

    if printBreakdown:
        # Print detailed breakdown
        print("\nCycle Count Breakdown for Audio Classification with SW FFT:")
        print("-" * 60)
        for action_name, count in zip(action_names, cycle_counts):
            percentage = norm_factor*(count / total_cycles) * 100
            print(f"{action_name:20s}: {int( norm_factor*count):>12,} cycles ({percentage:5.1f}%)")
        print("-" * 60)
        print(f"{'Total':20s}: {int(total_cycles):>12,} cycles ({100.0:5.1f}%)")

    return fig, ax



def breakdown_power(node,figAppend=None,printBreakdown=False,figsize=(10, 8), norm_factor = 1, keep_total=False):

    task_energy  = []
    task_en_ratio= []
    task_label   = []
    colors_task  = []
    patches_list = []
    colors = listColor
    i=0
    j=0

    
    normalize = not keep_total

    plot_task_list      =  node.profile.task_list      + [node.sleep_task, node.power_tree_task]
    plot_task_rate_list =  node.profile.task_rate_list + [1, 1]


    for task_index,task in enumerate(plot_task_list) :
        if (task.get_energy_task()* plot_task_rate_list[task_index] != 0) :
            patches_list.append( mpatches.Patch(color=colors[i], label=task.get_name()))
            for action_index, action in enumerate (task.actions) :
                task_energy   .append(action.get_energy() * plot_task_rate_list[task_index]/ (norm_factor*node.profile.get_time_window()))
                task_en_ratio .append(action.get_energy() * plot_task_rate_list[task_index]/ (node.energy))
                task_label    .append(action.get_name())
                patches_list  .append( mpatches.Patch(color='white', label=action.get_name()))
                
                j=j+1
            i=i+1

    #################################################
    if not figAppend:
        fig, ax = plt.subplots(figsize=figsize)
    else:
        fig, ax = figAppend

        n = len(fig.axes) + 1
        cols = n
        rows = math.ceil(n / cols)

        # 2. Create a new GridSpec with the updated dimensions
        gs = gridspec.GridSpec(1, cols, figure=fig)

        # 3. Reposition all existing axes to fit the new grid
        for i, existing_ax in enumerate(fig.axes):
            existing_ax.set_subplotspec(gs[i])

        ax = fig.add_subplot(gs[n - 1])

    #################################################
    colors = plt.cm.Set3(np.linspace(0, 1, len(task_label)))
    labels0 = [('{}'+'\n'*int(100*b>7)+'({:.1f}%)').format(a,100*b)*int(100*b>0.5) for a,b in zip(task_label,task_en_ratio)]

    patches0, texts0 = ax.pie(task_energy, labels = labels0, radius = 0.8,
                                        shadow=False, 
                                        startangle=0,   colors= colors, 
                                        wedgeprops={'linewidth': 1.0, 'edgecolor': 'white'},
                                    textprops={'size': 'x-large'},normalize=normalize)
    
    ax.set_title("Tasks energy repartition",fontsize = 15)
    for i, patch in enumerate(patches0):
        #texts0[i].set_color(patch.get_facecolor())
        texts0[i].set_fontsize(10)

    
    # Add total cycles in center or as legend
    ax.text(0.0, -1, f'Total: {node.average_power:.3f}mW', 
            ha='center', fontsize=fontsize_perc, style='italic')

    return fig, ax

