import math
import numpy as np
import sys
import matplotlib.pyplot as plt
import LoRa_library as lora 

    
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
def prob_collision(pkt_size = 1,Tb = 100, Nfc = 3, Nlc = 6, Nnode = 100, d=0.01, Coding=1,prob_SF = (np.array([1,1,1,1,1,1])/6)):
    toa = lora.time_on_air(Payload=pkt_size+9,Coding=Coding,Header=True,DE = None,B = 125e3,SF=np.array([7,8,9,10,11,12]), Bytes=True)
    print(3600/(toa/d))
    print(toa/d)
    TbRestriction  = np.maximum.outer(toa/d,Tb)#toa/(d)   
    N_user = prob_SF*Nnode/Nfc
    G                   = np.divide((np.expand_dims(N_user,axis=1)*np.expand_dims(toa,axis=1)),TbRestriction)
    #G                   = np.divide((np.expand_dims(N_user,axis=1)*np.expand_dims(toa,axis=1)),TbRestriction)
    prob_coll_fl        = 1-np.exp(-2*G)
    prob_coll           = np.matmul(prob_coll_fl.T,prob_SF)

    return prob_coll, TbRestriction

def prob_collision_Poisson(pkt_size = 1,Tb = 100, Nfc = 3, Nlc = 6, Nnode = 100, d=0.01, Coding=1,prob_SF = (np.array([1,1,1,1,1,1])/6)):
    toa = lora.time_on_air(Payload=pkt_size+5,Coding=Coding,Header=True,DE = 0,B = 125e3,SF=np.array([7,8,9,10,11,12]), Bytes=True)
    TbRestriction  = np.maximum.outer(toa/d,Nfc*Tb)#toa/(d)   
    N_user = prob_SF*Nnode
    G                   = np.divide((np.expand_dims(N_user,axis=1))*np.expand_dims(toa,axis=1),TbRestriction)
    prob_coll_fl        = 1-np.exp(-2*G)
    prob_coll           = np.matmul(prob_coll_fl.T,prob_SF)

    return prob_coll, TbRestriction

def prob_collision_Regular(pkt_size = 1,Tb = 100, Nfc = 3, Nlc = 6, Nnode = 100, d=0.01, Coding=1,prob_SF = (np.array([1,1,1,1,1,1])/6)):
    toa = lora.time_on_air(Payload=pkt_size+5,Coding=Coding,Header=True,DE = 0,B = 125e3,SF=np.array([7,8,9,10,11,12]), Bytes=True)
    TbRestriction  = np.maximum.outer(toa/d,Nfc*Tb)#toa/(d)
    prob_coll_fl_2users = np.minimum(np.divide(2*np.expand_dims(toa,axis=1),TbRestriction), 1)
    N_user = prob_SF*Nnode
    prob_coll_fl        = 1 - np.power((1-prob_coll_fl_2users),np.expand_dims(N_user,axis=1))
    prob_coll           = np.matmul(prob_coll_fl.T,prob_SF)
    return prob_coll, TbRestriction

def Pkt_received_for_tb_NoFH_Nnode(pkt_size = 10, Nnode = np.array([100,250,500,1000]), MaxPkt_PHour=2000,dp=10,Nfc = 3, Nlc = 6, d=0.01, Coding=1,prob_SF = (np.array([1,1,1,1,1,1])/6)):
    Pkt_PHour = np.linspace(1,MaxPkt_PHour,int(MaxPkt_PHour/dp))
    Tb = 3600/Pkt_PHour
    maxY=0
    step = 5
    plt.figure(figsize=(10,12))
    for nnode in Nnode:
        pcol, TbRestriction = prob_collision(pkt_size = pkt_size, Tb=Tb,  Nfc = Nfc, Nlc = 6, Nnode = nnode, Coding=Coding,prob_SF=prob_SF,d=d)
        Rate =Nfc*3600*np.matmul((1/TbRestriction).T,prob_SF) 
        Rpkt_Phour_Pnode = (1-pcol)*Rate
        
        plt.plot(Pkt_PHour,Rpkt_Phour_Pnode,label=("# Node: %d"%nnode))
        maxY = np.maximum(np.max(Rpkt_Phour_Pnode),maxY)
    
    plt.yticks(np.arange(0, maxY+step, step)) 
    plt.xticks(np.arange(0, MaxPkt_PHour, 50))
    plt.xlim([0,MaxPkt_PHour])
    plt.ylim([0,maxY+step])
    plt.grid() 
    plt.legend()
    plt.title("Pkt received vs #pkt generated for MAC payload = 10B")
    plt.xlabel("Num. generated packets/hour per node")
    plt.ylabel("Num. received packets/hour per node")
    plt.show()
    return TbRestriction, (1-pcol), Rate

