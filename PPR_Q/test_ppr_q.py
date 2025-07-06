#!/usr/bin/env python3
"""
Test script for PPR_Q module
Tests the PPR_Q functionality with a small time range to verify it works
"""

import json
import sys
from datetime import datetime, timedelta
from PPR_Q_FF import PPR_Q_function

def test_ppr_q():
    """
    Test PPR_Q with a small time range to verify functionality
    """
    print("=" * 60)
    print("TESTING PPR_Q MODULE")
    print("=" * 60)
    
    # Test parameters
    site = "DTM2"  # You can change this to your site
    
    # Use a recent time range (last hour for testing)
    end_time = datetime.now()
    start_time = end_time - timedelta(minutes=30)  # 30 minute window for testing
    
    print(f"Site: {site}")
    print(f"Start Time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"End Time: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Duration: 30 minutes")
    print("-" * 60)
    
    try:
        print("Starting PPR_Q data fetch...")
        
        # Call PPR_Q function
        result = PPR_Q_function(
            Site=site,
            start_datetime=start_time,
            end_datetime=end_time
        )
        
        print("PPR_Q completed successfully!")
        print("-" * 60)
        print("RESULTS SUMMARY:")
        print("-" * 60)
        
        if result:
            print(f"Number of processes returned: {len(result)}")
            print("\nProcesses found:")
            for process_name in result.keys():
                print(f"  - {process_name}")
            
            print("\n" + "=" * 60)
            print("DETAILED RESULTS:")
            print("=" * 60)
            print(json.dumps(result, indent=2, default=str))
            
        else:
            print("No data returned - this might be expected if no activity during the time range")
            
    except Exception as e:
        print(f"ERROR: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        print("Full traceback:")
        traceback.print_exc()
        return False
    
    return True

def test_with_custom_time():
    """
    Test with a custom time range that you can specify
    """
    print("\n" + "=" * 60)
    print("CUSTOM TIME RANGE TEST")
    print("=" * 60)
    
    # You can modify these for your specific test
    site = "DTM2"
    start_datetime = "2025-01-14 06:00:00"  # Modify as needed
    end_datetime = "2025-01-14 06:30:00"    # Modify as needed
    
    print(f"Site: {site}")
    print(f"Start Time: {start_datetime}")
    print(f"End Time: {end_datetime}")
    print("-" * 60)
    
    try:
        result = PPR_Q_function(
            Site=site,
            start_datetime=start_datetime,
            end_datetime=end_datetime
        )
        
        print("Custom time range test completed!")
        print(f"Processes returned: {len(result) if result else 0}")
        
        if result:
            for process_name, data in result.items():
                print(f"\n{process_name}:")
                if isinstance(data, dict):
                    for key, value in data.items():
                        print(f"  {key}: {value}")
                        
    except Exception as e:
        print(f"Custom test ERROR: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    print("PPR_Q Test Suite")
    print("================")
    
    # Test 1: Recent time range
    success1 = test_ppr_q()
    
    # Test 2: Custom time range (uncomment to run)
    # success2 = test_with_custom_time()
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Recent time test: {'PASSED' if success1 else 'FAILED'}")
    # print(f"Custom time test: {'PASSED' if success2 else 'FAILED'}")
    
    if success1:
        print("\n✅ PPR_Q module is working correctly!")
        print("You can now use it in your main application.")
    else:
        print("\n❌ PPR_Q module has issues that need to be resolved.") 