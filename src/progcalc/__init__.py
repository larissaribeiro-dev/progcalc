"""progcalc: calculadora para programadores."""

from .calculator import calculate
from .errors import CalcError

__all__ = ["calculate", "CalcError"]
__version__ = "0.1.0"
