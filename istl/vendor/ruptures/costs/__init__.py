"""Local loader for the unmodified upstream CostL2 and Dynp modules."""
from ruptures.exceptions import NotEnoughPoints
from .costl2 import CostL2

def cost_factory(model, **kwargs):
    if model != "l2":
        raise ValueError("This bundled subset supports only l2")
    return CostL2(**kwargs)

