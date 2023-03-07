from matplotlib import colors, pyplot as plt
import matplotlib.pyplot as plt
plt.rcParams['figure.facecolor'] = 'white'
plt.rcParams['mathtext.fontset'] = 'stix'
plt.rcParams['font.family'] = 'STIXGeneral'
plt.rcParams['font.size'] = 16
import math
import numpy as np
import inspect
import scipy.interpolate
import plotly.graph_objects as go
import plotly.express as px
import plotly.io as pio
pio.renderers.default = "svg"
from plotly.offline import plot



dictColor = {"DeepBlue"     :"#095256",
             "LightBlue"    :"#01a7c2",
             "UnitedBlue"   :"#6290c8",
             "CerulBlue"    :"#6096ba",
             "Green"        :"#44af69",
             "LightRed"     :"#f8333c",
             "DeepRed"      :"#a22c29",
             "Orange"       :"#fcab10",
             "Sandy"        :"#fc9e4F",
             "Olivine"      :"#9ab87a",
             "CarolinaBlue" :"#009DDC"}
listColor = list(dictColor.values())

greenDict  = {  "Granny Smith Apple":"#b9ffb7",
                "Magic Mint"        :"#abedc6",
                "Middle Blue Green" :"#98d9c2",
                "Olivine"           :"#9ab87a",
                "Green"             :"#44af69",
                "Fern Green"        :"#3a7d44"}
listGreen = list(greenDict.values())

redDict   = {   "FieryRose"         :"#f45b69",
                "Crimson"           :"#d7263d",
                "LightRed"          :"#f8333c",       
                "DeepRed"           :"#db222a",
                "Upsdell"           :"#ad2831"}
listRed  = list(redDict.values())


##F15025 BC3908
orangeDict = {  "Maize"             :"#ffcf56",
                "Yellow"            :"#f5d547",
                "Brown  "           :"#F15025",
                "Red"               :"#ff0000",
                "Orange"            :"#fcab10",
                "Flame  "           :"#e55934",
                "Orange2"           :"#ff8200",               
                "Mellow Apricot"    :"#f7b267",
                "Atomic Tangerine"  :"#f79d65",
                "Coral"             :"#f4845f",
                "Bittersweet"       :"#f27059",
                "Orange Red Crayola":"#f25c54"}
listOrange = list(orangeDict.values())
listOrange.reverse()

blueDict  = {   "Baby Blue Eyes"    :"#a7cced",
                "Blue Jeans"        :"#63adf2",
                "CarolinaBlue"      :"#009DDC",
                "LightBlue"         :"#01a7c2",
                "UnitedBlue"        :"#6290c8",
                "CerulBlue"         :"#6096ba",
                "Independence"      :"#545e75",
                "Y In Mn Blue"      :"#304d6d",
                }
listBlue  = list(blueDict.values())

turquoiseDict=  {   "Tiffany Blue"      :"#07beb8",
                    "Medium Turquoise"  :"#3dccc7",
                    "Medium Turquoise 2":"#68d8d6",
                    "Blizzard Blue"     :"#9ceaef",
                    "Celeste"           :"#c4fff9"}
listTurquoise  = (list(turquoiseDict.values()))
listTurquoise.reverse()

colorGrey     = "#b3bfb8"
colorGreyDark = "#949ba0"

def plotColors(dict):
    fig,ax = plt.subplots(1,1,figsize=(8,4))
    plt.bar(range(len(dict)), np.ones(len(dict)), align='center',color= list(dict.values()))
    plt.xticks(range(len(dict)), list(dict.keys()),rotation = 90)

if __name__ == '__main__':
    plotColors(greenDict)
    plotColors(dictColor)
    plotColors(redDict)
    plotColors(blueDict)
    plotColors(orangeDict)
    plt.show()