#%%
import math
import numpy as np
import inspect
import importlib

import scipy.interpolate

import matplotlib
from matplotlib import pyplot as plt
import matplotlib.pyplot as plt

plt.rcParams['figure.facecolor'] = 'white'
plt.rcParams['mathtext.fontset'] = 'stix'
plt.rcParams['font.family'] = 'STIXGeneral'
plt.rcParams['font.size'] = 16

import plotly.graph_objects as go
import plotly.express as px
import plotly.io as pio
from plotly.offline import plot
pio.renderers.default = "svg"

import sys
import os
parent_directory = os.path.dirname(os.getcwd())
sys.path.append(parent_directory)

from IoT_node_models.Node_description                        import *
from IoT_node_models.Node_description.Wireless_communication import *
from IoT_node_models.Component_set                    import *
from IoT_node_models.Analysis                            import *

path_to_save_svg = "Saved_Data"



if __name__ == '__main__':
    print("Hello")
