#!/usr/bin/env python3
"""
Debug script to test PPR_PRU data fetching and processing
"""

import logging
import sys
import os
from datetime import datetime

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PPR_Q import PPRQProcessor

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_ppr_pru():
    """Test PPR_PRU data fetching and processing"""
    
    # Test parameters
    site = "BHX4"
    sos_datetime = datetime(2025, 8, 22, 18, 0, 0)
    eos_datetime = datetime(2025, 8, 23, 5, 15, 0)
    
    print(f"Testing PPR_PRU for {site} from {sos_datetime} to {eos_datetime}")
    print("=" * 80)
    
    # Create PPR_Q processor
    ppr_q = PPRQProcessor(site=site, sos_datetime=sos_datetime, eos_datetime=eos_datetime)
    
    # Test only PPR_PRU
    print("Fetching PPR_PRU data...")
    ppr_pru_df = ppr_q.fetch_process_data("PPR_PRU")
    
    if ppr_pru_df.empty:
        print("❌ No data returned for PPR_PRU")
        return
    
    print(f"✅ Got {len(ppr_pru_df)} rows for PPR_PRU")
    print(f"Columns: {list(ppr_pru_df.columns)}")
    
    # Show first few rows
    print("\nFirst 5 rows:")
    print(ppr_pru_df.head())
    
    # Test the generic_process method directly
    print("\n" + "=" * 80)
    print("Testing generic_process method...")
    
    from PPR.PPR_PRU import CONFIG as PRU_CONFIG
    
    # Create a test JSON
    test_json = {}
    
    # Call generic_process
    ppr_q.generic_process(ppr_pru_df, "PPR_PRU", test_json, PRU_CONFIG)
    
    print("\nResults from generic_process:")
    for key, value in test_json.get("PPR_PRU", {}).items():
        print(f"  {key}: {value}")
    
    # Check specific rates
    print("\n" + "=" * 80)
    print("Checking specific rates:")
    
    pru_data = test_json.get("PPR_PRU", {})
    
    # Check if divide_by: 4 was applied
    rates_to_check = [
        "PRU_Receive_Dock",
        "PRU_Each_Receive_Total", 
        "PRU_LP_Receive",
        "PRU_RC_Sort_Total",
        "PRU_Transfer_Out"
    ]
    
    for rate in rates_to_check:
        value = pru_data.get(rate, "NOT_FOUND")
        print(f"  {rate}: {value}")
        if isinstance(value, (int, float)) and value > 0:
            # Check if it looks like it was divided by 4
            # If the original value was around 1200-1400, divided by 4 should be 300-350
            if value < 1000:
                print(f"    ✅ Looks like divide_by: 4 was applied (value: {value})")
            else:
                print(f"    ❌ Value too high, divide_by: 4 may not have been applied (value: {value})")

if __name__ == "__main__":
    test_ppr_pru()
