#!/usr/bin/env python3
"""
Comprehensive test script for the FIXED PPR_Q module
Tests multiple scenarios to validate the API limitation workarounds
"""

import json
import sys
import logging
from datetime import datetime, timedelta
from PPR_Q_FF import PPR_Q_function

# Configure logging for better debugging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)

def test_scenario_1_short_range():
    """
    Test 1: Very short time range (30 minutes) - most likely to fail with original API
    """
    print("=" * 80)
    print("TEST SCENARIO 1: SHORT TIME RANGE (30 minutes)")
    print("=" * 80)
    
    site = "DTM2"
    end_time = datetime.now()
    start_time = end_time - timedelta(minutes=30)
    
    print(f"Site: {site}")
    print(f"Start Time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"End Time: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Duration: 30 minutes")
    print("-" * 80)
    
    try:
        result = PPR_Q_function(
            Site=site,
            start_datetime=start_time,
            end_datetime=end_time
        )
        
        print("✅ Test 1 completed!")
        print(f"Processes returned: {len(result) if result else 0}")
        
        if result:
            print("\nProcesses with data:")
            for process_name, data in result.items():
                if process_name != '_metadata':
                    print(f"  - {process_name}")
            
            # Check for rate values
            print("\nRate values found:")
            for process_name, data in result.items():
                if process_name != '_metadata' and isinstance(data, dict):
                    for key, value in data.items():
                        if 'rate' in key.lower() and value != 0.0:
                            print(f"  {process_name}.{key}: {value}")
        
        return True, result
        
    except Exception as e:
        print(f"❌ Test 1 FAILED: {str(e)}")
        return False, None

def test_scenario_2_medium_range():
    """
    Test 2: Medium time range (2 hours) - should work better
    """
    print("\n" + "=" * 80)
    print("TEST SCENARIO 2: MEDIUM TIME RANGE (2 hours)")
    print("=" * 80)
    
    site = "DTM2"
    end_time = datetime.now()
    start_time = end_time - timedelta(hours=2)
    
    print(f"Site: {site}")
    print(f"Start Time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"End Time: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Duration: 2 hours")
    print("-" * 80)
    
    try:
        result = PPR_Q_function(
            Site=site,
            start_datetime=start_time,
            end_datetime=end_time
        )
        
        print("✅ Test 2 completed!")
        print(f"Processes returned: {len(result) if result else 0}")
        
        if result:
            print("\nProcesses with data:")
            for process_name, data in result.items():
                if process_name != '_metadata':
                    print(f"  - {process_name}")
        
        return True, result
        
    except Exception as e:
        print(f"❌ Test 2 FAILED: {str(e)}")
        return False, None

def test_scenario_3_historical_range():
    """
    Test 3: Historical time range (yesterday) - should work well
    """
    print("\n" + "=" * 80)
    print("TEST SCENARIO 3: HISTORICAL TIME RANGE (yesterday)")
    print("=" * 80)
    
    site = "DTM2"
    end_time = datetime.now() - timedelta(days=1)
    start_time = end_time - timedelta(hours=2)
    
    print(f"Site: {site}")
    print(f"Start Time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"End Time: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Duration: 2 hours (yesterday)")
    print("-" * 80)
    
    try:
        result = PPR_Q_function(
            Site=site,
            start_datetime=start_time,
            end_datetime=end_time
        )
        
        print("✅ Test 3 completed!")
        print(f"Processes returned: {len(result) if result else 0}")
        
        if result:
            print("\nProcesses with data:")
            for process_name, data in result.items():
                if process_name != '_metadata':
                    print(f"  - {process_name}")
        
        return True, result
        
    except Exception as e:
        print(f"❌ Test 3 FAILED: {str(e)}")
        return False, None

def test_scenario_4_custom_time():
    """
    Test 4: Custom time range with specific shift hours
    """
    print("\n" + "=" * 80)
    print("TEST SCENARIO 4: CUSTOM SHIFT TIME RANGE")
    print("=" * 80)
    
    site = "DTM2"
    # Use a specific shift time (6 AM to 8 AM)
    start_time = datetime.now().replace(hour=6, minute=0, second=0, microsecond=0)
    end_time = start_time + timedelta(hours=2)
    
    print(f"Site: {site}")
    print(f"Start Time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"End Time: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Duration: 2 hours (6 AM - 8 AM)")
    print("-" * 80)
    
    try:
        result = PPR_Q_function(
            Site=site,
            start_datetime=start_time,
            end_datetime=end_time
        )
        
        print("✅ Test 4 completed!")
        print(f"Processes returned: {len(result) if result else 0}")
        
        if result:
            print("\nProcesses with data:")
            for process_name, data in result.items():
                if process_name != '_metadata':
                    print(f"  - {process_name}")
        
        return True, result
        
    except Exception as e:
        print(f"❌ Test 4 FAILED: {str(e)}")
        return False, None

def analyze_results(all_results):
    """
    Analyze all test results to provide insights
    """
    print("\n" + "=" * 80)
    print("COMPREHENSIVE ANALYSIS")
    print("=" * 80)
    
    successful_tests = 0
    total_processes_found = set()
    
    for i, (success, result) in enumerate(all_results, 1):
        if success and result:
            successful_tests += 1
            for process_name in result.keys():
                if process_name != '_metadata':
                    total_processes_found.add(process_name)
    
    print(f"Successful tests: {successful_tests}/4")
    print(f"Total unique processes found: {len(total_processes_found)}")
    
    if total_processes_found:
        print("\nAll processes found across tests:")
        for process in sorted(total_processes_found):
            print(f"  - {process}")
    
    # Check for rate calculations
    print("\nRate calculation analysis:")
    rate_found = False
    for i, (success, result) in enumerate(all_results, 1):
        if success and result:
            for process_name, data in result.items():
                if process_name != '_metadata' and isinstance(data, dict):
                    for key, value in data.items():
                        if 'rate' in key.lower() and value != 0.0:
                            print(f"  Test {i}: {process_name}.{key} = {value}")
                            rate_found = True
    
    if not rate_found:
        print("  ⚠️  No non-zero rate values found - this might indicate the API is still not calculating rates properly")
    else:
        print("  ✅ Rate calculations are working!")

def main():
    """
    Run all test scenarios
    """
    print("PPR_Q FIXED - COMPREHENSIVE TEST SUITE")
    print("=" * 80)
    print("This test suite validates the fixes for the PPR_Q API limitations.")
    print("It tests multiple scenarios to ensure the fallback logic works correctly.")
    print("=" * 80)
    
    all_results = []
    
    # Run all test scenarios
    test1_success, test1_result = test_scenario_1_short_range()
    all_results.append((test1_success, test1_result))
    
    test2_success, test2_result = test_scenario_2_medium_range()
    all_results.append((test2_success, test2_result))
    
    test3_success, test3_result = test_scenario_3_historical_range()
    all_results.append((test3_success, test3_result))
    
    test4_success, test4_result = test_scenario_4_custom_time()
    all_results.append((test4_success, test4_result))
    
    # Analyze results
    analyze_results(all_results)
    
    # Final summary
    print("\n" + "=" * 80)
    print("FINAL SUMMARY")
    print("=" * 80)
    
    successful_tests = sum(1 for success, _ in all_results if success)
    
    if successful_tests >= 3:
        print("✅ PPR_Q FIXES ARE WORKING WELL!")
        print("   The fallback logic is successfully handling API limitations.")
    elif successful_tests >= 2:
        print("⚠️  PPR_Q FIXES ARE PARTIALLY WORKING")
        print("   Some scenarios work, but there may still be issues.")
    else:
        print("❌ PPR_Q FIXES NEED MORE WORK")
        print("   Most scenarios are failing - additional debugging needed.")
    
    print(f"\nSuccess rate: {successful_tests}/4 tests passed")
    
    # Save detailed results to file
    try:
        with open('ppr_q_test_results.json', 'w') as f:
            json.dump({
                'test_results': [
                    {
                        'scenario': f'Test {i+1}',
                        'success': success,
                        'process_count': len(result) if result else 0,
                        'processes': list(result.keys()) if result else []
                    }
                    for i, (success, result) in enumerate(all_results)
                ],
                'summary': {
                    'successful_tests': successful_tests,
                    'total_tests': 4
                }
            }, f, indent=2, default=str)
        print("\n📄 Detailed results saved to 'ppr_q_test_results.json'")
    except Exception as e:
        print(f"\n⚠️  Could not save results file: {e}")

if __name__ == "__main__":
    main() 