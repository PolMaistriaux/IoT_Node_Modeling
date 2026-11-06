import numpy as np
import sys
import os

from ..Node_description import *


# Process node impact factor (in kgCO2 eq.)

kgCO2_p_mm2_n65 = 0.94/100
kgCO2_p_mm2_n45 = 1.03/100
kgCO2_p_mm2_n40 = 1.06/100
kgCO2_p_mm2_n28 = 1.23/100
kgCO2_p_mm2_n20 = 1.23/100
kgCO2_p_mm2_n14 = 1.40/100

Base_MCU_Clock_freq = 32

Base_MCU_Voltage    = 3.3

############################
# Apollo 3 
############################
MCU_Apollo3_component = Component(name="Apollo3", category = "Processing",
                            v      =Base_MCU_Voltage,
                            i_sleep=0.05) #4.5e-3

MCU_Apollo3_mm2    = 3.37*3.25
MCU_Apollo3_CFemb  = MCU_Apollo3_mm2 * kgCO2_p_mm2_n40

#MCU : Apollo3
    #6 µA/MHz executing from FLASH or RAM at 3.3 V
    #1 µA deep sleep mode (BLE in shutdown) with RTC at 3.3 V

MCU_Apollo3_state_active  = Digital_Processing_State("Active"      ,i_per_MHz = {1.8 : 0.018, 3.3 : 0.010},freq_MHz=Base_MCU_Clock_freq,cycle = None)

MCU_Apollo3_component.add_state(MCU_Apollo3_state_active)

###############################################
# Based on  STM32 L4 datasheet, coremark ex
###############################################

MCU_STM32L4_component = Component(name="STM32L4", category = "Processing",
                            v      =Base_MCU_Voltage,
                            i_sleep=6.9e-3) #4.5e-3


MCU_STM32L4_mm2   = 3.132 * 3.127
MCU_STM32L4_CFemb = MCU_STM32L4_mm2 * kgCO2_p_mm2_n65 

MCU_STM32L4_state_active  = Digital_Processing_State("Active"      ,i_per_MHz = 0.114,freq_MHz=Base_MCU_Clock_freq,cycle = None)

MCU_STM32L4_component.add_state(MCU_STM32L4_state_active)

###############################################
# Based on  nRF52840 datasheet, coremark ex on LDO
###############################################
MCU_nRF52840_Clock_freq = 32 #MHz

MCU_nRF52840_component = Component(name="nRF52840",category = "Processing",
                            v      =Base_MCU_Voltage,
                            i_sleep=3.16e-3)

MCU_nRF52840_mm2   = 3.5*3.6
MCU_nRF52840_CFemb = MCU_nRF52840_mm2 * (kgCO2_p_mm2_n65+kgCO2_p_mm2_n45)/2

MCU_nRF52840_state_active  = Digital_Processing_State("Active"      ,i_per_MHz = (6.3/64),freq_MHz=Base_MCU_Clock_freq,cycle = None) # Assuming the LDO

MCU_nRF52840_component.add_state(MCU_nRF52840_state_active)

############################
# MCU registry
############################

MCU_components = {
    "Apollo3": MCU_Apollo3_component,
    "STM32L4": MCU_STM32L4_component,
    "nRF52840": MCU_nRF52840_component,
}

MCU_CFemb = {
    "Apollo3": MCU_Apollo3_CFemb,
    "STM32L4": MCU_STM32L4_CFemb,
    "nRF52840": MCU_nRF52840_CFemb,
}