def Pkt_received_for_tb_NoFH_NChannel(pkt_size = 10, Nnode = 500, MaxPkt_PHour=2000,dp=10,Nfc = np.array([1,3,6,9,12]), Nlc = 6, d=0.01, Coding=1,prob_SF = (np.array([1,1,1,1,1,1])/6)):
    Pkt_PHour = np.linspace(1,MaxPkt_PHour,int(MaxPkt_PHour/dp))
    Tb = 3600/Pkt_PHour
    maxY=0
    step = 100
    for nfc in Nfc:
        pcol, TbRestriction = prob_collision(pkt_size = pkt_size, Tb=Tb,  Nfc = nfc, Nlc = 6, Nnode = Nnode, Coding=1,prob_SF=prob_SF,d=d)
        Rpkt_Phour_Pnode = 3600*(1-pcol)*np.matmul((1/TbRestriction).T,prob_SF)
        
        plt.plot(Pkt_PHour,Rpkt_Phour_Pnode,label=("# freq channel: %d"%nfc))
        maxY = np.maximum(np.max(Rpkt_Phour_Pnode),maxY)
    
    
    plt.yticks(np.arange(0, maxY+step, step)) 
    plt.xlim([0,MaxPkt_PHour])
    plt.ylim([0,maxY+step])
    plt.grid()
    plt.title("Pkt received vs #pkt generated for MAC payload = 10B")
    plt.legend()
    plt.xlabel("Num. generated packets/hour per node")
    plt.ylabel("Num. received packets/hour per node")
    plt.show()
    
def PER_for_tb_NoFH_Nnode(pkt_size = 10, Nnode = np.array([100,250,500,1000]), MaxPkt_PHour=2000,dp=10,Nfc = 3, Nlc = 6, d=0.01, Coding=1,prob_SF = (np.array([1,1,1,1,1,1])/6)):
    Pkt_PHour = np.linspace(1,MaxPkt_PHour,int(MaxPkt_PHour/dp))
    Tb = 3600/Pkt_PHour
    maxY=0
    step = 0.1
    for nnode in Nnode:
        pcol, TbRestriction = prob_collision(pkt_size = pkt_size, Tb=Tb,  Nfc = Nfc, Nlc = 6, Nnode = nnode, Coding=1,prob_SF=prob_SF,d=d)
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
    

def PER_for_tb_NoFH_NChannel(pkt_size = 10, Nnode = 500, MaxPkt_PHour=2000,dp=10,Nfc = np.array([1,3,6,9,12]), Nlc = 6, d=0.01, Coding=4/5,prob_SF = (np.array([1,1,1,1,1,1])/6)):
    Pkt_PHour = np.linspace(1,MaxPkt_PHour,int(MaxPkt_PHour/dp))
    Tb = 3600/Pkt_PHour
    maxY=0
    step = 0.1
    for nfc in Nfc:
        pcol, TbRestriction = prob_collision(pkt_size = pkt_size, Tb=Tb,  Nfc = nfc, Nlc = 6, Nnode = Nnode, Coding=4/5,prob_SF=prob_SF,d=d)
        plt.plot(Pkt_PHour,pcol,label=("# freq channel: %d"%nfc))
        maxY = np.maximum(np.max(pcol),maxY)
        
    plt.yticks(np.arange(0, maxY+step, step)) 
    plt.xlim([0,MaxPkt_PHour])
    plt.ylim([0,maxY+step])
    plt.grid()
    plt.title("PER vs #pkt generated for MAC payload = 10B")
    plt.legend()
    plt.xlabel("Num. generated packets/hour per node")
    plt.ylabel("PER")
    plt.show()
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
def prob_collision_minTb(pkt_size = 1, Nfc = 3, Nlc = 6, Nnode = 100, d=0.01, Coding=1,prob_SF = (np.array([1,1,1,1,1,1])/6)):
    toa = lora.time_on_air(Payload=pkt_size+5,Coding=Coding,Header=True,DE = 0,B = 125e3,SF=np.array([7,8,9,10,11,12]), Bytes=True)
    Tb = toa/(d)
    prob_coll_fl_2users = np.minimum(2*toa/Tb, 1)
    prob_coll_fl        = 1 - np.power.outer((1-prob_coll_fl_2users),Nnode/(Nlc)) 
    prob_coll           = np.matmul(prob_coll_fl.T,prob_SF)
    return prob_coll, Tb

