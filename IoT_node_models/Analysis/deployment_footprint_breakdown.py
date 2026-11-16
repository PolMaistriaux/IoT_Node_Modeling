#%%
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

from ..MyColors import *
from ..Node_description.Hardware.Footprint import FootprintVector, LOW, MID, HIGH

def plot_deployment_footprint_breakdown(node,name="", analysis_number = 0,label="GWP", figsize=(10, 6), factor_xlim = 1.1,
                                        filename=None, figAppend=None, fontsize=14,**kwargs):
    """Plot horizontal bar chart of deployment footprint breakdown.

    Shows contributions from:
    - Hardware total footprint (per node)
    - Overhead placement (transport/other placement costs)
    - Overhead decommissioning
    - Overhead replacement (transport/other replacement costs)

    Parameters
    ----------
    node : Node_description
        A fully computed node with deployment_strategy set.
    label : str
        Impact label to plot (must exist in node.hardware.footprintStructure).
        Default: "GWP"
    figsize : tuple, optional
        Figure size (width, height). Default: (10, 6)
    filename : str, optional
        If provided, save the figure to this path.
    figAppend : [fig, ax], optional
        If provided, append bars to existing figure and axes instead of creating new ones.
    **kwargs
        Additional keyword arguments (colorList, title, etc.)

    Returns
    -------
    fig, ax
        Matplotlib figure and axes for further modification or appending.

    Raises
    ------
    ValueError
        If node.deployment_strategy or hardware footprint is not computed.
    """
    # Validate inputs
    if node.deployment_strategy is None:
        raise ValueError("Node must have a deployment_strategy set")
    if node.deployment_strategy.total_footprint is None:
        raise ValueError("Node must be computed (node.compute()) before plotting")

    ds = node.deployment_strategy
    hw = node.hardware

    # Extract values for the given label
    try:
        hw_footprint = hw.footprint_total[label]
    except (KeyError, TypeError):
        raise ValueError(f"Label '{label}' not found in hardware footprint")

    # Overhead values (scalars or FootprintVectors with [label] access)
    overhead_placement      = ds.overhead_placement[label]      
    overhead_decom          = ds.overhead_decom[label]          
    overhead_replacement    = ds.overhead_replacement[label]    
    overhead_sum = (overhead_placement+ overhead_decom+ overhead_replacement)
    # Prepare data
    components = [
        "Initial hardware (1st deployement)",
        f"{node.deployment_strategy.n_replacements:.1f} hardware replacements",
        "Transport overheads",
    ]
    values = [
        hw_footprint[MID],
        ds.total_footprint[label][MID] -  hw_footprint[MID] - (overhead_sum[MID]*node.deployment_strategy.n_replacements),
        overhead_sum[MID]*node.deployment_strategy.n_replacements,
    ]
    tot_footprint = ds.total_footprint[label][MID]
    # Create or append to figure
    if figAppend is not None:
        fig, ax = figAppend
    else:
        fig, ax = plt.subplots(figsize=figsize)
        ax.set_yticks([0])
        ax.set_yticklabels([""])

    # Color list
    colorList = [blueDict["UnitedBlue"], blueDict["Independence"],colorGreyDark]

    analysis_number= - analysis_number
    # Create horizontal bar plot
    total = 0
    for i in range(len(components)):
        ax.barh(analysis_number, values[i],left=total, height= 0.75,color=colorList[i],edgecolor='black', linewidth=1.5)
        total += values[i]
        
    total = 0
    # Add value labels on bars
    for i, value in enumerate(values):
        label_str = f'{100*value/tot_footprint:.1f}%'
        ax.text(total+value/2, analysis_number,
                f' {label_str}',
                ha='center', va='center', fontsize=fontsize)

        total += value

    ax.text(total, analysis_number,
            f' {tot_footprint:.2f}',
            ha='left', va='center', fontsize=fontsize, fontweight='bold')
    
    # Formatting
    current_ticks = list(ax.get_yticks())
    current_labels = [t.get_text() for t in ax.get_yticklabels()]

    ax.set_yticks(current_ticks + [analysis_number])
    ax.set_yticklabels(current_labels + [name])
    ax.set_xlabel(f'{label} Footprint', fontsize=fontsize)
    title = kwargs.get('title', f'Deployment Footprint Breakdown ({label})')
    ax.set_title(title, fontsize=fontsize, fontweight='bold')
    ax.set_axisbelow(True)
    ax.grid(axis='x')

    left, right = ax.get_xlim()
    # Set x-axis to start at 0
    ax.set_xlim(left=0)
    ax.set_xlim(right=max(factor_xlim*total, right))

    plt.tight_layout()

    if filename:
        fig.savefig(filename, dpi=300, bbox_inches='tight')

    
    print(ds.total_footprint)

    return fig, ax
