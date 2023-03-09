import numpy as np
import sys
import os
sys.path.append(os.path.abspath("../Energy_model"))

from IoT_node_models.Energy_model.Node_profile import *

#BME680 no AI: AVERAGE POWER
BME_sleepCur_3V3 = 0.032796386921874914#0.15e-3 #0.15e-3 #
BME_sleepCur_1V8 = 0.0005              #0.037   with EVB
BME_sleepCur_Data= 0.032796386921874914 
BME_voltage_3V3  = 3.3
BME_voltage_1V8  = 1.8
    #Temperature only
T_activCur_3V3    = 0.45703
T_activCur_1V8    = 0.48966
T_duration        = 4.14e-3

    #Pressur  only
P_activCur_3V3    = 0.79926
P_activCur_1V8    = 0.83133
P_duration        = 16.26e-3

    #Humidity only
H_activCur_3V3    = 0.39126
H_activCur_1V8    = 0.42402
H_duration        = 32e-3
    #Gas only
G_activCur_3V3    = 11.964
G_activCur_1V8    = 11.982
G_duration        = 100.74e-3
    #TPH:
TPH_activCur_3V3  = 0.52251
TPH_activCur_1V8  = 0.55331
TPH_duration      = 52.45e-3

TPH_activCur_Data = 3.7e-3
TPH_duration_Data = 1
    # TPHG
TPHG_activCur_3V3  = 11565.80536855e-3#8.006
TPHG_activCur_1V8  = 8.04474
TPHG_duration      = 2030.46912e-3 #154.7e-3

TPHG_activCur_Data = 12
TPHG_duration_Data = 2

MCU_BME_duration = 152.86e-3
MCU_FWI_duration = 1.5e-3
MCU_I2C          = 106.2e-3 
MCU_BME_TPHG     = 2000-3
MCU_BME_TPH      = 158.7e-3

############################
#3.3V
############################
bme_module_3V3   = Node_module(name="BME680",
                            v=BME_voltage_3V3,
                            i_sleep=BME_sleepCur_3V3)
bme_state_T_3V3    = Module_state("T", i = T_activCur_3V3,   duration = T_duration)
bme_state_P_3V3    = Module_state("P", i = P_activCur_3V3,   duration = P_duration)
bme_state_H_3V3    = Module_state("H", i = H_activCur_3V3,   duration = H_duration)
bme_state_G_3V3    = Module_state("G", i = G_activCur_3V3,   duration = G_duration)
bme_state_TPH_3V3  = Module_state("TPH", i = TPH_activCur_3V3, duration = TPH_duration)
bme_state_TPHG_3V3 = Module_state("TPHG",i = TPHG_activCur_3V3,duration = TPHG_duration)

bme_module_3V3.add_state(bme_state_T_3V3)
bme_module_3V3.add_state(bme_state_P_3V3)
bme_module_3V3.add_state(bme_state_H_3V3)
bme_module_3V3.add_state(bme_state_G_3V3)
bme_module_3V3.add_state(bme_state_TPH_3V3)
bme_module_3V3.add_state(bme_state_TPHG_3V3)

############################
#1.8V
############################
bme_module_1V8   = Node_module(name="BME680",
                            v=BME_voltage_1V8,
                            i_sleep=BME_sleepCur_1V8)
bme_state_T_1V8    = Module_state("T", i = T_activCur_1V8,   duration = T_duration)
bme_state_P_1V8    = Module_state("P", i = P_activCur_1V8,   duration = P_duration)
bme_state_H_1V8    = Module_state("H", i = H_activCur_1V8,   duration = H_duration)
bme_state_G_1V8    = Module_state("G", i = G_activCur_1V8,   duration = G_duration)
bme_state_TPH_1V8  = Module_state("TPH", i = TPH_activCur_1V8, duration = TPH_duration)
bme_state_TPHG_1V8 = Module_state("TPHG",i = TPHG_activCur_1V8,duration = TPHG_duration)

bme_module_1V8.add_state(bme_state_T_1V8)
bme_module_1V8.add_state(bme_state_P_1V8)
bme_module_1V8.add_state(bme_state_H_1V8)
bme_module_1V8.add_state(bme_state_G_1V8)
bme_module_1V8.add_state(bme_state_TPH_1V8)
bme_module_1V8.add_state(bme_state_TPHG_1V8)

############################
#3.3V from datasheet
############################
bme_module_Data  = Node_module(name="BME680",
                            v=BME_voltage_3V3,
                            i_sleep=BME_sleepCur_Data)
bme_state_TPHG_Data = Module_state("TPHG",i = TPHG_activCur_Data,duration = TPHG_duration_Data)
bme_module_Data.add_state(bme_state_TPHG_Data)

