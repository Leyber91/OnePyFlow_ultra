#!/usr/bin/env python3
"""
OnePyFlow Params Generator Launcher
Launches the modular params generator interface
"""

import sys
import os

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

try:
    from params_generator.proper_ui import main
    if __name__ == "__main__":
        main()
except ImportError as e:
    print(f"❌ Error importing params generator: {e}")
    print("Make sure all required files are present in the params_generator directory.")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error launching params generator: {e}")
    sys.exit(1)