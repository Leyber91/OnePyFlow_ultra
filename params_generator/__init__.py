"""
🚀 OnePyFlow Params Generator V2.0 - Modular Edition
Dark Matrix Theme with Adaptive UI
"""

from .main_window import OnePyFlowParamsGenerator
from .components import *
from .themes import DarkMatrixTheme

__version__ = "2.0.0"
__author__ = "OnePyFlow Team"

def main():
    """Launch the params generator"""
    from .main_window import main
    main()

if __name__ == "__main__":
    main() 