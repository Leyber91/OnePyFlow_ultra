#!/usr/bin/env python3
"""
Test script to validate PPR fixes and hybrid approach.
"""

import sys
import os
import logging
from datetime import datetime, timedelta

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PPR.PPR_processor import PPRProcessor, DataFetchError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler()]
)

def test_ppr_fixes():
    """Test the PPR fixes with enhanced error handling and PPR_Q fallback."""
    
    # Test parameters
    site = "DTM2"  # Use DTM2 as it showed good results in diagnostics
    now = datetime.now()
    sos_datetime = now - timedelta(hours=2)
    eos_datetime = now
    
    logging.info("=" * 80)
    logging.info("TESTING PPR FIXES")
    logging.info("=" * 80)
    logging.info(f"Site: {site}")
    logging.info(f"Time range: {sos_datetime} to {eos_datetime}")
    logging.info("")
    
    try:
        # Initialize PPR processor
        processor = PPRProcessor(site, sos_datetime, eos_datetime)
        
        # Test individual critical processes
        critical_processes = ["PPR_Pallet_Receive", "PPR_Case_Receive", "PPR_LP_Receive"]
        
        for process_key in critical_processes:
            logging.info(f"Testing critical process: {process_key}")
            try:
                # Test the hybrid fetch approach
                df = processor.fetch_with_ppr_q_fallback(process_key)
                
                if not df.empty:
                    logging.info(f"✓ {process_key}: SUCCESS - {len(df)} rows")
                    logging.info(f"  Columns: {list(df.columns)}")
                    logging.info(f"  Shape: {df.shape}")
                else:
                    logging.warning(f"⚠ {process_key}: No data returned")
                    
            except DataFetchError as e:
                logging.error(f"✗ {process_key}: CRITICAL ERROR - {e}")
            except Exception as e:
                logging.error(f"✗ {process_key}: UNEXPECTED ERROR - {e}")
            
            logging.info("")
        
        # Test full processing
        logging.info("Testing full PPR processing...")
        try:
            result = processor.run()
            
            # Check if critical processes are in the result
            for process_key in critical_processes:
                if process_key in result:
                    logging.info(f"✓ {process_key} found in results")
                    process_data = result[process_key]
                    logging.info(f"  Keys: {list(process_data.keys())}")
                    
                    # Check for specific Pallet Receive metrics
                    if process_key == "PPR_Pallet_Receive":
                        if "Pallet_Receive_TotalPallets" in process_data:
                            pallets = process_data["Pallet_Receive_TotalPallets"]
                            logging.info(f"  Total Pallets: {pallets}")
                        if "MonoAsinUPP" in process_data:
                            mono_upp = process_data["MonoAsinUPP"]
                            logging.info(f"  MonoAsinUPP: {mono_upp}")
                else:
                    logging.warning(f"⚠ {process_key} NOT found in results")
            
            logging.info("✓ Full PPR processing completed successfully")
            
        except Exception as e:
            logging.error(f"✗ Full PPR processing failed: {e}")
        
    except Exception as e:
        logging.error(f"✗ Test setup failed: {e}")

def test_url_parameters():
    """Test that URL parameters are correctly added."""
    logging.info("=" * 80)
    logging.info("TESTING URL PARAMETERS")
    logging.info("=" * 80)
    
    site = "DTM2"
    now = datetime.now()
    sos_datetime = now - timedelta(hours=2)
    eos_datetime = now
    
    processor = PPRProcessor(site, sos_datetime, eos_datetime)
    
    # Test URL building for Pallet Receive
    process_key = "PPR_Pallet_Receive"
    process_id = processor.process_ids[process_key]
    
    # Create a test shift
    shift = {
        'start_hour': '06',
        'start_minute': '0',
        'start_day': '19',
        'start_month': '07',
        'start_year': '2025',
        'end_hour': '08',
        'end_minute': '0',
        'end_day': '19',
        'end_month': '07',
        'end_year': '2025'
    }
    
    url = processor.build_url(process_key, process_id, shift)
    logging.info(f"Generated URL for {process_key}:")
    logging.info(url)
    
    # Check for required parameters
    required_params = ["_adjustPlanHours=on", "_hideEmptyLineItems=on", "employmentType=AllEmployees"]
    missing_params = []
    
    for param in required_params:
        if param not in url:
            missing_params.append(param)
    
    if missing_params:
        logging.error(f"✗ Missing URL parameters: {missing_params}")
    else:
        logging.info("✓ All required URL parameters present")

def main():
    """Main test function."""
    logging.info("Starting PPR fixes validation...")
    
    # Test URL parameters
    test_url_parameters()
    logging.info("")
    
    # Test PPR fixes
    test_ppr_fixes()
    
    logging.info("=" * 80)
    logging.info("TESTING COMPLETE")
    logging.info("=" * 80)

if __name__ == "__main__":
    main() 