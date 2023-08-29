import math
import numpy as np
import sys
import matplotlib.pyplot as plt

 
def time_on_air(Payload,Coding=1,Header=True,DE = None,B = 125e3,SF=np.array([7,8,9,10,11,12]), Bytes=True, verbose = False):
    TSym =( 2**(SF) *(1/B))
    if DE == None:
        DE = TSym>16e-3
    Payload_bits  = Payload*(7*Bytes+1)
    Payload_bits  = Payload_bits -4*SF+16+28-20*(Header==False)            
    N_payload     = np.divide(Payload_bits,4*(SF-2*DE))
    N_payload     = 8+np.maximum(np.ceil(N_payload)* (Coding+4),  0)
    N_preamble    = 4.25 + 8;  
    if(verbose):
        if ((2**(SF) *(1/B) *1000) >16) and DE ==0:
            print("Careful, symbol duration is longer than 16 ms, Low data rate should be used")
        print("Symbol length is %.2f ms"%(2**(SF) *(1/B) *1000))

    if __name__ == '__main__':
        print("Number of symbols in payload +header: %d" %(N_payload) )
        print("Symbol period : %f" %( 2**(SF) *(1/B)))
        print("Preamble duration : %f" %( N_preamble*2**(SF) *(1/B)))
        print("Payload  duration : %f" %( N_payload*2**(SF) *(1/B)))
        print("Total  duration   : %f" %( (N_payload+N_preamble) * 2**(SF) *(1/B)))

    return (N_payload+N_preamble) * 2**(SF) *(1/B)

def data_rate(B = 125e3,SF=12, Bytes=True):
    Rb = SF*B/(2**SF)
    if Bytes:
        return Rb/8
    else:
        return Rb  

#%%%
if __name__ == '__main__':
    Rb = time_on_air(Payload=11,Coding=4,Header=True,DE = 0,B = 125e3,SF=8, Bytes=True)
    print(Rb)
    print(data_rate(B = 125e3,SF=7, Bytes=False))
        

            