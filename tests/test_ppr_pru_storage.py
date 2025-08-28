#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PPR_Q import PPRQProcessor
from datetime import datetime
import json

def test_ppr_pru_storage():
    """Test to see what PPR_PRU data is being stored"""
    
    # Create PPRQProcessor with the same parameters as main.py
    sos_dt = datetime(2025, 8, 22, 18, 0, 0)
    eos_dt = datetime(2025, 8, 23, 5, 15, 0)
    
    ppr_q = PPRQProcessor(
        site="BHX4",
        sos_datetime=sos_dt,
        eos_datetime=eos_dt
    )
    
    # Run PPR_Q
    result = ppr_q.run()
    
    # Check PPR_PRU section specifically
    if "PPR_PRU" in result:
        ppr_pru_data = result["PPR_PRU"]
        print("=== PPR_PRU Data ===")
        for key, value in ppr_pru_data.items():
            print(f"{key}: {value}")
    else:
        print("No PPR_PRU section found!")
    
    # Also check for any volume/hours data
    print("\n=== Looking for Volume/Hours Data ===")
    for key, value in result.items():
        if "Volume" in key or "Hours" in key:
            print(f"{key}: {value}")

if __name__ == "__main__":
    test_ppr_pru_storage()
