import math
import numpy as np
import sys
import matplotlib.pyplot as plt
import os
sys.path.append(os.getcwd() + '\..')

import LoRa.LoRa_library as lora 
import Energy_model.Node_Energy as energy 
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
def prob_collision(pkt_size,pkt_freq,Nfc=1,Nlc=1,Nnode=100,d=0.01,prob_lc =np.array([1]), timeOnAir=lambda x:x):
    toa = timeOnAir(pkt_size)
    print(toa)
    TbRestriction  = np.maximum.outer(toa/(d),1/pkt_freq)
    prob_coll_fl_2users = np.minimum(np.divide(2*np.expand_dims(toa,axis=1),TbRestriction), 1)
    N_user = prob_lc*Nnode/Nfc
    prob_coll_fl        = 1 - np.power((1-prob_coll_fl_2users),np.expand_dims(N_user,axis=1))
    prob_coll           = np.matmul(prob_coll_fl.T,prob_lc)
    return prob_coll, TbRestriction

def Pkt_received_Freq_vs_Nnode(pkt_size = 10, Nnode = np.array([100,250,500,1000]), MaxPkt_PHour=2000,dp=10,Nfc = 3, Nlc = 6, d=0.01,prob_lc = (np.array([1])),timeOnAir=lambda x:x):
    Pkt_PHour = np.linspace(1,MaxPkt_PHour,int(MaxPkt_PHour/dp))
    pkt_freq= Pkt_PHour/3600
    maxY=0
    step = 100
    plt.figure(figsize=(10,12))
    for nnode in Nnode:
        pcol, TbRestriction = prob_collision(pkt_size = pkt_size,pkt_freq=pkt_freq,  Nfc = Nfc, Nlc = Nlc, Nnode = nnode, prob_lc=prob_lc,timeOnAir=timeOnAir,d=d )
        Rpkt_Phour_Pnode = Nfc*3600*(1-pcol)*np.matmul((1/TbRestriction).T,prob_lc)
        plt.plot(Pkt_PHour,Rpkt_Phour_Pnode,label=("# Node: %d"%nnode))
        maxY = np.maximum(np.max(Rpkt_Phour_Pnode),maxY)
        
    plt.yticks(np.arange(0, maxY+step, step)) 
    plt.xlim([0,MaxPkt_PHour])
    plt.ylim([0,maxY+step])
    plt.grid() 
    plt.legend(fontsize = 15)
    plt.title("Pkt received vs #pkt generated for MAC payload = 10B",fontsize = 15)
    plt.xlabel("Num. generated packets/hour per node",fontsize = 15)
    plt.ylabel("Num. received packets/hour per node",fontsize = 15)
    plt.show()
    return TbRestriction
    
def PER_Freq_vs_Nnode(pkt_size = 10, Nnode = np.array([100,250,500,1000]), MaxPkt_PHour=2000,dp=10,Nfc = 3, Nlc = 6, d=0.01,prob_lc = (np.array([1])),timeOnAir=lambda x:x):
    Pkt_PHour = np.linspace(1,MaxPkt_PHour,int(MaxPkt_PHour/dp))
    pkt_freq= Pkt_PHour/3600
    maxY=0
    step = 0.1
    plt.figure(figsize=(10,12))
    for nnode in Nnode:
        pcol, TbRestriction = prob_collision(pkt_size = pkt_size,pkt_freq=pkt_freq,  Nfc = Nfc, Nlc = Nlc, Nnode = nnode, prob_lc=prob_lc,timeOnAir=timeOnAir,d=d )
        plt.plot(Pkt_PHour,pcol,label=("# Node: %d"%nnode))
        maxY = np.maximum(np.max(pcol),maxY)
        
    plt.yticks(np.arange(0, maxY+step, step)) 
    plt.xlim([0,MaxPkt_PHour])
    plt.ylim([0,maxY+step])
    plt.grid() 
    plt.legend()
    plt.title("PER vs #pkt generated for MAC payload = 10B")
    plt.xlabel("Num. generated packets/hour per node")
    plt.ylabel("PER")
    plt.show()
    return TbRestriction

def Power_Efficiency_vs_Node(pkt_size = 10, Nnode = np.array([100,250,500,1000]), MaxPkt_PHour=2000,dp=10,Nfc = 3, Nlc = 6, d=0.01,prob_lc = (np.array([1])),timeOnAir=lambda x:x):
    nodePower = energy.default_Node()
    Pkt_PHour = np.linspace(1,MaxPkt_PHour,int(MaxPkt_PHour/dp))
    pkt_freq= Pkt_PHour/3600
    maxY=0
    step = 100
    plt.figure(figsize=(10,12))
    for nnode in Nnode:
        pcol, TbRestriction = prob_collision(pkt_size = pkt_size,pkt_freq=pkt_freq,  Nfc = Nfc, Nlc = Nlc, Nnode = nnode, prob_lc=prob_lc,timeOnAir=timeOnAir,d=d )
        Rpkt_Phour_Pnode = Nfc*3600*(1-pcol)*np.matmul((1/TbRestriction).T,prob_lc)
        plt.plot(Pkt_PHour,Rpkt_Phour_Pnode,label=("# Node: %d"%nnode))
        maxY = np.maximum(np.max(Rpkt_Phour_Pnode),maxY)
        
    plt.yticks(np.arange(0, maxY+step, step)) 
    plt.xlim([0,MaxPkt_PHour])
    plt.ylim([0,maxY+step])
    plt.grid() 
    plt.legend(fontsize = 15)
    plt.title("Pkt received vs #pkt generated for MAC payload = 10B",fontsize = 15)
    plt.xlabel("Num. generated packets/hour per node",fontsize = 15)
    plt.ylabel("Num. received packets/hour per node",fontsize = 15)
    plt.show()
    return TbRestriction

    
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
if __name__ == '__main__':
    prob_lc = np.array([0.2233, 0.0949, 0.1394, 0.1957, 0.1885, 0.1582])
    #prob_lc = np.array([1,1,1,1,1,1])/6
    d=0.01
    Coding = 1
    pkt_size = 10
    MaxPkt_PHour = 1200
    #Pkt_received_for_Nnode(pkt_size = np.array([10,30,50,70,90]), MaxNnode=3000,dp=10,Nfc = 3, Nlc = 6, d=0.01, Coding=4/5,prob_SF = prob_SF)
    TbRestriction = PER_Freq_vs_Nnode( pkt_size = pkt_size, Nnode = np.array([250,500,1000,5000]), MaxPkt_PHour=MaxPkt_PHour,dp=1,Nfc = 3, Nlc = 6, d=d,prob_lc = prob_lc,timeOnAir= lora.time_on_air)
    Pkt_received_Freq_vs_Nnode(pkt_size = pkt_size, Nnode = np.array([250,500,1000,5000]), MaxPkt_PHour=MaxPkt_PHour,dp=1,Nfc = 3, Nlc = 6, d=d,prob_lc = prob_lc,timeOnAir= lora.time_on_air) 