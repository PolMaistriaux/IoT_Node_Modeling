
import sys
import os

import math
import numpy as np

from .Deployment_strategy import *


####################################################
def transport_footprint(km_p_node = 10,km_fixed=5, type ="Unit", n_node = 1,footprint_p_km = 0.350):
    if(type == "Unit"):
        return (km_p_node+km_fixed/n_node)* footprint_p_km
    else:
        print("Error in type specification for transport footprint calculation")


#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# One transport trip, described by:
#   -km_fixed        : distance of the trip shared by the n_node nodes handled together
#   -km_p_node       : distance specific to each node
#   -n_node          : number of nodes sharing the fixed part of the trip
#   -footprint_p_km  : impact per km. A float is applied to `label`,
#                      a {label: value} dict gives several impacts (e.g. GWP and Money)
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
class Transport:
    def __init__(self, km_fixed=1, km_p_node=1, n_node=1, footprint_p_km=0.350, label="GWP"):
        self.km_fixed       = km_fixed
        self.km_p_node      = km_p_node
        self.n_node         = n_node
        self.footprint_p_km = footprint_p_km if isinstance(footprint_p_km, dict) else {label: footprint_p_km}

    def F_trans(self, label):
        """Transport impact of a single node for one impact label."""
        return transport_footprint(km_p_node = self.km_p_node, km_fixed=self.km_fixed, type ="Unit",
                                   n_node = self.n_node, footprint_p_km = self.footprint_p_km[label])

    def footprint(self, structure):
        """Transport impact of a single node as a FootprintVector of the given structure."""
        return structure.vector({label: self.F_trans(label) for label in self.footprint_p_km})

    def __repr__(self):
        return (f"Transport(km_fixed={self.km_fixed}, km_p_node={self.km_p_node}, "
                f"n_node={self.n_node}, footprint_p_km={self.footprint_p_km})")


#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# Deployment strategy where each phase has its own transport (or None for no transport):
#   -transport_placement   : once, when the node is placed
#   -transport_replacement : at every replacement
#   -transport_decom       : once, when the node is decommissioned
# The transport of each phase is stored in overhead_placement / overhead_replacement / overhead_decom
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
class DeploymentStrategy_wTransport(DeploymentStrategy):
    def __init__(self, Nyears=10, replacementCategories=None,
                 transport_placement=None, transport_replacement=None, transport_decom=None):
        super().__init__(Nyears=Nyears, replacementCategories=replacementCategories)
        self.transport_placement   = transport_placement
        self.transport_replacement = transport_replacement
        self.transport_decom       = transport_decom

    def placement_footprint(self, hardware):
        footprint = super().placement_footprint(hardware)
        if self.transport_placement is not None:
            if isinstance(self.transport_placement, Transport):
                self.overhead_placement = self.transport_placement.footprint(hardware.footprintStructure)
            else:
                self.overhead_placement = self.transport_placement
            footprint = footprint + self.overhead_placement
        return footprint

    def replacement_footprint(self, hardware):
        footprint = super().replacement_footprint(hardware)
        if self.transport_replacement is not None:
            if isinstance(self.transport_replacement, Transport):
                self.overhead_replacement = self.transport_replacement.footprint(hardware.footprintStructure)
            else:
                self.overhead_replacement = self.transport_replacement
        return footprint

    def decom_footprint(self, hardware):
        footprint = super().decom_footprint(hardware)
        if self.transport_decom is not None:
            if isinstance(self.transport_decom, Transport):
                self.overhead_decom = self.transport_decom.footprint(hardware.footprintStructure)
            else:
                self.overhead_decom = self.transport_decom
            footprint = footprint + self.overhead_decom
        return footprint
