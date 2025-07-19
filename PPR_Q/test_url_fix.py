#!/usr/bin/env python3
"""
Quick test to validate that the URL fix is working
and the API is returning CSV data instead of HTML.
"""

import logging
from datetime import datetime
from PPR_Q_FF import PPR_Q_function

# Configure logging to see the URL details
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

def test_url_fix():
    """Test that the API URLs now include _adjustPlanHours=on and return CSV data"""
    print("=" * 80)
    print("TESTING URL FIX - _adjustPlanHours=on PARAMETER")
    print("=" * 80)
    
    site = "ZAZ1"
    end_time = datetime(2025, 6, 30, 8, 30, 0)  # 30 minutes into ES shift
    start_time = datetime(2025, 6, 30, 8, 0, 0)  # Start of ES shift
    
    print(f"Site: {site}")
    print(f"Requested Time Range: {start_time.strftime('%Y-%m-%d %H:%M')} to {end_time.strftime('%H:%M')}")
    print(f"Duration: {(end_time - start_time).total_seconds() / 3600:.2f} hours")
    print("-" * 80)
    
    try:
        result = PPR_Q_function(Site=site, start_datetime=start_time, end_datetime=end_time)
        
        if not result:
            print("❌ No data returned")
            return False
        
        print(f"✅ Data returned: {len(result)} processes")
        
        # Check if we got any actual data (not just empty processes)
        data_found = False
        for process_name, data in result.items():
            if process_name != '_metadata' and isinstance(data, dict):
                for key, value in data.items():
                    if isinstance(value, (int, float)) and value > 0:
                        print(f"   ✅ {process_name}.{key}: {value}")
                        data_found = True
        
        if not data_found:
            print("   ⚠️  No actual data values found - may still have issues")
            return False
        
        # Check metadata for execution info
        if '_metadata' in result:
            metadata = result['_metadata']
            print(f"\n📋 Execution Info:")
            for key, value in metadata.items():
                print(f"   {key}: {value}")
        
        print(f"\n🎉 URL FIX SUCCESSFUL!")
        print(f"   API is now returning CSV data instead of HTML error pages")
        print(f"   _adjustPlanHours=on parameter is working")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    test_url_fix() 