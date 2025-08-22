#!/usr/bin/env python3
"""
Quick debug script to examine rate calculation data structure
"""

import sys
import os
import logging
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, os.getcwd())

from PPR_Q.PPR_Q_processor import PPRQProcessor

# Set up logging to see debug output
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

def debug_single_process():
    """Debug a single process to see data structure"""
    
    # Test parameters
    site = "BHX4"
    end_time = datetime.now()
    start_time = end_time - timedelta(hours=1)
    
    print(f"🔍 DEBUGGING PPR_Q RATE CALCULATIONS")
    print(f"Site: {site}")
    print(f"Time range: {start_time} to {end_time}")
    
    try:
        # Create processor
        processor = PPRQProcessor(site, start_time, end_time)
        
        # Test PPR_PRU specifically (has rate calculations)
        process_key = "PPR_PRU"
        process_id = processor.process_ids[process_key]
        
        print(f"\n📊 Testing {process_key} (ID: {process_id})")
        
        # Fetch data
        df = processor.fetch_process_data(process_key)
        
        if not df.empty:
            print(f"✅ Got {len(df)} rows, {len(df.columns)} columns")
            
            # Show column structure
            print(f"\n📋 COLUMN STRUCTURE:")
            for i, col in enumerate(df.columns):
                print(f"   {i:2d}: {col}")
            
            # Show sample data for rate-related columns
            print(f"\n🎯 RATE-RELATED COLUMNS (14, 15, 16):")
            for col_idx in [14, 15, 16]:
                if col_idx < len(df.columns):
                    col_name = df.columns[col_idx]
                    sample_vals = df.iloc[:3, col_idx].tolist() if len(df) > 0 else []
                    print(f"   Column {col_idx:2d} ({col_name}): {sample_vals}")
                else:
                    print(f"   Column {col_idx:2d}: NOT PRESENT")
            
            # Check for any columns with 'rate' in the name
            print(f"\n🔍 COLUMNS WITH 'RATE' IN NAME:")
            rate_cols = [(i, col) for i, col in enumerate(df.columns) if 'rate' in col.lower()]
            if rate_cols:
                for i, col in rate_cols:
                    sample_vals = df.iloc[:3, i].tolist() if len(df) > 0 else []
                    print(f"   Column {i:2d} ({col}): {sample_vals}")
            else:
                print("   No columns with 'rate' in name found")
                
        else:
            print("❌ No data returned")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_single_process()
