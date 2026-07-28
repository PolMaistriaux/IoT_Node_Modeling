
import math
import numpy as np

import inspect
import importlib

import scipy.interpolate
from scipy import stats

######################
# NCF functions
######################

def ncf_ft(alpha = 0.5, area_ratio  = 1, power_ratio = 1 ,print=False):
    return (alpha * area_ratio ) + ( (1-alpha) * power_ratio )


def ncf_fw(alpha = 0.5, area_ratio  = 1, energy_ratio = 1 ,print=False):
    return (alpha * area_ratio ) + ( (1-alpha) * energy_ratio )

######################
# ASI function  -- Speedup related
######################

def asi_function(alpha = 0.5, area_ratio  = 1, power_ratio = 1 ,print=False):

    return (1- (alpha * area_ratio))/( (1 - alpha) * power_ratio)


def asi_critical_alpha(area_ratio, power_ratio, speedup):
    """Alpha at which NCF_ratio == 1 (breakeven).
    Only meaningful in the classic accelerator case A_ratio>1, E_ratio<1
    (or vice versa); returns NaN when A_ratio==E_ratio==1 (degenerate)."""
    index_speedup     = np.where(speedup <= 1)
    inv_index_speedup = np.where(speedup > 1)
    res = np.full(area_ratio.shape, np.nan)
    if index_speedup[0].size > 0:
        res[index_speedup] = (1-power_ratio[index_speedup])/(area_ratio[index_speedup]-power_ratio[index_speedup])
    if inv_index_speedup[0].size > 0:   
        energy_ratio = power_ratio[inv_index_speedup]/speedup[inv_index_speedup]       
        res[inv_index_speedup] = (1-energy_ratio)/(area_ratio[inv_index_speedup]-energy_ratio)

    return res


def asi_classify(asi = 1, speedup = 1):
    """Region classification, alpha-independent:
    'strong'  : wins on both axes -> sustainable for ALL alpha
    'unsust'  : loses on both axes -> unsustainable for ALL alpha
    'weak'    : trade-off -> depends on alpha (the expected accelerator case)
    """
    both_better = (asi > 1.0) & (asi > (1/speedup))
    both_worse  = (asi <= 1.0) & (asi <= (1/speedup))
    region = np.full(asi.shape, 'weak', dtype=object)
    region[both_better] = 'strong'
    region[both_worse] = 'unsust'
    return region


######################
# SoA scaling function
######################
def scale_area (area= 1, nfft_ref = 1, nfft = 1, acc_type ="Memory-b"):
    area_scaled = np.copy(area)
    for i,this_area in enumerate(area):
        if acc_type[i].startswith("Mem"):
            area_scaled[i] = area[i] * nfft_ref / nfft[i]
        elif acc_type[i].startswith("Pip"):
            area_scaled[i] = area[i] * (nfft_ref*np.log2(nfft_ref)) / (nfft[i]*np.log2(nfft[i]))
    return area_scaled

def scale_latency (latency= 1, nfft_ref = 1, nfft = 1, acc_type ="Memory-b"):
    latency_scaled = np.copy(latency)
    for i,this_area in enumerate(latency):
        if acc_type[i].startswith("Mem"):
            latency_scaled[i] = latency[i] * (nfft_ref*np.log2(nfft_ref)) / (nfft[i]*np.log2(nfft[i])) 
        elif acc_type[i].startswith("Pip"):
            latency_scaled[i] = latency[i] * nfft_ref / nfft[i]
    return latency_scaled


######################
# Architecture exploration
######################
nFFT = 4096
lFFT = int(np.log2(nFFT))

baseline_area    = 10
baseline_energy  = 4096* 5.85e-9
baseline_latency = 4096* 80
baseline_power   = baseline_energy / baseline_latency

sp_mem_size  = np.array([4096   ,   2048  ,  1024   , 512    ,  256     ,  128   ] )                 
sp_mem_area  = np.array([0.0945 ,   0.0563,  0.0327 , 0.0202 ,  0.0152  ,  0.0098] )                 
sp_mem_e     = np.array([20.366 ,   14.951,  11.484 , 10.045 ,  4.04    ,  3.814 ] ) *1.2 * 1e-3                 


dp_mem_size  = np.array([4096   ,   2048  ,  1024   , 512    ,  256    ,  128    ] )                 
dp_mem_area  = np.array([0.1984 ,   0.1040,  0.0567 , 0.0371 ,  0.0159 ,  0.0111 ] )                 
dp_mem_e     = np.array([19.65  ,   16.105,  14.325 , 12.23  ,  5.047  ,  4.365  ] ) *1.2 * 1e-3             

half_bf_area = 0.012258/2
cmult_e      = 16*1e-3  



paraLevel     = np.array([1 , 2 , 4 , 8 ,  16 ])
pipeLevel     = np.array([1 , 2 , 3 , 4 ,  5 ])
paraPipeLevel = np.array([1 , 1 , 2 , 3 ,  4 ])

