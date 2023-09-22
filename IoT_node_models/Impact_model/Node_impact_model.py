
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

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from MyColors           import *


from Impact_model.Node_BoM     import *
from Impact_model.Transport    import *
