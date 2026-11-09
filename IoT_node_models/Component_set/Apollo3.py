import numpy as np
import sys
import os

from ..Node_description import *

#MCU : Apollo3
    #6 µA/MHz executing from FLASH or RAM at 3.3 V
    #1 µA deep sleep mode (BLE in shutdown) with RTC at 3.3 V

# Measured currents {supply voltage (V): current (mA)}
MCU_activCur  = {1.8 : 0.970, 3.3 : 0.573}
MCU_sleepCur  = {1.8 : 0.0027, 3.3 : 0.0027216100533922765}
MCU_voltage   = 3.3   # Default supply voltage, use component.set_v() to switch

Clock_Freq = 48 #MHz
MCU_activCur_Data  = 10.3e-3 * Clock_Freq
MCU_sleepCur_Data  = (2.3e-3+4.1e-3)/2
MCU_voltage_Data   = 3.3


############################
# Measured (1.8V / 3.3V)
############################

apollo_component = Component(name="Apollo3",category="Processing",
                            v      =MCU_voltage,
                            i_sleep=MCU_sleepCur )
apollo_state_active  = State("Active",i = MCU_activCur,duration = None)
apollo_component.add_state(apollo_state_active)

############################
#3.3V from datasheet
############################

apollo_component_Data = Component(name="Apollo3",category="Processing",
                            v      =MCU_voltage_Data,
                            i_sleep=MCU_sleepCur_Data)
apollo_state_active_Data  = State("Active",i = MCU_activCur_Data,duration = None)
apollo_component_Data.add_state(apollo_state_active_Data)

############################
# Backward-compatible aliases (same objects, voltage selected with set_v)
############################
apollo_component_3V3    = apollo_component
apollo_state_active_3V3 = apollo_state_active
apollo_component_1V8    = apollo_component
apollo_state_active_1V8 = apollo_state_active
