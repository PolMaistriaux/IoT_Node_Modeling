import math
import numpy as np
import sys
import logNormal_PL as logPL

c = 3e8


treeDict ={ #               TD      DT    Dc  FD  8.7e8  n    PLd0  2.4e9   n    PLd0 
    "Acacia dealbata"   : [0.4,     9,   0.8, 10,        3.4, 47.5,         3.5, 54.9],
    "Cryptomeria"       : [0.6,     8,   0.6, 30,        3.6, 46.1,         3.8, 57.1],
    "Pine"              : [0.1,     10,  2.6, 70,        3.5, 53.5,         3.3, 70.2],
    "Small pines"       : [0.375,   13,  2.0, 30,        4.5, 48.4,         5.2, 58.0],
    "Juniperus cedrus"  : [0.115,   18,  4.0, 70,        4.0, 45.5,         4.3, 64.6],
    "Different species" : [0.065,   38,  6.0, 30,        3.4, 47.2,         4.1, 56.3],
    "Spruce and oak"    : [0.035,   34,  5.4, 30,        3.2, 45.1,         3.2, 57.4],
    "Chestnut and cedar": [0.065,   18,  4.2, 50,        3.1, 47.7,         3.8, 62.8],
    "Beech"             : [0.043,   22,  7.0, 30,        3.3, 50.3,         3.6, 59.9],
    "Spruce"            : [0.033,   50,  6.4, 90,        3.0, 52.5,         3.2, 69.4],
    "Beech2"            : [0.035,   35,  3.0, 10,        2.5, 46.2,         2.5, 53.8],
    "Oak"               : [0.055,   30,  2.0, 10,        2.5, 45.1,         2.8, 53.9],    
}

treeDict_Label = {
    "TD" : 0,
    "DT" : 1,
    "Dc" : 2,
    "FD" : 3,
    "SubG_n"    : 4,
    "SubG_PLd0" : 5,
    "OvG_n"     : 6,
    "OvG_PLd0"  : 7,    
}

###################################################################
def test_freq_range(f):
    if (f<20e9 and f>0.4e9):
        return True
    else:
        print("Azevedo Santos Model : Freq out of model range")
        return False
    
def get_k1(f=0):
    fGHz = f/1e9
    return (-0.0011*(fGHz**2) + 0.61*fGHz + 2.84)

def get_m(f=0):
    fGHz = f/1e9
    return (3.1*math.exp(1.173*((1/(2.4**0.5))-(1/(fGHz**0.5)))) -1)/10


def get_PLE(TD=0, Dc=0,f=0):
    if test_freq_range(f):
        return get_k1(f) *TD*Dc + 2.27
    return 0

def get_PLE_tree(treeName = "Pine" ,f=0):
    TD = (treeDict[treeName])[treeDict_Label["TD"]]
    Dc = (treeDict[treeName])[treeDict_Label["Dc"]]
    if test_freq_range(f):
        return get_k1(f) *(TD*Dc) + 2.27
    return 0    


def get_PLd0(FD=0, d0=5, f=0):
    if test_freq_range(f):
        return logPL.path_loss(d=d0, f =f, n=2) + get_m(f)*(FD-15) +1
    return 0

def get_PLd0_tree(treeName = "Pine" ,f=0, d0=5):
    FD = (treeDict[treeName])[treeDict_Label["FD"]]
    if test_freq_range(f):
        return logPL.path_loss(d=d0, f =f, n=2) + get_m(f)*(FD-15) +1
    return 0


def path_loss(d=0,TD=0,Dc=0,FD=0,f=0,d0=5):
    if test_freq_range(f):
        PLE = get_PLE(TD, Dc,f)
        PLd0= get_PLd0(FD, d0, f)
        return logPL.path_loss_PLd0(d=d, PLd0=PLd0,d0=d0, n=PLE)
    return 0

def path_loss_tree(d=0,treeName = "Pine" ,f=0,d0=5):
    if test_freq_range(f):
        TD = (treeDict[treeName])[treeDict_Label["TD"]]
        Dc = (treeDict[treeName])[treeDict_Label["Dc"]]
        FD = (treeDict[treeName])[treeDict_Label["FD"]]
        
        PLE = get_PLE(TD, Dc,f)
        PLd0= get_PLd0(FD, d0, f)
        return logPL.path_loss_PLd0(d=d, PLd0=PLd0,d0=d0, n=PLE)
    return 0


def path_loss_distance_tree(PL=0,treeName = "Pine" ,f=0,d0=5):
    if test_freq_range(f):
        TD = (treeDict[treeName])[treeDict_Label["TD"]]
        Dc = (treeDict[treeName])[treeDict_Label["Dc"]]
        FD = (treeDict[treeName])[treeDict_Label["FD"]]
        
        PLE = get_PLE(TD, Dc,f)
        PLd0= get_PLd0(FD, d0, f) 
        return logPL.path_loss_distance_PLd0(PL=PL, PLd0=PLd0, d0=d0,n=PLE)
    return 0
  
  
if __name__ == '__main__':
    treeName = "Juniperus cedrus"
    PLE = get_PLE_tree(treeName = treeName ,f=0.87e9)
    print(get_PLd0_tree(treeName = treeName, d0=5,f=0.87e9))
    print(logPL.path_loss(d=5,f = 0.87e9, n=PLE))
    print(logPL.path_loss(d=5,f = 0.87e9, n=2))
    #print(get_PLE_tree(treeName = treeName ,f=0.87e9))
    #print(get_PLd0_tree(treeName = treeName, d0=5,f=0.87e9))
    
    #print(get_PLE_tree(treeName = treeName ,f=2.4e9))
    #print(get_PLd0_tree(treeName = treeName , d0=5,f=2.4e9))

