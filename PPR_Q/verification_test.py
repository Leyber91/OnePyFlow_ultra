#!/usr/bin/env python3
"""
VERIFICATION TEST - Double-check that all fixes are working correctly
Focus on the original issue and any remaining problems identified.
"""

import json
import logging
import time
from datetime import datetime
from PPR_Q_FF import PPR_Q_function

# Configure logging to see detailed information
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

def verify_original_issue_fix():
    """Test 1: Verify the original issue is completely fixed"""
    print("=" * 80)
    print("VERIFICATION 1: ORIGINAL ISSUE FIX")
    print("=" * 80)
    
    site = "ZAZ1"
    end_time = datetime(2025, 6, 30, 10, 0, 0)  # 2 hours into ES shift
    start_time = datetime(2025, 6, 30, 8, 0, 0)  # Start of ES shift
    
    print(f"Original Issue: PPR_PRU > PRU_Receive_Dock = 553 u/h (expected ~1700)")
    print(f"Original Issue: 1M+ units processed (expected ~3400)")
    print("-" * 80)
    print(f"Site: {site}")
    print(f"Time Range: {start_time.strftime('%Y-%m-%d %H:%M')} to {end_time.strftime('%H:%M')}")
    print(f"Duration: {(end_time - start_time).total_seconds() / 3600:.1f} hours")
    print("-" * 80)
    
    try:
        result = PPR_Q_function(Site=site, start_datetime=start_time, end_datetime=end_time)
        
        if not result:
            print("❌ No data returned")
            return False
        
        print(f"✅ Data returned: {len(result)} processes")
        
        # Check PPR_PRU specifically
        if 'PPR_PRU' in result:
            pru_data = result['PPR_PRU']
            print(f"\n📊 PPR_PRU Analysis:")
            
            if isinstance(pru_data, dict):
                for key, value in pru_data.items():
                    if 'Receive_Dock' in key:
                        print(f"   {key}: {value}")
                        if isinstance(value, (int, float)):
                            if value > 1000 and value < 2000:
                                print(f"   ✅ FIXED: {value} is in expected range (~1700)")
                                return True
                            elif value < 1000:
                                print(f"   ❌ STILL BROKEN: {value} is below expected range")
                                return False
                            else:
                                print(f"   ⚠️  SUSPICIOUS: {value} is above expected range")
                                return False
        
        print("❌ PPR_PRU data not found")
        return False
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def verify_no_html_responses():
    """Test 2: Verify no HTML responses are being returned"""
    print("\n" + "=" * 80)
    print("VERIFICATION 2: NO HTML RESPONSES")
    print("=" * 80)
    
    site = "ZAZ1"
    end_time = datetime(2025, 6, 30, 8, 30, 0)  # 30 minutes
    start_time = datetime(2025, 6, 30, 8, 0, 0)
    
    print(f"Site: {site}")
    print(f"Time Range: {start_time.strftime('%Y-%m-%d %H:%M')} to {end_time.strftime('%H:%M')}")
    print("-" * 80)
    
    try:
        result = PPR_Q_function(Site=site, start_datetime=start_time, end_datetime=end_time)
        
        if not result:
            print("❌ No data returned")
            return False
        
        print(f"✅ Data returned: {len(result)} processes")
        
        # Check for HTML responses in the data
        html_detected = False
        for process_name, data in result.items():
            if process_name != '_metadata' and isinstance(data, dict):
                for key, value in data.items():
                    if isinstance(value, str) and ('<!DOCTYPE' in value or '<html' in value):
                        print(f"   ❌ HTML detected in {process_name}.{key}")
                        html_detected = True
        
        if not html_detected:
            print("   ✅ FIXED: No HTML responses detected")
            return True
        else:
            print("   ❌ STILL BROKEN: HTML responses found")
            return False
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def verify_url_parameters():
    """Test 3: Verify URLs include required parameters"""
    print("\n" + "=" * 80)
    print("VERIFICATION 3: URL PARAMETERS")
    print("=" * 80)
    
    from PPR_Q_processor import PPRQProcessor
    
    site = "ZAZ1"
    start_time = datetime(2025, 6, 30, 8, 0, 0)
    end_time = datetime(2025, 6, 30, 10, 0, 0)
    
    processor = PPRQProcessor(site, start_time, end_time)
    
    print(f"Site: {site}")
    print(f"Time Range: {start_time} to {end_time}")
    print("-" * 80)
    
    # Test URL generation for different processes
    test_processes = [
        ("PPR_PRU", ""),  # No process_id
        ("PPR_Receive_Dock", "1003010"),
        ("PPR_Transfer_Out", "1003021")
    ]
    
    all_urls_correct = True
    
    for process_key, process_id in test_processes:
        print(f"\n🔗 Testing URL for {process_key}:")
        time_range = processor.get_time_range()
        url = processor.build_url(process_key, process_id, time_range)
        print(f"   URL: {url}")
        
        # Check for required parameters
        required_params = ["_adjustPlanHours=on", "_hideEmptyLineItems=on"]
        for param in required_params:
            if param in url:
                print(f"   ✅ {param}")
            else:
                print(f"   ❌ {param} - MISSING!")
                all_urls_correct = False
        
        # Check for problematic parameters
        bad_params = ["intervalType=INTRADAY"]
        for param in bad_params:
            if param in url:
                print(f"   ❌ {param} - SHOULD NOT BE PRESENT!")
                all_urls_correct = False
    
    if all_urls_correct:
        print(f"\n✅ FIXED: All URLs include required parameters")
        return True
    else:
        print(f"\n❌ STILL BROKEN: Some URLs missing required parameters")
        return False

