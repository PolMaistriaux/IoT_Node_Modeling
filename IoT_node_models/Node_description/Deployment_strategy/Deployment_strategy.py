#%%
import numpy as np



#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# Deployment of a node over Nyears, described by:
#   -Nyears               : service duration to cover
#   -ReplacementStrategy  : what is replaced each time the node reaches its lifetime
# Placement and decommissioning default to the footprint of the node hardware and to nothing
# (end of life is a hardware category). Subclasses override placement_footprint / decom_footprint
# to add e.g. transport.
# Results of compute_footprint:
#   -placement, decom, replacements : FootprintVector of each phase
#   -n_replacements                 : number of replacements over Nyears
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
class DeploymentStrategy:
    def __init__(self, Nyears=10, replacementCategories=None):
        if Nyears <= 0:
            raise ValueError("Nyears must be positive")
        if replacementCategories is not None :
            if not isinstance(replacementCategories, tuple):
                raise TypeError("replacementCategories must be a tuple of strings or None")
            
        self.Nyears = Nyears
        self.ReplacementStrategy = replacementCategories
        self.placement       = None
        self.decom           = None
        self.replacement     = None
        
        self.overhead_placement       = 0
        self.overhead_decom           = 0
        self.overhead_replacement    = 0

        self.n_replacements  = 0

    def placement_footprint(self, hardware):
        self.overhead_placement = 0
        return hardware.footprint_total

    def replacement_hardware(self, hardware):
        """Footprint of a single replacement, from the footprint already computed by the hardware."""
        if self.ReplacementStrategy is None:
            return hardware.footprint_total
        unknown = set(self.ReplacementStrategy) - set(hardware.footprint_by_category)
        if unknown:
            raise ValueError(f"Replaced categories {sorted(unknown)} not in hardware categories {list(hardware.footprint_by_category)}")
        
        return sum((hardware.footprint_by_category[c] for c in self.ReplacementStrategy),
                   hardware.footprintStructure.zeros())

    def replacement_footprint(self, hardware):
        self.overhead_replacement = 0
        return self.replacement_hardware(hardware)

    def decom_footprint(self, hardware):
        self.overhead_decom = 0
        return hardware.footprintStructure.zeros()

    def compute_footprint(self, hardware, lifetime,smooth=False):
        """Total footprint of covering Nyears with nodes of the given lifetime [years]:
        placement + replacements + decommissioning."""
        if lifetime <= 0:
            raise ValueError(f"Node lifetime must be positive, got {lifetime}")
        if hardware.compute_footprint(verbose=False) is None:
            raise ValueError("Hardware has no footprint structure: nothing to deploy")

        # A replacement is only needed when the service outlasts the node
        if smooth:
            self.n_replacements = max(           (self.Nyears / lifetime)  - 1 , 0)
        else:    
            self.n_replacements = max(int(np.ceil(self.Nyears / lifetime)) - 1, 0)

        self.placement    = self.placement_footprint(hardware)
        self.decom        = self.decom_footprint(hardware)
        self.replacement  = self.replacement_footprint(hardware)
        return self.placement + (self.replacement * self.n_replacements) + self.decom
