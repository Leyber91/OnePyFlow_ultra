#!/usr/bin/env python3
"""
🚀 OnePyFlow Params Generator Launcher
Launches the new modular dark matrix themed params generator
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from params_generator.main_window import main
    print("🚀 Launching OnePyFlow Params Generator V2.0 - Dark Matrix Edition...")
    main()
except ImportError as e:
    print(f"❌ Error importing params generator: {e}")
    print("Make sure all required files are present in the params_generator directory.")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error launching params generator: {e}")
    sys.exit(1) 