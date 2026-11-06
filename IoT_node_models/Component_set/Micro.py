import numpy as np
import sys
import os

from ..Node_description import *

Base_Micro_Voltage = 3.3

Micro_ICS_component           = Component(name="ICS-40310"              , category = "Sensing", v      =Base_Micro_Voltage, i_sleep=0.000)
Micro_Digital_component       = Component(name="Digital Micro IC"       , category = "Sensing", v      =Base_Micro_Voltage, i_sleep=0.000)
Micro_MP23DB01HP_component    = Component(name="MP23DB01HP : Low-Power" , category = "Sensing", v      =Base_Micro_Voltage, i_sleep=0.000)
Micro_MP23DB01HP_LP_component = Component(name="MP23DB01HP : High-Perf" , category = "Sensing", v      =Base_Micro_Voltage, i_sleep=0.000)

Micro_state_active  = State("Active",i = 0.190,duration = None) #ICS-40310 
Micro_state_active  = State("Active",i = 0.650,duration = None) #Digital one
Micro_state_active  = State("Active",i = 0.285,duration = None) #MP23DB01HP : Low-Power 
Micro_state_active  = State("Active",i = 0.800,duration = None) #MP23DB01HP : High-Perf 

Micro_ICS_component           .add_state(State("Active",i = 0.190,duration = None)) #ICS-40310  
Micro_Digital_component       .add_state(State("Active",i = 0.650,duration = None)) #Digital one 
Micro_MP23DB01HP_component    .add_state(State("Active",i = 0.285,duration = None)) #MP23DB01HP : Low-Power  
Micro_MP23DB01HP_LP_component .add_state(State("Active",i = 0.800,duration = None)) #MP23DB01HP : High-Perf  