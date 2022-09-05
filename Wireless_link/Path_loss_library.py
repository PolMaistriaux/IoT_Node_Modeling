import math
import numpy as np
import sys
sys.path.insert(0, './Path_loss_model')

import logNormal_PL as logPL
import Azevedo_Santos_PL as AzSaPL
import Various_models as vmPL


modelList = [
    ["FPL"                   , [0]                  ],
    ["PLE"                   , [2.8]                ],
    ["PLEref"                , [7.7,1,3.76]         ],
    ["2Ray"                  , [3,2]                ],
    ["Azevedo"               , ["Small pines"]      ],
    ["Azevedo"               , ["Pine"]             ],
    ["Callebaut"             , [0]                  ],
    ["Silva"                 , [3]                  ],
    ["Jiang"                 , [0.9]                ],
    ["COST235"               , ["FPL"]              ],
    ["Weissberger"           , ["FPL"]              ],
    ["ITUR"                  , ["FPL"]              ],
    ["FITUR"                 , ["FPL"]              ],
    ["LITUR"                 , ["FPL"]              ]]

###################################################################
def path_loss_All_Model(d=1, f = 8e8):
    name   = []
    result = np.zeros((len(modelList),1))
    index = 0
    for model in modelList:
        if isinstance((model[1])[0],str):
            name.append(model[0]+" - "+(model[1])[0])
        else:
            name.append(model[0])
        result[index]=path_loss_Model(d=d, f = f, model=model[0], arg=model[1:][0])[0]
        index +=1
    return name, result 
###################################################################
   
def path_loss_Model(d=1, f = 8e8, model = "FPL", arg=[]):
    arg_index = 0
    if model == "FPL":
        PL = logPL.path_loss(d,f,2)
    elif model == "PLE":
        PL = logPL.path_loss(d,f,arg[arg_index])
    elif model == "PLEref":
        PL = logPL.path_loss_PLd0(d,arg[arg_index],arg[arg_index+1],arg[arg_index+2])
    elif model == "2Ray":
        PL = vmPL.twoRay(d,arg[arg_index],arg[arg_index+1])
        arg_index +=2
    elif model == "Azevedo":
        PL = AzSaPL.path_loss_tree(d=d,treeName = arg[arg_index] ,f=f)
        arg_index +=1
    elif model == "Callebaut":
        PL = vmPL.Callebaut_lowH(d,f)
    elif model == "Silva":
        PL = vmPL.Silva_tropical(d=d, h_tx=arg[arg_index] ,f=f, isCloseTrunk=True)
        arg_index +=1
    elif model == "Jiang":
        PL = vmPL.Jiang_NDVI(d=d, NDVI=arg[arg_index] ,f=f)
        arg_index +=1
    elif model == "Ibdah":
        PL = vmPL.Ibdah_inLeaf(d=d, f=f)
    elif model == "COST235":
        PL = base_Pl_model(d,f,arg[arg_index]) + vmPL.COST235(d=d,f=f)
    elif model == "Weissberger":
        PL = base_Pl_model(d,f,arg[arg_index]) + vmPL.Weissberger(d=d,f=f)
    elif model == "ITUR":
        PL = base_Pl_model(d,f,arg[arg_index]) + vmPL.ITUR(d=d,f=f)
    elif model == "FITUR":
        PL = base_Pl_model(d,f,arg[arg_index]) + vmPL.FITUR(d=d,f=f)
    elif model == "LITUR":
        PL = base_Pl_model(d,f,arg[arg_index]) + vmPL.LITUR(d=d,f=f)
    else:
        print("Path loss: PL : Model not found : " +model )
        PL = 0
    return PL, arg_index
###################################################################

def path_loss_Model_distance(PL=0, f = 8e8, model = "FPL", arg=[]):
    arg_index = 0
    if model == "FPL":
        distance = logPL.path_loss_distance(PL,f,2)
    elif model == "PLE":
        distance = logPL.path_loss_distance(PL,f, arg[arg_index])
    elif model == "2Ray":
        distance = vmPL.twoRay_distance(PL,f,arg[arg_index],arg[arg_index+1])
        arg_index +=2
    elif model == "Azevedo":
        distance = AzSaPL.path_loss_distance_tree(PL=PL,treeName = arg[arg_index] ,f=f)
    elif model == "Callebaut":
         distance = vmPL.Callebaut_lowH_distance(PL,f)
    elif model == "Silva":
         distance = vmPL.Silva_tropical_distance(PL=PL, h_tx=arg[arg_index] ,f=f, isCloseTrunk=True)
         arg_index +=1
    elif model == "Jiang":
        distance = vmPL.Jiang_NDVI_distance(PL=PL, NDVI=arg[arg_index] ,f=f)
        arg_index +=1
    else:
        print("Path loss: range : model not found : " +model )
        distance = 0
    return distance, arg_index
###################################################################

def Switch_range_model(d=1, f = 8e8, from_Model = "FPL", to_Model="PLE", arg=[]):
    PL, arg_index = path_loss_Model(d, f, from_Model, arg)
    arg = arg[arg_index:]
    new_distance,arg_index = path_loss_Model_distance(PL, f, to_Model, arg)    
    return new_distance
###################################################################

def base_Pl_model(d=0,f=0,model="FPL"):
    if model == "2Ray":
        return vmPL.twoRay(d)
    else:
        return logPL.path_loss(d,f,2)
###################################################################

if __name__ == '__main__':
    print(Switch_range_model(d=400, f = 2.4e9, from_Model = "FPL", to_Model= "PLE", arg=[4]))
    #print(logPL.path_loss_distance(PL=103, fc = 2.4e9, n=2))
    #print(logPL.path_loss_exponent(PL=103, fc = 2.4e9, d = 400))
    #print(logPL.path_loss(d = 5, fc =0.87e9, n=2))
    print(len(modelList))
    for model in modelList:
        print(model)