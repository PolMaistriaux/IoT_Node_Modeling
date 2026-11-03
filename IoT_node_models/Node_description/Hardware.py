#%%
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Node_description.State import *
from Node_description.Battery           import *
from Node_description.PMU               import *


UNCATEGORIZED = "Uncategorized"


def _fmt(row):
    """Format a (low, mid, high) row: single value if fixed, else [lo, mid, hi]."""
    lo, mid, hi = row
    return f"{mid:.4g}" if lo == mid == hi else f"[{lo:.3g}, {mid:.3g}, {hi:.3g}]"



#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# Given component of the node described by:
#   -Current consumption in sleep mode
#   -Operating voltage in sleep mode
#   -List of the different component state in which it can operate (sleep is referred a default state)
# Additional variables used:
#   -energy_day   : overall energy consumed by the component over the day
#   -t_active_day : overall time spent in active (not in sleep state) during the day
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
class Hardware:
    def __init__(self,name = "None", footprintStructure=None, categories=()): # constructor
        self.name = name
        self.energy = 0
        self.average_power = 0
        self.component_list = []

        # Powered node
        self.isPowered = False
        self.PMU_composition = []
        self.Battery = None
        self.lifetime = 0 

        self.footprintStructure=footprintStructure

        categories = tuple(categories)
        if len(set(categories)) != len(categories):
            raise ValueError("Duplicate category labels")
        self.categories = categories
        self.footprint_by_category         = None  # {category: FootprintVector}
        self.footprint_total               = None  # FootprintVector
        self.footprint_by_category_samples = None  # {category: ndarray (n_labels, n)}
        self.footprint_total_samples       = None  # ndarray (n_labels, n)

        
        
    def add_Battery(self, Battery_instance):
        if self.Battery is not None:
            print("Warning : Battery already specified : replacing it")
        self.Battery = Battery_instance

        if self.PMU_composition:
            for PMU in self.PMU_composition:
                if (PMU.v_in != self.Battery.v):
                    raise Exception("Error : PMU supply voltage is different from battery voltage")

    def add_PMU(self, PMU_instance):
        if self.Battery is not None:
            if (PMU_instance.v_in != self.Battery.v):
                raise Exception("Error : PMU supply voltage is different from battery voltage")
        self.PMU_composition.append(PMU_instance)
    
    def add (self, Component_instance):
        if Component_instance.factors is not None:
            if self.footprintStructure is None:
                raise ValueError(f"{Component_instance.name}: has impact factors but node has no structure")
            if Component_instance.factors.structure is not self.footprintStructure:
                raise ValueError(f"{Component_instance.name}: structure mismatch with node")
        
        if Component_instance.category is not None and Component_instance.category not in self.categories:
            raise ValueError(f"{Component_instance.name}: category {Component_instance.category} not in node categories {self.categories}")
  
        self._invalidate_footprint()

        if isinstance(Component_instance, Battery):
            self.add_Battery(Component_instance)
        elif isinstance(Component_instance, PMU):
            self.add_PMU(Component_instance)
        elif isinstance(Component_instance, Component):
            self.component_list.append(Component_instance)
            self.isPowered = False
        else :
            raise Exception("Error : Component is not of type Component, PMU or Battery, type is %s"%type(Component_instance))


    def _invalidate_footprint(self):
        self.footprint_by_category = self.footprint_total = None
        self.footprint_by_category_samples = self.footprint_total_samples = None

    @property
    def active_categories(self):
        """Declared categories, plus UNCATEGORIZED only if some component uses it."""
        cats = list(self.categories)
        if any(c.category is None for c in self.component_list):
            cats.append(UNCATEGORIZED)
        return tuple(cats)

    def _category_of(self, comp):
        return comp.category if comp.category is not None else UNCATEGORIZED

    def get_component_list(self):
        return self.component_list
    
    def get_name(self):
        return self.name
    
    def get_energy(self):
        return self.energy
    
    def get_lifetime(self):
        return self.lifetime
    
    def get_Battery(self):
        return self.Battery
    
    def get_isPowered(self):
        return self.isPowered
    
    def get_PMU_composition(self):
        return self.PMU_composition
    
    def get_Battery(self):
        return self.Battery

    def set_name(self, name):
        self.name = name

    def set_component_list(self, component_list):
        self.component_list = component_list


    def reset_hardware(self):
        self.energy = 0
        self.average_power = 0
        for component in self.component_list:
            component.reset_component()



    def compute(self, time_window, verbose = False):
        
        self.check_correctness()
        #################################################################################
        #  For each component, compute the energy it consumes over a single day
        #################################################################################
        self.energy = 0
        for component in self.component_list:
            #Compute the component energy for a single day, considering sleep mode.
            energy = component.compute_energy(time_window)
            self.energy = self.energy + energy
        self.average_power = self.energy/time_window

        if self.isPowered:
            i_battery =0
            for PMU in self.PMU_composition:
                PMU.compute()
                i_battery = i_battery + PMU.get_i_in()
            
            self.Battery.set_i(i_battery)
            self.Battery.compute()
            self.lifetime =self.Battery.get_lifetime()
            if verbose:
                print('Node lifetime is %.1f years. Average current drawn from battery : %.3f [mA]'%(self.Battery.get_lifetime(), self.Battery.get_i() ))
        else:
            self.lifetime = 0
            if verbose:
                print('Node is not powered, no lifetime can be computed')


    # --- deterministic (bounds) -------------------------------------------
    def compute_footprint(self, verbose=True):
        """Compute per-category footprint, then the total. Stores and returns the total."""
        if self.footprintStructure is None:
            self.footprint_by_category = self.footprint_total = None
            if verbose:
                print("No footprint structure defined: not modeled.")
            return None

        by_cat = {cat: self.footprintStructure.zeros() for cat in self.active_categories}
        for c in self.component_list:
            if c.factors is not None:
                cat = self._category_of(c)
                by_cat[cat] = by_cat[cat] + c.factors

        self.footprint_by_category = by_cat
        self.footprint_total = sum(by_cat.values(), self.footprintStructure.zeros())
        return self.footprint_total

    
    def report_footprint(self):
        print("No footprint schema defined.")

        headers = ["Category"] + [
            f"{l} [{u}]" if u else l for l, u in zip(self.footprintStructure.labels, self.footprintStructure.units)
        ]
        rows = [[cat] + [_fmt(r) for r in v.data] for cat, v in self.footprint_by_category.items()]
        total_row = ["Total"] + [_fmt(r) for r in self.footprint_total.data]

        widths = [max(len(str(x)) for x in col) for col in zip(headers, *rows, total_row)]
        line = lambda cells: "  ".join(str(c).ljust(w) for c, w in zip(cells, widths))
        sep = "  ".join("-" * w for w in widths)

        out = [line(headers), sep, *(line(r) for r in rows), sep, line(total_row)]
        print("\n".join(out))

    def footprint_category_array(self, which="mid"):
        """(categories, array of shape (n_categories, n_labels)) for plotting."""
        if self.by_category is None:
            self.compute(verbose=False)
        col = {"low": LOW, "mid": MID, "high": HIGH}[which]
        cats = list(self.by_category)
        return cats, np.array([self.by_category[c].data[:, col] for c in cats])
    
    def print_components(self):
        sum_energy = 0
        print("-----------------------------------------------------------------")
        print("                        Module summary                           ")
        print("-----------------------------------------------------------------") 
        print ("{:<12} {:<12} {:<12} {:<12} {:<12}  ".format("Component","State","Active [s]","Energy [mJ]","Av. Cur.[uA]"))
        for component in self.get_component_list():
            print ("{:<12} {:<12} {:<12.4f} {:<12.4f} {:<12.7f}  ".format(component.get_name()," ",component.get_activeTime(),component.get_energy(),component.get_average_current()*1000))
            for state in component.state_list:
                sum_energy = sum_energy + state.get_energy()
                print ("{:<12} {:<12} {:<12.4f} {:<12.4f} ".format("     -",state.get_name(),state.get_activeTime(),state.get_energy()))
            if component.get_i_sleep() > 0:
                sum_energy = sum_energy + component.sleep_state.get_energy()
                print ("{:<12} {:<12} {:<12.4f} {:<12.4f} ".format("     -",component.sleep_state.get_name(),component.sleep_state.get_activeTime(),component.sleep_state.get_energy()))
        print("-----------------------------------------------------------------")      
        print ("{:<12} {:<12} {:<12} {:<12.4f}  {:<6.4f}  {:<4} ".format("Total"," "," ",sum_energy,self.average_power,"[mW]"))
        print("-----------------------------------------------------------------")
        if self.get_isPowered() :  
            print ("{:<12} {:<12} {:<12} {:<12} {:<12}  ".format("PMU","Vin[V]","Vout[V]","Energy [mJ]","Av. Cur.[uA]")) 
            for PMU in self.get_PMU_composition():
                print ("{:<12} {:<12} {:<12.4f} {:<12.4f} {:<12.4f}  ".format(PMU.get_name(),PMU.get_v_in(),PMU.get_v_out(),PMU.get_v_in()*PMU.get_i_in(),1000*PMU.get_i_in()))
            print("-----------------------------------------------------------------")
            print ("{:<12} {:<12} {:<12} {:<12} {:<12}  ".format("Battery","Vin[V]","C[mAh]","I [mJ]","Lifetime[years]")) 
            battery = self.get_Battery()
            print ("{:<12} {:<12} {:<12.4f} {:<12.4f} {:<12.4f}  ".format(battery.get_name(), battery.get_v(), battery.get_capacity_mAh(), battery.get_i(), battery.get_lifetime()))
            print("-----------------------------------------------------------------")



    def check_correctness(self):
        
        self.isPowered = True

        if not self.PMU_composition:
            print("Warning : No PMU in node")
            self.isPowered = False
            
        if self.Battery == None:
            print("Warning : No Battery in node")

        if not self.component_list:
            print("Warning : No component in node")
            self.isPowered = False

        if self.isPowered is False:
            return 
        
        for component in self.component_list:
            found = 0
            for PMU in self.PMU_composition:
                if (PMU.v_in != self.Battery.v):
                    print("Error : PMU supply voltage is different from battery voltage")
                    self.isPowered = False
                try:
                    for PMU_component in PMU.component_list:
                        if PMU_component == component :
                            found = 1
                        if found>1:
                            raise Exception("Error : component registered multiples in a PMU or in multiple PMUs")
                except:
                    raise Exception("Error : PMU component_list is not properly defined")
                
        return 