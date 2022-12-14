import numpy as np
import sys
import os
sys.path.append(os.path.abspath("../Energy_model"))

import Energy_node as eNode

#MCU : Apollo3
    #6 µA/MHz executing from FLASH or RAM at 3.3 V
    #1 µA deep sleep mode (BLE in shutdown) with RTC at 3.3 V

MCU_activCur_1V8  = 0.970
MCU_sleepCur_1V8  = 0.0027
MCU_voltage_1V8   = 1.8

MCU_activCur_3V3  = 0.573
MCU_sleepCur_3V3  = 0.0027216100533922765
MCU_voltage_3V3   = 3.3

Clock_Freq = 48 #MHz
MCU_activCur_Data  = 10.3e-3 * Clock_Freq
MCU_sleepCur_Data  = (2.3e-3+4.1e-3)/2
MCU_voltage_Data   = 3.3


############################
#3.3V 
############################

apollo_module_3V3 = eNode.Node_module(name="Apollo3",
                            v      =MCU_voltage_3V3,
                            i_sleep=MCU_sleepCur_3V3)
apollo_state_active_3V3  = eNode.Module_state("Active",i = MCU_activCur_3V3,duration = None)
apollo_module_3V3.add_state(apollo_state_active_3V3)

############################
#1.8V
############################

apollo_module_1V8 = eNode.Node_module(name="Apollo3",
                            v      =MCU_voltage_1V8,
                            i_sleep=MCU_sleepCur_1V8)
apollo_state_active_1V8  = eNode.Module_state("Active",i = MCU_activCur_1V8,duration = None)
apollo_module_1V8.add_state(apollo_state_active_1V8)

############################
#3.3V from datasheet
############################

apollo_module_Data = eNode.Node_module(name="Apollo3",
                            v      =MCU_voltage_3V3,
                            i_sleep=MCU_sleepCur_Data)
apollo_state_active_Data  = eNode.Module_state("Active",i = MCU_activCur_Data,duration = None)
apollo_module_Data.add_state(apollo_state_active_Data)