def verify_data_volume_reasonableness():
    """Test 4: Verify data volumes are reasonable for time ranges"""
    print("\n" + "=" * 80)
    print("VERIFICATION 4: DATA VOLUME REASONABLENESS")
    print("=" * 80)
    
    site = "ZAZ1"
    end_time = datetime(2025, 6, 30, 8, 30, 0)  # 30 minutes
    start_time = datetime(2025, 6, 30, 8, 0, 0)
    
    print(f"Site: {site}")
    print(f"Time Range: {start_time.strftime('%Y-%m-%d %H:%M')} to {end_time.strftime('%H:%M')}")
    print(f"Duration: {(end_time - start_time).total_seconds() / 3600:.2f} hours")
    print("-" * 80)
    
    try:
        result = PPR_Q_function(Site=site, start_datetime=start_time, end_datetime=end_time)
        
        if not result:
            print("❌ No data returned")
            return False
        
        print(f"✅ Data returned: {len(result)} processes")
        
        # Check for reasonable data volumes
        reasonable_data = True
        high_volume_issues = []
        
        for process_name, data in result.items():
            if process_name != '_metadata' and isinstance(data, dict):
                print(f"\n   📋 {process_name}:")
                for key, value in data.items():
                    if isinstance(value, (int, float)):
                        print(f"      {key}: {value}")
                        
                        # Check for suspiciously high values for 30 minutes
                        if value > 50000:
                            high_volume_issues.append(f"{process_name}.{key}: {value}")
                            reasonable_data = False
                        elif value > 10000:
                            print(f"      ⚠️  {key}: {value} - High but may be reasonable")
        
        if high_volume_issues:
            print(f"\n   ❌ STILL BROKEN: High volume issues detected:")
            for issue in high_volume_issues:
                print(f"      - {issue}")
            return False
        else:
            print(f"\n   ✅ FIXED: Data volumes look reasonable for 30-minute window")
            return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def verify_rate_calculations():
    """Test 5: Verify rate calculations are working"""
    print("\n" + "=" * 80)
    print("VERIFICATION 5: RATE CALCULATIONS")
    print("=" * 80)
    
    site = "ZAZ1"
    end_time = datetime(2025, 6, 30, 8, 30, 0)  # 30 minutes
    start_time = datetime(2025, 6, 30, 8, 0, 0)
    
    print(f"Site: {site}")
    print(f"Time Range: {start_time.strftime('%Y-%m-%d %H:%M')} to {end_time.strftime('%H:%M')}")
    print(f"Duration: {(end_time - start_time).total_seconds() / 3600:.2f} hours")
    print("-" * 80)
    
    try:
        result = PPR_Q_function(Site=site, start_datetime=start_time, end_datetime=end_time)
        
        if not result:
            print("❌ No data returned")
            return False
        
        print(f"✅ Data returned: {len(result)} processes")
        
        # Check for rate calculations
        print(f"\n📈 Rate Calculation Analysis:")
        zero_rates = []
        non_zero_rates = []
        
        for process_name, data in result.items():
            if process_name != '_metadata' and isinstance(data, dict):
                print(f"\n   📊 {process_name}:")
                for key, value in data.items():
                    if isinstance(value, (int, float)):
                        if value == 0:
                            zero_rates.append(f"{process_name}.{key}")
                            print(f"      ❌ {key}: {value} - ZERO RATE!")
                        else:
                            non_zero_rates.append(f"{process_name}.{key}: {value}")
                            print(f"      ✅ {key}: {value}")
        
        print(f"\n📊 Rate Summary:")
        print(f"   ✅ Non-zero rates: {len(non_zero_rates)}")
        print(f"   ❌ Zero rates: {len(zero_rates)}")
        
        if len(zero_rates) > len(non_zero_rates):
            print(f"   ❌ STILL BROKEN: Too many zero rates")
            return False
        else:
            print(f"   ✅ FIXED: Most rates are non-zero")
            return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def main():
    """Run verification tests"""
    print("PPR_Q VERIFICATION TESTS")
    print("=" * 80)
    print("Double-checking that all fixes are working correctly")
    print("=" * 80)
    
    start_time = time.time()
    
    # Run all verification tests
    test_results = {}
    
    # Test 1: Original Issue Fix
    test_results["Original Issue Fix"] = verify_original_issue_fix()
    
    # Test 2: No HTML Responses
    test_results["No HTML Responses"] = verify_no_html_responses()
    
    # Test 3: URL Parameters
    test_results["URL Parameters"] = verify_url_parameters()
    
    # Test 4: Data Volume Reasonableness
    test_results["Data Volume Reasonableness"] = verify_data_volume_reasonableness()
    
    # Test 5: Rate Calculations
    test_results["Rate Calculations"] = verify_rate_calculations()
    
    # Summary
    total_time = time.time() - start_time
    
    print("\n" + "=" * 80)
    print("VERIFICATION SUMMARY")
    print("=" * 80)
    
    print(f"⏱️  Total verification time: {total_time:.2f} seconds")
    print(f"\n📊 Verification Results:")
    
    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name}: {status}")
    
    # Overall assessment
    passed_tests = sum(1 for result in test_results.values() if result)
    total_tests = len(test_results)
    
    print(f"\n🎯 Overall Verification:")
    print(f"   Tests Passed: {passed_tests}/{total_tests}")
    
    if passed_tests == total_tests:
        print(f"   🎉 ALL VERIFICATIONS PASSED! Everything is fixed!")
    elif passed_tests >= total_tests * 0.8:
        print(f"   ✅ MOSTLY FIXED! Minor issues remain.")
    else:
        print(f"   ❌ SIGNIFICANT ISSUES REMAIN! More work needed.")
    
    # Critical check
    if test_results["Original Issue Fix"]:
        print(f"\n🏆 CRITICAL SUCCESS: Your original issue is completely fixed!")
        print(f"   PPR_PRU > PRU_Receive_Dock now returns correct values (~1700 u/h)")
    else:
        print(f"\n🚨 CRITICAL FAILURE: Your original issue is still broken!")

if __name__ == "__main__":
    main() 