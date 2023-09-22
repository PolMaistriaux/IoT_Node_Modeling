
#%%
from matplotlib import colors, pyplot as plt
import matplotlib as mpl
import matplotlib.pyplot as plt
plt.rcParams['figure.facecolor'] = 'white'
plt.rcParams['mathtext.fontset'] = 'stix'
plt.rcParams['font.family'] = 'STIXGeneral'
plt.rcParams['font.size'] = 16
import math
import numpy as np

from Impact_model.Node_BoM  import *
from Impact_model.Transport import *




def deployment_battery_replacement( Replacement_type = "Complete",Footprint=None,Node=None,Nyears= 100):
    Node.compute()
    [power,lifetime] = [Node.average_power,Node.lifetime] 
    Footprint.recompute()
    Placement_cost   = Footprint.F_prod[0] + Footprint.placement[0] + Footprint.battery[0]
    Decom_cost       = Footprint.decom[0]
    Replacement_cost = 0
    if Replacement_type == "Complete" : 
        Replacement_cost = Footprint.F_prod[0] + Footprint.replacement[0] + Footprint.battery[0]
    elif Replacement_type == "Battery" : 
        Replacement_cost = Footprint.replacement[0] + Footprint.battery[0]
    else:
        print("No replacement type found")
    Deployment_footprint   = Placement_cost + Decom_cost
    year = lifetime
    looping = True
    residue = 0 
    while looping :
        if year > Nyears:
            looping = False
            residue = year-Nyears
        else:
            Deployment_footprint = Deployment_footprint + Replacement_cost
            year = year + lifetime
    
    Deployment_footprint_2 = Placement_cost + Replacement_cost * np.max([0,(Nyears/lifetime)-1]) + Decom_cost
    Deployment_footprint_2 = Deployment_footprint_2/Nyears
    Deployment_footprint = Deployment_footprint/Nyears
    return [Deployment_footprint,Deployment_footprint_2,lifetime,power]