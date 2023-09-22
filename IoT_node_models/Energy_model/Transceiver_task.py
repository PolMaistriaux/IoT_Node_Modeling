#%%
import scipy.interpolate
import numpy as np

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Energy_model.Wireless_communication   import LoRa_library as LoRa
from Energy_model.Wireless_communication   import Optimal_strategy as optStrat
from Energy_model.Node      import *
from Energy_model.Node_task import *



##############################################################################################


class TX_task(Node_task):
    def __init__(self,name = "None", radio = None, processor=None, state_Processing=None, state_TX=None,Proc_duration=0,TX_duration =0, I_TX=None, P_TX=None, Ptx=0):

        self.radio     = radio
        self.processor = processor

        self.state_TX      = state_TX
        self.radio.add_state(self.state_TX )
        self.subtask_TX    = Node_subtask(name='TX ' + name ,module=radio , moduleState = self.state_TX     , stateDuration=TX_duration)
        self.TX_duration = TX_duration

        self.P_TX_interpolator = None
        self.I_TX  = I_TX
        self.P_TX  = P_TX
        self.Ptx = Ptx
        if (I_TX is not None) and (P_TX is not None):
            self.set_TX_Power_config(self.P_TX ,  self.I_TX)

        self.state_Processing       = state_Processing
        self.substask_Processing    = Node_subtask(name='Processing ' + name ,module=processor , moduleState = self.state_Processing, stateDuration=Proc_duration)
        self.proc_duration          = Proc_duration

        super().__init__(name = name, node_modules= [radio,processor], subtasks=[self.substask_Processing, self.subtask_TX], taskDuration = self.proc_duration+self.TX_duration)

    def change_TX_duration(self,duration):
        self.subtask_TX.set_stateDuration(duration)
        self.TX_duration      = duration
        self.taskDuration     = duration + self.proc_duration

    def change_MCU_TX_duration(self,duration):
        self.substask_Processing.set_stateDuration(duration)
        self.proc_duration    = duration
        self.taskDuration     = duration + self.TX_duration

    def set_TX_Power_config(self, P_TX, I_TX ):
        if np.size(I_TX)<=1 or np.size(P_TX)<=1 :
            print("Error: array provided to set_TX_Power_config is empty")
        elif len(P_TX) != len(I_TX):
            print("Error: arrays provided to set_TX_Power_config have different lengths")
        else : 
            self.I_TX = I_TX
            self.P_TX  = P_TX
            self.P_TX_interpolator = scipy.interpolate.interp1d(self.P_TX,self.I_TX )
            self.set_TX_Power(Ptx=self.Ptx)

    def set_TX_Power(self, Ptx=0, Itx=0):
        if Itx==0 and self.P_TX_interpolator == None: 
            print("Error : No power config. made and no Itx specified")
        if np.size(self.I_TX)==0 or np.size(self.P_TX)==0 :
            self.Ptx = Ptx
            self.subtask_TX.set_stateParam_i(Itx)
        else : 
            if(Ptx < np.min(self.P_TX)):
                Ptx = np.min(self.P_TX)
            elif (Ptx > np.max(self.P_TX)):
                Ptx = np.max(self.P_TX)
            self.Ptx = Ptx
            self.subtask_TX.set_param_i(self.P_TX_interpolator(Ptx))

##############################################################################################          

class LoRa_TX_task(TX_task):
    def __init__(self,name = "None", radio = None, processor=None, state_Processing=None,state_TX=None,Proc_duration=0.3, I_TX=[], P_TX=[], Ptx=0, SF = 7 ,Payload = 100 ,Header = True ,DE = None ,Coding = 1 ,BW = 125e3  ):
        super().__init__(name = name, radio = radio, processor=processor, state_Processing=state_Processing,state_TX=state_TX,Proc_duration=Proc_duration,TX_duration =0, I_TX=I_TX, P_TX=P_TX,Ptx=Ptx)
        self.set_radio_parameters(SF=SF,Coding=Coding,Header=Header,DE = DE,BW = BW, Payload = Payload)
        #For settings of Link budget
        self.PL_model = None
        self.distance = 1
        

    
    def set_radio_parameters(self, SF=None,Coding=None,Header=None,DE = None,BW = None, Payload = None):
        if SF != None:
            self.SF = SF
        if Payload != None:
            self.Payload = Payload
        if Header != None:
            self.Header = Header
        if DE != None:
            self.DE = DE
        if Coding != None:
            self.Coding = Coding
        if BW != None:
            self.BW = BW
        self.compute_tx_time()
    
    def compute_tx_time(self):
        durationTX =  LoRa.time_on_air(Payload=self.Payload,Coding=self.Coding,Header=self.Header,DE = self.DE,B = self.BW,SF=self.SF, Bytes=True)
        self.change_TX_duration(durationTX)

    
    def set_distance(self,d):
        self.distance = d
        self.set_optimal_SF_PTX_at_PL()

    def set_Path_loss_model(self,PL_model):
        self.PL_model = PL_model
        self.set_optimal_SF_PTX_at_PL()

    def set_optimal_SF_PTX_at_PL(self,verbose = False):
        if self.PL_model is None:
            raise Exception("Error : No Path loss model provided") 
        PL = self.PL_model(self.distance)    
        [opt_SF,opt_PTX,dummy] = optStrat.find_Opti_SF_PTX(PTX_possible = self.P_TX, PL = PL , I_PTX=self.I_TX,verbose=verbose)
        if opt_SF == 0:
            raise Exception("Error : Out of range for d = %.2f"%(self.distance)) 
            return [0,0]
        self.SF =opt_SF
        self.set_radio_parameters(SF=opt_SF)
        self.set_TX_Power(Ptx = opt_PTX) 
        if verbose:
            print("Radio parameter : SF = %d and PTx = %.1f dBm"%(opt_SF,opt_PTX))

    
##############################################################################################   
# 
# 
##############################################################################################      


class RX_task(Node_task):
    def __init__(self,name = "None", radio = None, processor=None, state_Processing=None,state_RX=None,Proc_duration=0,RX_duration =0):

        self.radio     = radio
        self.processor = processor

        self.state_RX      = state_RX
        self.radio.add_state(self.state_RX )
        self.subtask_RX    = Node_subtask(name='RX ' + name ,module=radio , moduleState = self.state_RX     , stateDuration=RX_duration)
        self.RX_duration   = RX_duration

        self.state_Processing       = state_Processing
        self.substask_Processing    = Node_subtask(name='Processing ' + name ,module=processor , moduleState = self.state_Processing, stateDuration=Proc_duration)
        self.proc_duration          = Proc_duration

        super().__init__(name = name, node_modules= [radio,processor], subtasks=[self.substask_Processing, self.subtask_RX], taskDuration = self.proc_duration+self.RX_duration)

    def change_RX_duration(self,duration):
        self.subtask_RX.set_stateDuration(duration)
        self.RX_duration      = duration
        self.taskDuration     = duration + self.proc_duration

    def change_MCU_RX_duration(self,duration):
        self.substask_Processing.set_stateDuration(duration)
        self.proc_duration    = duration
        self.taskDuration     = duration + self.RX_duration