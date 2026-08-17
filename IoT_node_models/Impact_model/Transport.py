

import math
import numpy as np



####################################################
def transport_footprint(km_p_node = 10,km_fixed=5, type ="Unit", n_node = 1,footprint_p_km = 0.350):
    if(type == "Unit"):
        return (km_p_node+km_fixed/n_node)* footprint_p_km
    else: 
        print("Error in type specification for transport footprint calculation")
####################################################
def transport_cost(km_fixed=5,worker = 1, salary_p_hour = 20, work_hour_p_node =1, km_p_h = 50, type ="Unit",n_node = 1,cost_p_km = 6*2):
    transp_hour_fixed = km_fixed /km_p_h
    if(type == "Unit"):
        fixed_cost = worker*salary_p_hour * (work_hour_p_node + transp_hour_fixed/n_node)
        return fixed_cost  + cost_p_km*km_fixed/n_node
    else: 
        print("Error in type specification for transport footprint calculation")




####################################################
def F_trans(km_fixed=1,km_p_node=1,n_node=1 ):
    return transport_footprint(km_p_node = km_p_node, km_fixed=km_fixed, type ="Unit", 
                            n_node = n_node,footprint_p_km = 0.350)

####################################################
def C_trans(km):
    return transport_cost(  worker = 1, 
                            salary_p_hour = 5, 
                            work_hour_p_node =10/60, 
                            km_p_h = 50,
                            km_fixed = km, 
                            type ="Unit", 
                            n_node = 1,cost_p_km = 0.2)