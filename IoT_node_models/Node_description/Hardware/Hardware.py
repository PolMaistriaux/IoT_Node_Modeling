#%%
import sys
import os

from .State             import *
from .Battery           import *
from .PMU               import *
from ...MyColors        import *


UNCATEGORIZED = "Uncategorized"

DEFAULT_CATEGORIES = (
    "Casing",            
    "Connectivity",      
    "EoL",               
    "Memory",            
    "Others",            
    "PCB",               
    "Power_supply",      
    "Processing",        
    "Sensing",           
    "UI",                
    "Battery"    
)


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
#   -average_power : power consumed by the components, averaged over time
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
class Hardware:
    def __init__(self,name = "None", footprintStructure=None, categories=()): # constructor
        self.name = name
        self.average_power = 0
        self.supply_power  = 0
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
                if (PMU.get_v_in() != self.Battery.get_v()):
                    raise Exception("Error : PMU supply voltage is different from battery voltage")

    def add_PMU(self, PMU_instance):
        if self.Battery is not None:
            if (PMU_instance.get_v_in() != self.Battery.get_v()):
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

        return Component_instance

    def _invalidate_footprint(self):
        self.footprint_by_category = self.footprint_total = None
        self.footprint_by_category_samples = self.footprint_total_samples = None

    def _footprint_components(self):
        """Everything that carries a footprint: components, PMUs and the battery."""
        battery = [self.Battery] if self.Battery is not None else []
        return self.component_list + self.PMU_composition + battery

    @property
    def active_categories(self):
        """Declared categories, plus UNCATEGORIZED only if some component uses it."""
        cats = list(self.categories)
        if any(c.category is None for c in self._footprint_components()):
            cats.append(UNCATEGORIZED)
        return tuple(cats)

    def _category_of(self, comp):
        return comp.category if comp.category is not None else UNCATEGORIZED

    def get_component_list(self):
        return self.component_list
    
    def get_name(self):
        return self.name
    
    def get_average_power(self):
        return self.average_power
    
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

    def set_footprint_structure(self, footprintStructure):
        self.footprintStructure = footprintStructure

    def set_component_list(self, component_list):
        self.component_list = component_list


    def reset_hardware(self):
        self.average_power = 0
        self.supply_power  = 0
        for component in self._footprint_components():
            component.reset_component()



    def compute(self, verbose = False):
        
        self.check_correctness()
        #################################################################################
        #  For each component, compute its average power, considering sleep mode.
        #  The duty cycle of the component states must have been set by the Profile.
        #################################################################################
        self.average_power = 0
        for component in self.component_list:
            self.average_power = self.average_power + component.compute_power()
            
        if self.isPowered:
            i_battery =0
            for PMU in self.PMU_composition:
                PMU.compute_power()
                i_battery = i_battery + PMU.get_i_in()

            self.Battery.set_i_load(i_battery)
            self.Battery.compute_power()
            self.lifetime =self.Battery.get_lifetime()
            if verbose:
                print('Node lifetime is %.1f years. Average current drawn from battery : %.3f [mA]'%(self.Battery.get_lifetime(), self.Battery.drawn_current ))
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
        for c in self._footprint_components():
            if c.factors is not None:
                cat = self._category_of(c)
                by_cat[cat] = by_cat[cat] + c.factors

        self.footprint_by_category = by_cat
        self.footprint_total = sum(by_cat.values(), self.footprintStructure.zeros())
        return self.footprint_total

    
    def report_footprint(self):

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

    def plot_footprint(self, label=None, filename=None, figsize=(7,6), separatePlot=False):
        """Bar per category (sorted, total last) for one impact label, with low/high as error bars.
        label defaults to the first impact label. separatePlot crops the first figure to the
        categories and adds a second figure zoomed on the top of the total bar."""
        if self.compute_footprint() is None:
            return

        labels = self.footprintStructure.labels
        label  = labels[0] if label is None else label
        unit   = self.footprintStructure.units[labels.index(label)]
        ylabel = f"{label} [{unit}]" if unit else label

        # Categories without any impact are not displayed
        rows = [(cat, *v[label]) for cat, v in self.footprint_by_category.items() if any(v[label])]
        if not rows:
            print(f"No {label} footprint to plot.")
            return
        rows.sort(key=lambda row: row[2])

        total_low, total, total_high = self.footprint_total[label]
        battery     = 0
        battery_cat = None
        if self.Battery is not None:
            battery_cat = self.Battery.category
            if self.Battery.factors is not None:
                battery = self.Battery.factors[label][MID]

        barWidth    = 0.6
        xlabel      = [row[0] for row in rows] + ["Total"]
        height_low  = np.array([row[1] for row in rows] + [total_low])
        height      = np.array([row[2] for row in rows] + [total])
        height_high = np.array([row[3] for row in rows] + [total_high])
        color       = [dictColor["Sandy"] if cat == battery_cat else dictColor["CarolinaBlue"] for cat in xlabel]

        if separatePlot:
            ax_y_fig_span = np.max(height_high[:-1])*1.3
        else:
            ax_y_fig_span = np.max(height_high)*1.3
        ax_y_max = np.max(height)*1.02

        height_e_up = height_high - height
        height_e_do = height - height_low

        fig,ax = plt.subplots(1,1,figsize=figsize)

        bar1 = ax.bar(xlabel,
                height = height, width =barWidth,
                yerr = [height_e_do,height_e_up],color = color, capsize=5,edgecolor = "black")
        # Battery share of the total bar
        ax.bar(xlabel[-1:],
                height = [battery], width =barWidth,
                color = dictColor["Sandy"],edgecolor = "black")

        ax.set_ylabel(ylabel)
        ax.set_ylim(ymin = 0, ymax = ax_y_fig_span)
        ax.tick_params(axis='x', labelrotation= 45 )
        plt.setp(ax.get_xticklabels(), ha='right')

        for rect in bar1:
            rect_height = rect.get_height()
            ax.text(rect.get_x() + rect.get_width()/2, rect_height, f'{(100*rect_height/total):.1f}%',fontsize = 13, ha='right', va='bottom',clip_on=True)
        if battery > 0:
            rect = bar1[-1]
            side_x = rect.get_x() + rect.get_width()*1.1
            ax.text(side_x, (battery + min(total,ax_y_fig_span))/2, f'{(100*(total-battery)/total):.1f}%',fontsize = 13, ha='left', va='center',rotation = -90)
            ax.text(side_x, battery/2, f'{(100*battery/total):.1f}%',fontsize = 13, ha='left', va='center',rotation = -90)

        fig.tight_layout()
        if(filename != None):
            to_save = filename+".svg"
            fig.savefig(to_save, format="svg")

        ####################################################
        if separatePlot:
            fig,ax = plt.subplots(1,1,figsize=figsize)

            ax.bar(xlabel,
                    height = height, width =barWidth,
                    color = color, capsize=5,edgecolor = "black")

            ax.set_ylabel(ylabel)
            ax.set_ylim(ymin = max(0,ax_y_max-ax_y_fig_span), ymax = ax_y_max)
            ax.tick_params(axis='x', labelrotation= 45 )
            plt.setp(ax.get_xticklabels(), ha='right')
            fig.tight_layout()
            if(filename != None):
                to_save = filename+"2.svg"
                fig.savefig(to_save, format="svg")

    def print_components(self):
        sum_power = 0
        print("-----------------------------------------------------------------")
        print("                        Module summary                           ")
        print("-----------------------------------------------------------------") 
        print ("{:<12} {:<12} {:<12} {:<12} {:<12}  ".format("Component","State","Duty [%]","Av. Pow.[mW]","Av. Cur.[uA]"))
        for component in self.get_component_list():
            print ("{:<12} {:<12} {:<12.6f} {:<12.6f} {:<12.7f}  ".format(component.get_name()," ",100*component.get_duty_cycle(),component.get_average_power(),component.get_average_current()*1000))
            for state in component.state_list:
                sum_power = sum_power + state.get_average_power()
                print ("{:<12} {:<12} {:<12.6f} {:<12.6f} ".format("     -",state.get_name(),100*state.get_duty_cycle(),state.get_average_power()))
            if component.sleep_state.get_average_power() >0:
                sum_power = sum_power + component.sleep_state.get_average_power()
                print ("{:<12} {:<12} {:<12.6f} {:<12.6f} ".format("     -",component.sleep_state.get_name(),100*component.sleep_state.get_duty_cycle(),component.sleep_state.get_average_power()))
        print("----------------------------------------------------------------------------------------------------------------")      
        print ("{:<12} {:<12} {:<12} {:<12.6f}  {:<4} ".format("Total"," "," ",sum_power,"[mW]"))
        print("----------------------------------------------------------------------------------------------------------------")
        if self.get_isPowered() :  
            print ("{:<15} {:<15} {:<15} {:<15} {:<15} {:<15} {:<15} {:<15} ".format("PMU","Vin[V]","Vout[V]","Load Cur.[mA]","In Cur.[mA]","P in [mW]" ,"P quies.[mW]","P loss [mW]"))
            for PMU in self.get_PMU_composition():
                print ("{:<15} {:<15} {:<15.4f} {:<15.4f} {:<15.4f} {:<15.4f} {:<15.4f} {:<15.4f}  ".format(PMU.get_name(),PMU.get_v_in(),PMU.get_v_out(),PMU.get_i_out(),PMU.get_i_in(),PMU.drawn_power,PMU.get_quiescent_power(),PMU.get_loss_power()))
            print("----------------------------------------------------------------------------------------------------------------")
            print ("{:<15} {:<15} {:<15} {:<15} {:<15} {:<15} {:<15} ".format("Battery","Vin[V]","C[mAh]","Iload [mA]","Idrawn [mA]","P [mW]","Lifetime[years]")) 
            battery = self.get_Battery()
            print ("{:<15} {:<15} {:<15.4f} {:<15.4f} {:<15.4f} {:<15.4f} {:<15.4f}  ".format(battery.get_name(), battery.get_v(), battery.get_capacity_mAh(), battery.get_i_load(),battery.drawn_current,battery.drawn_power, battery.get_lifetime()))
            print("----------------------------------------------------------------------------------------------------------------")



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
                if (PMU.get_v_in() != self.Battery.get_v()):
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