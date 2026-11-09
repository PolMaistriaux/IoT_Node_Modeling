import numpy as np
import sys
import os

from ..Node_description import *

Base_Micro_Voltage = 3.3

Micro_ICS40310_component      = Component(name="ICS-40310"              , category = "Sensing", v      =Base_Micro_Voltage, i_sleep=0.000)
Micro_ICS40212_component      = Component(name="ICS-40212"              , category = "Sensing", v      =Base_Micro_Voltage, i_sleep=0.000)
Micro_SPM_component           = Component(name="SPM0408LE5H"            , category = "Sensing", v      =Base_Micro_Voltage, i_sleep=0.000)
Micro_Digital_component       = Component(name="Digital Micro IC"       , category = "Sensing", v      =Base_Micro_Voltage, i_sleep=0.000)
Micro_MP23DB01HP_LP_component = Component(name="MP23DB01HP : Low-Power" , category = "Sensing", v      =Base_Micro_Voltage, i_sleep=0.000)
Micro_MP23DB01HP_component    = Component(name="MP23DB01HP : High-Perf" , category = "Sensing", v      =Base_Micro_Voltage, i_sleep=0.000)


Micro_ICS40310_component      .add_state(State("Active",i = 0.019                       ,duration = None)) #ICS-40310
Micro_ICS40212_component      .add_state(State("Active",i = {1.8: 0.055 , 3.3: 0.165}   ,duration = None)) #ICS-40212   
Micro_SPM_component           .add_state(State("Active",i = {1.8: 0.350 , 3.3: 0.350}   ,duration = None)) #SPM0408LE5H (AudioMoth  )
Micro_Digital_component       .add_state(State("Active",i = 0.650                       ,duration = None)) #Digital one 
Micro_MP23DB01HP_LP_component .add_state(State("Active",i = {1.8: 0.285 , 3.3: 0.285}   ,duration = None)) #MP23DB01HP : Low-Power  
Micro_MP23DB01HP_component    .add_state(State("Active",i = {1.8: 0.880 , 3.3: 0.880}   ,duration = None)) #MP23DB01HP : High-Perf  

############################
# MCU registry
############################

Micro_components = {
    "ICS40310"              : Micro_ICS40310_component      ,
    "ICS40212"              : Micro_ICS40212_component      ,
    "SPM0408LE5H"           : Micro_SPM_component           ,
    "DigitalMic"            : Micro_Digital_component,
    "MP23DB01HP Low Perf"   : Micro_MP23DB01HP_LP_component,
    "MP23DB01HP"            : Micro_MP23DB01HP_component,
}

Micro_CFemb = {
    "ICS40310 "             : 0,
    "ICS40310 "             : 0,
    "ICS40310 "             : 0,
    "DigitalMic"            : 0,
    "MP23DB01HP Low Per"    : 0,
    "MP23DB01HP"            : 0,
}

