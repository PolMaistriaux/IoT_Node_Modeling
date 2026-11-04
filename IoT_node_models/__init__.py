print("Importing IoT Node models")
import sys as _sys

# importlib.reload(IoT_node_models) re-executes this file: drop every submodule first (and the
# stale attributes pointing to them) so that all of them are rebuilt by the imports below.
_prefix = __name__ + "."
for _name in [m for m in _sys.modules if m.startswith(_prefix)]:
    del _sys.modules[_name]
    globals().pop(_name[len(_prefix):], None)

from . import MyColors
from . import Node_description
from . import Component_set

# Flat namespace: `from IoT_node_models import *` gives the whole API.
# Note that this makes IoT_node_models.Node_description the class, not the subpackage
# (`from IoT_node_models.Node_description import ...` still reaches the subpackage).
from .MyColors                                     import *
from .Node_description                             import *
from .Node_description.Profile.Wireless_communication import *
from .Component_set                                import *