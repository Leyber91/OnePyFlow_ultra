#!/usr/bin/env python3
"""
Quick comprehensive test for PPR_Q module
Tests key scenarios efficiently
"""

import json
import logging
from datetime import datetime, timedelta
from PPR_Q_FF import PPR_Q_function

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

def quick_test_1_current_hour():
    """Test current hour data"""
    print("=" * 60)
    print("QUICK TEST 1: CURRENT HOUR")
    print("=" * 60)
    
    site = "DTM2"
    end_time = datetime.now()
    start_time = end_time - timedelta(hours=1)
    
    print(f"Site: {site}")
    print(f"Time: {start_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')}")
    
    try:
        result = PPR_Q_function(Site=site, start_datetime=start_time, end_datetime=end_time)
        print(f"✅ SUCCESS: {len(result) if result else 0} processes")
        return True, result
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False, None

def quick_test_2_different_site():
    """Test different site"""
    print("\n" + "=" * 60)
    print("QUICK TEST 2: DIFFERENT SITE (CDG7)")
    print("=" * 60)
    
    site = "CDG7"
    end_time = datetime.now() - timedelta(days=1)
    start_time = end_time - timedelta(hours=2)
    
    print(f"Site: {site}")
    print(f"Time: {start_time.strftime('%Y-%m-%d %H:%M')} - {end_time.strftime('%H:%M')}")
    
    try:
        result = PPR_Q_function(Site=site, start_datetime=start_time, end_datetime=end_time)
        print(f"✅ SUCCESS: {len(result) if result else 0} processes")
        return True, result
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False, None

def quick_test_3_string_inputs():
    """Test string datetime inputs"""
    print("\n" + "=" * 60)
    print("QUICK TEST 3: STRING DATETIME INPUTS")
    print("=" * 60)
    
    site = "DTM2"
    end_time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    start_time_str = (datetime.now() - timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S")
    
    print(f"Site: {site}")
    print(f"Inputs: String format")
    
    try:
        result = PPR_Q_function(Site=site, start_datetime=start_time_str, end_datetime=end_time_str)
        print(f"✅ SUCCESS: {len(result) if result else 0} processes")
        return True, result
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False, None

def quick_test_4_peak_hours():
    """Test peak business hours"""
    print("\n" + "=" * 60)
    print("QUICK TEST 4: PEAK BUSINESS HOURS")
    print("=" * 60)
    
    site = "DTM2"
    yesterday = datetime.now() - timedelta(days=1)
    start_time = yesterday.replace(hour=10, minute=0, second=0, microsecond=0)
    end_time = yesterday.replace(hour=12, minute=0, second=0, microsecond=0)
    
    print(f"Site: {site}")
    print(f"Time: {start_time.strftime('%Y-%m-%d %H:%M')} - {end_time.strftime('%H:%M')}")
    
    try:
        result = PPR_Q_function(Site=site, start_datetime=start_time, end_datetime=end_time)
        print(f"✅ SUCCESS: {len(result) if result else 0} processes")
        
        # Check for high activity
        if result:
            high_activity = []
            for process_name, data in result.items():
                if process_name != '_metadata' and isinstance(data, dict):
                    for key, value in data.items():
                        if isinstance(value, (int, float)) and value > 500:
                            high_activity.append(f"{process_name}.{key}: {value}")
            
            if high_activity:
                print(f"📊 High activity found: {len(high_activity)} metrics > 500")
        
        return True, result
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False, None

def main():
    """Run all quick tests"""
    print("PPR_Q QUICK COMPREHENSIVE TEST")
    print("=" * 60)
    
    all_results = []
    
    # Run tests
    test1_success, test1_result = quick_test_1_current_hour()
    all_results.append((test1_success, test1_result))
    
    test2_success, test2_result = quick_test_2_different_site()
    all_results.append((test2_success, test2_result))
    
    test3_success, test3_result = quick_test_3_string_inputs()
    all_results.append((test3_success, test3_result))
    
    test4_success, test4_result = quick_test_4_peak_hours()
    all_results.append((test4_success, test4_result))
    
    # Summary
    print("\n" + "=" * 60)
    print("QUICK TEST SUMMARY")
    print("=" * 60)
    
    successful_tests = sum(1 for success, _ in all_results if success)
    total_processes = set()
    
    for success, result in all_results:
        if success and result:
            for process_name in result.keys():
                if process_name != '_metadata':
                    total_processes.add(process_name)
    
    print(f"✅ Success Rate: {successful_tests}/4 tests passed")
    print(f"📊 Total Processes Found: {len(total_processes)}")
    
    if total_processes:
        print("\nProcesses tested:")
        for process in sorted(total_processes):
            print(f"  - {process}")
    
    if successful_tests >= 3:
        print("\n🎉 PPR_Q IS WORKING EXCELLENTLY!")
        print("   Ready for production use.")
    elif successful_tests >= 2:
        print("\n✅ PPR_Q IS WORKING WELL!")
        print("   Minor issues but generally functional.")
    else:
        print("\n⚠️  PPR_Q NEEDS ATTENTION")
        print("   Some tests failed - review needed.")

if __name__ == "__main__":
    main() 