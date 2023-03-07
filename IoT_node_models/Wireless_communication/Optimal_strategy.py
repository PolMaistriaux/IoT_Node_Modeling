#%%


import numpy as np


k =1.38 * 10**(-23)
T=290
B=125e3
kTB = 10*np.log10(k*T*B) +30 # expressed in dBm

SF     = np.array([7   ,8  ,9    ,10 ,11   ,12 ]) 
PTX    = np.arange(2,21,1) # expressed in dBm

NF = 6
G_TX = 2
G_RX = 2
H = G_TX + G_RX - kTB - NF -10


def find_Opti_SF_PTX(PL,SF_possible=SF,PTX_possible=PTX,H=H,I_PTX=[],verbose=False,NF=NF,G_TX=G_TX,G_RX=G_RX,B=B):
    kT = 10*np.log10(k*T) +30
    kTB = kT + 10*np.log10(B)
    Sensi = kTB + NF + 10 #-2.5*SF
    LB = G_TX + G_RX - Sensi #-10 comes from the Spreading factor 

    E_best_solution = np.inf
    best_solution = [SF_possible[0],PTX_possible[0],E_best_solution]

    sol_found = 0

    for SF in SF_possible:
        for index,PTX_enum in enumerate(PTX_possible):
            if PL <= (LB+2.5*SF+PTX_enum):
                sol_found = sol_found+1
                if np.size(I_PTX)==0:
                    E_trial = (10**(0.5*PTX_enum/10)) * (2**SF)
                else:
                    E_trial = I_PTX[index] * (2**SF)
                if E_best_solution >  E_trial:
                    best_solution[0] = SF
                    best_solution[1] = PTX_enum
                    best_solution[2] = E_trial
                    E_best_solution = E_trial

    if sol_found ==0:
        if verbose:
            print("Careful, not solution found for SF and PTX, out of range")
        return [0,0,0]
    else:
        return best_solution