def Pkt_received_for_Nnode(pkt_size = np.array([10,30,50]), MaxNnode=3000,dp=10,Nfc = 3, Nlc = 6, d=0.01, Coding=1,prob_SF = (np.array([1,1,1,1,1,1])/6)):
    NnodeVector = np.linspace(0,MaxNnode,int(MaxNnode/dp))
    maxY=0
    step = 100
    for tb in pkt_size:
        pcol, Tb = prob_collision_minTb(pkt_size = tb, Nfc = Nfc, Nlc = Nlc, Nnode = NnodeVector, Coding=4/5,prob_SF=prob_SF,d=d)
        Rpkt_Phour_Pnode = Nfc*3600*(1-pcol)*np.sum(1/Tb)/6
        plt.plot(NnodeVector,Rpkt_Phour_Pnode,label=("MAC Payload: %d Bytes"%tb))
        maxY = np.maximum(np.max(Rpkt_Phour_Pnode),maxY)
        
    plt.yticks(np.arange(0, maxY+step, step)) 
    plt.xlim([0,MaxNnode])
    plt.ylim([0,maxY])
    plt.grid() 
    plt.legend()
    plt.title("PER vs # nodes for MAC payload at max legal throughput")
    plt.xlabel("Number of nodes")
    plt.ylabel("Num. received packets/hour per node")
    plt.show()

    
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
if __name__ == '__main__':
    #prob_SF = np.array([0.19,0.08,0.10,0.14,0.21,0.28])
    prob_SF = np.array([0.2233, 0.0949, 0.1394, 0.1957, 0.1885, 0.1582])
    print(np.sum(prob_SF))
    d=0.01
    pkt_size = 50
    maxNnode = 5000
    MaxPkt_PHour= 500
    Coding = 1
    #Pkt_received_for_Nnode(pkt_size = np.array([10,30,50,70,90]), MaxNnode=3000,dp=10,Nfc = 3, Nlc = 6, d=0.01, Coding=4/5,prob_SF = prob_SF)
    TbRestriction, pncoll, Rate = Pkt_received_for_tb_NoFH_Nnode(pkt_size = pkt_size, Nnode = np.array([250,500,1000,maxNnode]), MaxPkt_PHour=MaxPkt_PHour,dp=1,Nfc = 1, Nlc = 6, d=d, Coding=Coding,prob_SF = prob_SF)
    #Pkt_received_for_tb_NoFH_NChannel(pkt_size = 10, Nnode = 500, MaxPkt_PHour=2000,dp=10,Nfc = np.array([1,3,6,9,12]), Nlc = 6, d=0.01, Coding=4/5,prob_SF = prob_SF)
    #PER_for_tb_NoFH_Nnode(pkt_size = pkt_size, Nnode = np.array([250,500,1000,5000,maxNnode]), MaxPkt_PHour=2000,dp=1,Nfc = 3, Nlc = 6, d=0.01, Coding=Coding,prob_SF = prob_SF) 
    #PER_for_tb_NoFH_NChannel(pkt_size = 10, Nnode = 500, MaxPkt_PHour=2000,dp=10,Nfc = np.array([1,3,6,9,12]), Nlc = 6, d=0.01, Coding=4/5,prob_SF = prob_SF) 
    #█limit = 3*3600/((1/d)*np.min(lora.time_on_air(Payload=10,Coding=1,Header=True,DE = 0,B = 125e3,SF=np.array([7,8,9,10,11,12]), Bytes=True)))
    #print(lora.time_on_air(Payload=10,Coding=1,Header=True,DE = 1,B = 125e3, Bytes=True))