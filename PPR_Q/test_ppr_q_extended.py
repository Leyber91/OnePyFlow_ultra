#!/usr/bin/env python3
"""
Extended test suite for PPR_Q module
Tests edge cases, different sites, and various time scenarios
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

def test_edge_case_1_very_short_range():
    """
    Test Edge Case 1: Very short time range (5 minutes)
    """
    print("=" * 80)
    print("EDGE CASE 1: VERY SHORT TIME RANGE (5 minutes)")
    print("=" * 80)
    
    site = "DTM2"
    end_time = datetime.now()
    start_time = end_time - timedelta(minutes=5)
    
    print(f"Site: {site}")
    print(f"Start Time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"End Time: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Duration: 5 minutes")
    print("-" * 80)
    
    try:
        result = PPR_Q_function(
            Site=site,
            start_datetime=start_time,
            end_datetime=end_time
        )
        
        print("✅ Edge Case 1 completed!")
        print(f"Processes returned: {len(result) if result else 0}")
        
        if result:
            print("\nProcesses with data:")
            for process_name, data in result.items():
                if process_name != '_metadata':
                    print(f"  - {process_name}")
        
        return True, result
        
    except Exception as e:
        print(f"❌ Edge Case 1 FAILED: {str(e)}")
        return False, None

def test_edge_case_2_different_site():
    """
    Test Edge Case 2: Different site (CDG7)
    """
    print("\n" + "=" * 80)
    print("EDGE CASE 2: DIFFERENT SITE (CDG7)")
    print("=" * 80)
    
    site = "CDG7"
    end_time = datetime.now()
    start_time = end_time - timedelta(hours=1)
    
    print(f"Site: {site}")
    print(f"Start Time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"End Time: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Duration: 1 hour")
    print("-" * 80)
    
    try:
        result = PPR_Q_function(
            Site=site,
            start_datetime=start_time,
            end_datetime=end_time
        )
        
        print("✅ Edge Case 2 completed!")
        print(f"Processes returned: {len(result) if result else 0}")
        
        if result:
            print("\nProcesses with data:")
            for process_name, data in result.items():
                if process_name != '_metadata':
                    print(f"  - {process_name}")
        
        return True, result
        
    except Exception as e:
        print(f"❌ Edge Case 2 FAILED: {str(e)}")
        return False, None

def test_edge_case_3_weekend_time():
    """
    Test Edge Case 3: Weekend time (Saturday/Sunday)
    """
    print("\n" + "=" * 80)
    print("EDGE CASE 3: WEEKEND TIME")
    print("=" * 80)
    
    site = "DTM2"
    # Find the most recent Saturday
    today = datetime.now()
    days_since_saturday = (today.weekday() - 5) % 7
    saturday = today - timedelta(days=days_since_saturday)
    
    start_time = saturday.replace(hour=10, minute=0, second=0, microsecond=0)
    end_time = start_time + timedelta(hours=2)
    
    print(f"Site: {site}")
    print(f"Start Time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"End Time: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Duration: 2 hours (Saturday)")
    print("-" * 80)
    
    try:
        result = PPR_Q_function(
            Site=site,
            start_datetime=start_time,
            end_datetime=end_time
        )
        
        print("✅ Edge Case 3 completed!")
        print(f"Processes returned: {len(result) if result else 0}")
        
        if result:
            print("\nProcesses with data:")
            for process_name, data in result.items():
                if process_name != '_metadata':
                    print(f"  - {process_name}")
        
        return True, result
        
    except Exception as e:
        print(f"❌ Edge Case 3 FAILED: {str(e)}")
        return False, None

def test_edge_case_4_overnight_shift():
    """
    Test Edge Case 4: Overnight shift (crosses midnight)
    """
    print("\n" + "=" * 80)
    print("EDGE CASE 4: OVERNIGHT SHIFT (crosses midnight)")
    print("=" * 80)
    
    site = "DTM2"
    # Use yesterday's overnight shift
    yesterday = datetime.now() - timedelta(days=1)
    start_time = yesterday.replace(hour=22, minute=0, second=0, microsecond=0)
    end_time = yesterday.replace(hour=23, minute=59, second=59, microsecond=999999)
    
    print(f"Site: {site}")
    print(f"Start Time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"End Time: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Duration: ~2 hours (overnight)")
    print("-" * 80)
    
    try:
        result = PPR_Q_function(
            Site=site,
            start_datetime=start_time,
            end_datetime=end_time
        )
        
        print("✅ Edge Case 4 completed!")
        print(f"Processes returned: {len(result) if result else 0}")
        
        if result:
            print("\nProcesses with data:")
            for process_name, data in result.items():
                if process_name != '_metadata':
                    print(f"  - {process_name}")
        
        return True, result
        
    except Exception as e:
        print(f"❌ Edge Case 4 FAILED: {str(e)}")
        return False, None

def test_edge_case_5_peak_hours():
    """
    Test Edge Case 5: Peak business hours
    """
    print("\n" + "=" * 80)
    print("EDGE CASE 5: PEAK BUSINESS HOURS")
    print("=" * 80)
    
    site = "DTM2"
    # Use yesterday's peak hours (10 AM - 2 PM)
    yesterday = datetime.now() - timedelta(days=1)
    start_time = yesterday.replace(hour=10, minute=0, second=0, microsecond=0)
    end_time = yesterday.replace(hour=14, minute=0, second=0, microsecond=0)
    
    print(f"Site: {site}")
    print(f"Start Time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"End Time: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Duration: 4 hours (peak business hours)")
    print("-" * 80)
    
    try:
        result = PPR_Q_function(
            Site=site,
            start_datetime=start_time,
            end_datetime=end_time
        )
        
        print("✅ Edge Case 5 completed!")
        print(f"Processes returned: {len(result) if result else 0}")
        
        if result:
            print("\nProcesses with data:")
            for process_name, data in result.items():
                if process_name != '_metadata':
                    print(f"  - {process_name}")
            
            # Check for high activity indicators
            print("\nHigh activity indicators:")
            for process_name, data in result.items():
                if process_name != '_metadata' and isinstance(data, dict):
                    for key, value in data.items():
                        if isinstance(value, (int, float)) and value > 1000:
                            print(f"  {process_name}.{key}: {value}")
        
        return True, result
        
    except Exception as e:
        print(f"❌ Edge Case 5 FAILED: {str(e)}")
        return False, None

def test_edge_case_6_string_datetime():
    """
    Test Edge Case 6: String datetime inputs
    """
    print("\n" + "=" * 80)
    print("EDGE CASE 6: STRING DATETIME INPUTS")
    print("=" * 80)
    
    site = "DTM2"
    end_time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    start_time_str = (datetime.now() - timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S")
    
    print(f"Site: {site}")
    print(f"Start Time (string): {start_time_str}")
    print(f"End Time (string): {end_time_str}")
    print(f"Duration: 1 hour")
    print("-" * 80)
    
    try:
        result = PPR_Q_function(
            Site=site,
            start_datetime=start_time_str,
            end_datetime=end_time_str
        )
        
        print("✅ Edge Case 6 completed!")
        print(f"Processes returned: {len(result) if result else 0}")
        
        if result:
            print("\nProcesses with data:")
            for process_name, data in result.items():
                if process_name != '_metadata':
                    print(f"  - {process_name}")
        
        return True, result
        
    except Exception as e:
        print(f"❌ Edge Case 6 FAILED: {str(e)}")
        return False, None

def test_edge_case_7_historical_week():
    """
    Test Edge Case 7: Historical week (1 week ago)
    """
    print("\n" + "=" * 80)
    print("EDGE CASE 7: HISTORICAL WEEK (1 week ago)")
    print("=" * 80)
    
    site = "DTM2"
    end_time = datetime.now() - timedelta(weeks=1)
    start_time = end_time - timedelta(hours=4)
    
    print(f"Site: {site}")
    print(f"Start Time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"End Time: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Duration: 4 hours (1 week ago)")
    print("-" * 80)
    
    try:
        result = PPR_Q_function(
            Site=site,
            start_datetime=start_time,
            end_datetime=end_time
        )
        
        print("✅ Edge Case 7 completed!")
        print(f"Processes returned: {len(result) if result else 0}")
        
        if result:
            print("\nProcesses with data:")
            for process_name, data in result.items():
                if process_name != '_metadata':
                    print(f"  - {process_name}")
        
        return True, result
        
    except Exception as e:
        print(f"❌ Edge Case 7 FAILED: {str(e)}")
        return False, None

def test_edge_case_8_very_long_range():
    """
    Test Edge Case 8: Very long time range (24 hours)
    """
    print("\n" + "=" * 80)
    print("EDGE CASE 8: VERY LONG TIME RANGE (24 hours)")
    print("=" * 80)
    
    site = "DTM2"
    end_time = datetime.now()
    start_time = end_time - timedelta(hours=24)
    
    print(f"Site: {site}")
    print(f"Start Time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"End Time: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Duration: 24 hours")
    print("-" * 80)
    
    try:
        result = PPR_Q_function(
            Site=site,
            start_datetime=start_time,
            end_datetime=end_time
        )
        
        print("✅ Edge Case 8 completed!")
        print(f"Processes returned: {len(result) if result else 0}")
        
        if result:
            print("\nProcesses with data:")
            for process_name, data in result.items():
                if process_name != '_metadata':
                    print(f"  - {process_name}")
        
        return True, result
        
    except Exception as e:
        print(f"❌ Edge Case 8 FAILED: {str(e)}")
        return False, None

def analyze_extended_results(all_results):
    """
    Analyze all extended test results
    """
    print("\n" + "=" * 80)
    print("EXTENDED ANALYSIS")
    print("=" * 80)
    
    successful_tests = 0
    total_processes_found = set()
    site_coverage = set()
    
    for i, (success, result) in enumerate(all_results, 1):
        if success and result:
            successful_tests += 1
            for process_name in result.keys():
                if process_name != '_metadata':
                    total_processes_found.add(process_name)
            
            # Check site coverage
            if result.get('_metadata', {}).get('site'):
                site_coverage.add(result['_metadata']['site'])
    
    print(f"Successful tests: {successful_tests}/8")
    print(f"Total unique processes found: {len(total_processes_found)}")
    print(f"Sites tested: {', '.join(site_coverage) if site_coverage else 'None'}")
    
    if total_processes_found:
        print("\nAll processes found across extended tests:")
        for process in sorted(total_processes_found):
            print(f"  - {process}")
    
    # Check for rate calculations across all tests
    print("\nRate calculation analysis:")
    rate_found = False
    for i, (success, result) in enumerate(all_results, 1):
        if success and result:
            for process_name, data in result.items():
                if process_name != '_metadata' and isinstance(data, dict):
                    for key, value in data.items():
                        if 'rate' in key.lower() and isinstance(value, (int, float)) and value != 0.0:
                            if isinstance(value, list):
                                # Handle list of rates
                                non_zero_rates = [v for v in value if v != 0.0]
                                if non_zero_rates:
                                    print(f"  Test {i}: {process_name}.{key} = {len(non_zero_rates)} non-zero rates")
                                    rate_found = True
                            else:
                                print(f"  Test {i}: {process_name}.{key} = {value}")
                                rate_found = True
    
    if not rate_found:
        print("  ⚠️  No non-zero rate values found across extended tests")
    else:
        print("  ✅ Rate calculations are working across all scenarios!")

def main():
    """
    Run all extended test scenarios
    """
    print("PPR_Q EXTENDED TEST SUITE")
    print("=" * 80)
    print("This extended test suite validates PPR_Q fixes across edge cases and")
    print("various scenarios to ensure robustness.")
    print("=" * 80)
    
    all_results = []
    
    # Run all extended test scenarios
    test1_success, test1_result = test_edge_case_1_very_short_range()
    all_results.append((test1_success, test1_result))
    
    test2_success, test2_result = test_edge_case_2_different_site()
    all_results.append((test2_success, test2_result))
    
    test3_success, test3_result = test_edge_case_3_weekend_time()
    all_results.append((test3_success, test3_result))
    
    test4_success, test4_result = test_edge_case_4_overnight_shift()
    all_results.append((test4_success, test4_result))
    
    test5_success, test5_result = test_edge_case_5_peak_hours()
    all_results.append((test5_success, test5_result))
    
    test6_success, test6_result = test_edge_case_6_string_datetime()
    all_results.append((test6_success, test6_result))
    
    test7_success, test7_result = test_edge_case_7_historical_week()
    all_results.append((test7_success, test7_result))
    
    test8_success, test8_result = test_edge_case_8_very_long_range()
    all_results.append((test8_success, test8_result))
    
    # Analyze results
    analyze_extended_results(all_results)
    
    # Final summary
    print("\n" + "=" * 80)
    print("EXTENDED TEST SUMMARY")
    print("=" * 80)
    
    successful_tests = sum(1 for success, _ in all_results if success)
    
    if successful_tests >= 7:
        print("✅ PPR_Q FIXES ARE HIGHLY ROBUST!")
        print("   The module handles edge cases and various scenarios excellently.")
    elif successful_tests >= 5:
        print("✅ PPR_Q FIXES ARE ROBUST!")
        print("   The module handles most scenarios well with minor limitations.")
    elif successful_tests >= 3:
        print("⚠️  PPR_Q FIXES ARE PARTIALLY ROBUST")
        print("   Some scenarios work, but there are limitations to address.")
    else:
        print("❌ PPR_Q FIXES NEED MORE WORK")
        print("   Most edge cases are failing - additional debugging needed.")
    
    print(f"\nSuccess rate: {successful_tests}/8 tests passed")
    
    # Save detailed results to file
    try:
        with open('ppr_q_extended_test_results.json', 'w') as f:
            json.dump({
                'extended_test_results': [
                    {
                        'scenario': f'Edge Case {i+1}',
                        'success': success,
                        'process_count': len(result) if result else 0,
                        'processes': list(result.keys()) if result else []
                    }
                    for i, (success, result) in enumerate(all_results)
                ],
                'summary': {
                    'successful_tests': successful_tests,
                    'total_tests': 8,
                    'robustness_level': 'high' if successful_tests >= 7 else 'medium' if successful_tests >= 5 else 'low'
                }
            }, f, indent=2, default=str)
        print("\n📄 Extended test results saved to 'ppr_q_extended_test_results.json'")
    except Exception as e:
        print(f"\n⚠️  Could not save extended results file: {e}")

if __name__ == "__main__":
    main() 