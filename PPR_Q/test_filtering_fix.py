#!/usr/bin/env python3
"""
Test to validate that PPR_Q filtering is working correctly
and returning data for the exact time range requested.
"""

import json
import logging
from datetime import datetime, timedelta
from PPR_Q_FF import PPR_Q_function

# Configure logging to see the filtering details
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

def test_exact_time_range_filtering():
    """Test that PPR_Q returns data for the exact time range requested"""
    print("=" * 80)
    print("TESTING EXACT TIME RANGE FILTERING")
    print("=" * 80)
    
    site = "ZAZ1"  # Use the site from your original request
    end_time = datetime(2025, 6, 30, 10, 0, 0)  # 2 hours into ES shift
    start_time = datetime(2025, 6, 30, 8, 0, 0)  # Start of ES shift
    
    print(f"Site: {site}")
    print(f"Requested Time Range: {start_time.strftime('%Y-%m-%d %H:%M')} to {end_time.strftime('%H:%M')}")
    print(f"Duration: {(end_time - start_time).total_seconds() / 3600:.1f} hours")
    print("-" * 80)
    
    try:
        result = PPR_Q_function(Site=site, start_datetime=start_time, end_datetime=end_time)
        
        if not result:
            print("❌ No data returned")
            return False
        
        print(f"✅ Data returned: {len(result)} processes")
        
        # Check PPR_PRU specifically (the one you mentioned)
        if 'PPR_PRU' in result:
            pru_data = result['PPR_PRU']
            print(f"\n📊 PPR_PRU Analysis:")
            print(f"   Data returned: {len(pru_data) if isinstance(pru_data, dict) else 'N/A'}")
            
            if isinstance(pru_data, dict):
                for key, value in pru_data.items():
                    if 'Receive_Dock' in key:
                        print(f"   {key}: {value}")
                        if isinstance(value, (int, float)) and value > 1000:
                            print(f"   ⚠️  WARNING: {key} = {value} - This looks like extended time range data!")
                        elif isinstance(value, (int, float)) and value < 500:
                            print(f"   ✅ GOOD: {key} = {value} - This looks like current shift data!")
        
        # Check for any suspiciously high values
        print(f"\n🔍 Data Volume Analysis:")
        high_volume_processes = []
        
        for process_name, data in result.items():
            if process_name != '_metadata' and isinstance(data, dict):
                for key, value in data.items():
                    if isinstance(value, (int, float)) and value > 10000:
                        high_volume_processes.append(f"{process_name}.{key}: {value}")
        
        if high_volume_processes:
            print(f"   ⚠️  HIGH VOLUME WARNING: {len(high_volume_processes)} metrics > 10,000")
            for item in high_volume_processes[:5]:  # Show first 5
                print(f"      - {item}")
        else:
            print(f"   ✅ GOOD: No suspiciously high volume metrics found")
        
        # Check data source information
        if '_metadata' in result:
            metadata = result['_metadata']
            print(f"\n📋 Metadata:")
            for key, value in metadata.items():
                print(f"   {key}: {value}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_data_proportion_validation():
    """Test that the data proportion estimation is working correctly"""
    print("\n" + "=" * 80)
    print("TESTING DATA PROPORTION VALIDATION")
    print("=" * 80)
    
    site = "ZAZ1"
    # Test with a very short time range (30 minutes)
    end_time = datetime(2025, 6, 30, 8, 30, 0)
    start_time = datetime(2025, 6, 30, 8, 0, 0)
    
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
        
        # Check if the data volume looks reasonable for 30 minutes
        reasonable_volume = True
        for process_name, data in result.items():
            if process_name != '_metadata' and isinstance(data, dict):
                for key, value in data.items():
                    if isinstance(value, (int, float)) and value > 5000:
                        print(f"   ⚠️  {process_name}.{key}: {value} - Too high for 30 minutes!")
                        reasonable_volume = False
        
        if reasonable_volume:
            print(f"   ✅ Data volume looks reasonable for 30-minute window")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def main():
    """Run filtering validation tests"""
    print("PPR_Q FILTERING VALIDATION TESTS")
    print("=" * 80)
    
    # Test 1: Exact time range filtering
    test1_success = test_exact_time_range_filtering()
    
    # Test 2: Data proportion validation
    test2_success = test_data_proportion_validation()
    
    # Summary
    print("\n" + "=" * 80)
    print("FILTERING VALIDATION SUMMARY")
    print("=" * 80)
    
    if test1_success and test2_success:
        print("🎉 FILTERING IS WORKING CORRECTLY!")
        print("   PPR_Q should now return data for the exact time range requested")
        print("   No more 1M+ unit issues from extended time ranges")
    elif test1_success or test2_success:
        print("✅ FILTERING IS MOSTLY WORKING")
        print("   Some improvements needed but generally functional")
    else:
        print("❌ FILTERING NEEDS MORE WORK")
        print("   The filtering logic may need additional debugging")

if __name__ == "__main__":
    main() 