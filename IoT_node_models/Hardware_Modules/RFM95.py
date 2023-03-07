import numpy as np
import sys
import os
sys.path.append(os.path.abspath("../Energy_model"))

from IoT_node_models.Energy_model import Energy_node as eNode


I_PABoost_3V3 = np.array([ 37.42, 38.89, 40.26, 41.49, 42.88, 44.48, 45.99, 47.83, 50.15, 52.40, 55.73, 59.31, 63.70, 70.12, 76.86, 86.23, 88.82, 96.49,105.58]) #86.23
#I_PABoost_3V3 = np.array([40.25, 42.16, 44.25, 46.15, 48.35, 50.95, 53.35, 56.15, 59.65, 63.05, 67.45, 71.35, 75.90, 80.90, 86.70, 94.20, 100.70, 110.30, 119.05])
I_PABoost_1V8 = np.array([38.00 ,39.46 ,41.35 ,43.18 ,45.29 ,47.74 ,50.23 ,52.63 ,55.91 ,59.35 ,62.69 ,66.47 ,70.45 ,74.40 ,79.43 ,81.18 ,80.91  ,81.08  ,81.16])

PTX_PABOOST_configured  = np.array([2 ,3 ,4 ,5 ,6 ,7 ,8 ,9 ,10 ,11 ,12 ,13 ,14 ,15   ,16 ,17   ,18   ,19   ,20   ])
PTX_PABOOST_3V3         = np.array([2 ,3 ,4 ,5 ,6 ,7 ,8 ,9 ,10 ,11 ,12 ,13 ,14 ,15   ,16 ,16.5 ,17.0 ,17.5 ,18.0 ])
PTX_PABOOST_1V8         = np.array([2 ,3 ,4 ,5 ,6 ,7 ,8 ,9 ,10 ,11 ,12 ,13 ,14 ,14.5 ,15 ,15.5 ,15.5 ,15.5 ,15.5 ])

I_PARFO_3V3 = np.array([20.0008, 21.2920, 22.2228, 23.3346, 24.547,  25.7569, 27.0318, 28.2380, 29.195,  30.0716, 30.77,   31.5083, 32.5543, 33.7856, 35.8903, 39.40734])
I_PARFO_1V8 = np.array([14.415,  14.932,  15.429,  15.973,  16.489,  16.930,  17.395,  17.825,  18.214,  18.660,  19.195,  19.825,  20.545,  21.154,  21.704,  22.133 ])

PTX_RFO_configured  = np.array([0, 1, 2 ,3 ,4 ,5 ,6 ,7 ,8 ,9 ,10 ,11 ,12 ,13 ,14 ,15])


I_Data   = np.array([87, 120])
PTX_Data = np.array([17, 20])

I_RX_3V3  = 11.28
I_RX_1V8  = 10.94
I_RX_Data = 11.5

I_TX_3V3 = 40
I_TX_1V8 = 38

I_Sleep_3V3  = 0.0006057300682635614
I_Sleep_1V8  = 0.00031
I_Sleep_Data = 0.2e-3

TX_duration = 0.5
RX_duration = 0.5

MCU_RFM_duration = 0.20496384+0.10125312 

############################
#3.3V
############################

radio_module_3V3 = eNode.Node_module(name="LoRa radio",
                            v=3.3,
                            i_sleep=I_Sleep_3V3)
radio_state_TX_3V3 = eNode.Module_state("TX",i = I_TX_3V3,duration = None)
radio_state_RX_3V3 = eNode.Module_state("RX",i = I_RX_3V3,duration = None)
radio_module_3V3.add_state(radio_state_TX_3V3)
radio_module_3V3.add_state(radio_state_RX_3V3)

############################
#1.8V
############################

radio_module_1V8 = eNode.Node_module(name="LoRa radio",
                            v=1.8,
                            i_sleep=I_Sleep_1V8)
radio_state_TX_1V8 = eNode.Module_state("TX",i = I_TX_1V8,duration = None)
radio_state_RX_1V8 = eNode.Module_state("RX",i = I_RX_1V8,duration = None)
radio_module_1V8.add_state(radio_state_TX_1V8)
radio_module_1V8.add_state(radio_state_RX_1V8)

############################
#3.3V from datasheet
############################
radio_module_Data = eNode.Node_module(name="LoRa radio",
                            v=3.3,
                            i_sleep=I_Sleep_Data)
radio_state_TX_Data = eNode.Module_state("TX",i = I_TX_3V3,duration = None)
radio_state_RX_Data = eNode.Module_state("RX",i = I_RX_3V3,duration = None)
radio_module_Data.add_state(radio_state_TX_Data)
radio_module_Data.add_state(radio_state_RX_Data)