arch_Dim = max(len(paraLevel),len(pipeLevel),len(paraPipeLevel))

Mem_type = 4

if (len(paraLevel) != len(pipeLevel)) or (len(paraLevel) != len(paraPipeLevel)):
    print("Architecture parameters of different sizes, will cause issue")
    raise ValueError


# The three different equations represent the use of a single port, two single port, or a dual-port

#Based on parallelism level
para_theor_Area     = np.zeros((len(paraLevel),Mem_type))
para_theor_Latency  = np.zeros((len(paraLevel),Mem_type))
para_theor_Energy   = np.zeros((len(paraLevel),Mem_type))
for i, paraLv in enumerate(paraLevel):
    para_theor_Area    [i] = np.array([(sp_mem_area[i]  +half_bf_area)*paraLv      , (sp_mem_area[i]*2+half_bf_area)*paraLv  , (2*sp_mem_area[i+1]  +half_bf_area)*paraLv       , (dp_mem_area[i]  +half_bf_area)*paraLv        ]   )
    para_theor_Latency [i] = np.array([ nFFT*lFFT*2/paraLv                         ,  nFFT*lFFT/paraLv                       ,  nFFT*lFFT/paraLv                                ,  nFFT*lFFT/paraLv                               ]   )
    para_theor_Energy  [i] = np.array([(cmult_e/2+sp_mem_e[i]*2)*nFFT*lFFT         , (cmult_e/2+sp_mem_e[i]*2)*nFFT*lFFT     , (cmult_e/2+sp_mem_e[i+1]*2)*nFFT*lFFT            , (cmult_e/2+dp_mem_e[i]*2)*nFFT*lFFT             ]   )*1e-9 
    

#Based on pipeline level
pipe_theor_Area     = np.zeros((len(pipeLevel),Mem_type))
pipe_theor_Latency  = np.zeros((len(pipeLevel),Mem_type))
pipe_theor_Energy   = np.zeros((len(pipeLevel),Mem_type))
for i, pipeLv in enumerate(pipeLevel):
    pipe_theor_Area    [i,:] = np.array([sp_mem_area[0] + (half_bf_area*pipeLv)          , sp_mem_area[0]*2 + (half_bf_area*pipeLv)        ,   (2*sp_mem_area[1]) + (half_bf_area*pipeLv)         ,  dp_mem_area[0] + (half_bf_area*pipeLv)      ] )    
    pipe_theor_Latency [i,:] = np.array([ nFFT*lFFT*2/pipeLv                             ,  nFFT*lFFT/pipeLv                               ,    nFFT*lFFT/pipeLv                                  ,  nFFT*lFFT/pipeLv                              ] )              
    pipe_theor_Energy  [i,:] = np.array([ nFFT*lFFT*(cmult_e/2 +(sp_mem_e[0]*2/pipeLv))  , nFFT*lFFT*(cmult_e/2 +(sp_mem_e[0]*2/pipeLv))   ,    nFFT*lFFT*(cmult_e/2 +(sp_mem_e[1]*2/pipeLv))     , nFFT*lFFT*(cmult_e/2 +(dp_mem_e[0]*2/pipeLv))  ] )  *1e-9           
    

#Based on pipeline level
pipePara_theor_Area     = np.zeros((len(paraPipeLevel),Mem_type))
pipePara_theor_Latency  = np.zeros((len(paraPipeLevel),Mem_type))
pipePara_theor_Energy   = np.zeros((len(paraPipeLevel),Mem_type))
for i, ppLv in enumerate(paraPipeLevel):
    pipePara_theor_Area    [i] = np.array([(sp_mem_area[i]  +half_bf_area*ppLv)*paraLevel[i]      , (sp_mem_area[i]*2  +half_bf_area*ppLv)*paraLevel[i]   , (2*sp_mem_area[i+1]  +half_bf_area*ppLv)*paraLevel[i]   ,  (dp_mem_area[i]  +half_bf_area*ppLv)*paraLevel[i]   ]  )   
    pipePara_theor_Latency [i] = np.array([ (nFFT/paraLevel[i])*(lFFT/ppLv)*2                     , (nFFT/paraLevel[i])*(lFFT/ppLv)                       ,  (nFFT/paraLevel[i])*(lFFT/ppLv)                        ,  (nFFT/paraLevel[i])*(lFFT/ppLv)                       ]  )            
    pipePara_theor_Energy  [i] = np.array([ nFFT*lFFT*(cmult_e/2 +(sp_mem_e[i]*2/ppLv))           , nFFT*lFFT*(cmult_e/2 +(sp_mem_e[i]*2/ppLv))           ,  nFFT*lFFT*(cmult_e/2 +(sp_mem_e[i+1]*2/ppLv))          , nFFT*lFFT*(cmult_e/2 +(dp_mem_e[i]*2/ppLv))            ]  )    *1e-9      
   


