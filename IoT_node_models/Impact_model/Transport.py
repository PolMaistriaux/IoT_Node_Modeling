

import math
import numpy as np



####################################################
def transport_footprint(km_one_way = 10, type ="Unit", weight_g = 500, footprint_p_tkm = 0.545,unit_factor = 1,footprint_p_km = 0.350,km_fixed=5):
    km = 2* km_one_way
    if(type == "Unit"):
        return (km_fixed+km*unit_factor)* footprint_p_km
    elif type =="Per_tkm":
        return km*footprint_p_tkm*weight_g/10e6
    else: 
        print("Error in type specification for transport footprint calculation")
####################################################
def transport_cost(worker = 1, salary_p_hour = 20, work_hour =1, km_p_h = 50,km_one_way = 10, type ="Unit", weight_g = 500, cost_p_tkm = 0.545,unit_factor = 1,cost_p_km = 6*2):
    km = 2* km_one_way
    transp_hour = km /km_p_h
    fixed_cost = worker*salary_p_hour * (work_hour + transp_hour)
    if(type == "Unit"):
        return fixed_cost + cost_p_km*km*unit_factor
    elif type =="Per_tkm":
        return fixed_cost + km*cost_p_tkm*weight_g/10e6
    else: 
        print("Error in type specification for transport footprint calculation")