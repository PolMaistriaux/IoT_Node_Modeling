import numpy as np
import sys
import os

from ..Node_description import *

# All currents are {supply voltage (V): current (mA)}

#BME680 no AI: AVERAGE POWER
BME_sleepCur     = {3.3 : 0.15e-3, 1.8 : 0.037}   #with EVB     3.3V: 0.032796386921874914   1.8V: 0.0005
BME_sleepCur_Data= 0.15e-3
BME_voltage      = 3.3   # Default supply voltage, use component.set_v() to switch
BME_voltage_Data = 3.3

    #Temperature only
T_activCur        = {3.3 : 0.45703, 1.8 : 0.48966}
T_duration        = 4.14e-3

    #Pressur  only
P_activCur        = {3.3 : 0.79926, 1.8 : 0.83133}
P_duration        = 16.26e-3

    #Humidity only
H_activCur        = {3.3 : 0.39126, 1.8 : 0.42402}
H_duration        = 32e-3
    #Gas only
G_activCur        = {3.3 : 11.964, 1.8 : 11.982}
G_duration        = 100.74e-3
    #TPH:
TPH_activCur      = {3.3 : 0.52251, 1.8 : 0.55331}
TPH_duration      = 52.45e-3

TPH_activCur_Data = 3.7e-3
TPH_duration_Data = 1
    # TPHG
TPHG_activCur     = {3.3 : 11565.80536855e-3, 1.8 : 8.04474}   #3.3V: 8.006
TPHG_duration     = 2030.46912e-3 #154.7e-3

TPHG_activCur_Data = 12
TPHG_duration_Data = 2

MCU_BME_duration = 152.86e-3
MCU_FWI_duration = 1.5e-3
MCU_I2C          = 106.2e-3
MCU_BME_TPHG     = 2000-3
MCU_BME_TPH      = 158.7e-3

############################
# Measured (1.8V / 3.3V)
############################
bme_component   = Component(name="BME680",category="Sensing",
                            v=BME_voltage,
                            i_sleep=BME_sleepCur)
bme_state_T    = State("T",   i = T_activCur,   duration = T_duration)
bme_state_P    = State("P",   i = P_activCur,   duration = P_duration)
bme_state_H    = State("H",   i = H_activCur,   duration = H_duration)
bme_state_G    = State("G",   i = G_activCur,   duration = G_duration)
bme_state_TPH  = State("TPH", i = TPH_activCur, duration = TPH_duration)
bme_state_TPHG = State("TPHG",i = TPHG_activCur,duration = TPHG_duration)

bme_component.add_state(bme_state_T)
bme_component.add_state(bme_state_P)
bme_component.add_state(bme_state_H)
bme_component.add_state(bme_state_G)
bme_component.add_state(bme_state_TPH)
bme_component.add_state(bme_state_TPHG)

############################
#3.3V from datasheet
############################
bme_component_Data  = Component(name="BME680",category="Sensing",
                            v=BME_voltage_Data,
                            i_sleep=BME_sleepCur_Data)
bme_state_TPHG_Data = State("TPHG",i = TPHG_activCur_Data,duration = TPHG_duration_Data)
bme_component_Data.add_state(bme_state_TPHG_Data)

############################
# Backward-compatible aliases (same objects, voltage selected with set_v)
############################
bme_component_3V3 = bme_component_1V8 = bme_component
bme_state_T_3V3   = bme_state_T_1V8   = bme_state_T
bme_state_P_3V3   = bme_state_P_1V8   = bme_state_P
bme_state_H_3V3   = bme_state_H_1V8   = bme_state_H
bme_state_G_3V3   = bme_state_G_1V8   = bme_state_G
bme_state_TPH_3V3 = bme_state_TPH_1V8 = bme_state_TPH
bme_state_TPHG_3V3= bme_state_TPHG_1V8= bme_state_TPHG
