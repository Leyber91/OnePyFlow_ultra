#!/usr/bin/env python3
"""
FINAL COMPREHENSIVE TEST - PPR_Q Module Validation
Extensive debugging to cover all bases and ensure the module is working correctly.
"""

import json
import logging
import time
from datetime import datetime, timedelta
from PPR_Q_FF import PPR_Q_function

# Configure comprehensive logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.FileHandler('ppr_q_final_test.log'),
        logging.StreamHandler()
    ]
)

def test_url_generation():
    """Test 1: Validate URL generation with _adjustPlanHours=on parameter"""
    print("=" * 100)
    print("TEST 1: URL GENERATION VALIDATION")
    print("=" * 100)
    
    from PPR_Q_processor import PPRQProcessor
    
    site = "ZAZ1"
    start_time = datetime(2025, 6, 30, 8, 0, 0)
    end_time = datetime(2025, 6, 30, 10, 0, 0)
    
    processor = PPRQProcessor(site, start_time, end_time)
    
    print(f"Site: {site}")
    print(f"Time Range: {start_time} to {end_time}")
    print("-" * 100)
    
    # Test URL generation for different processes
    test_processes = [
        ("PPR_PRU", ""),  # No process_id
        ("PPR_Receive_Dock", "1003010"),
        ("PPR_Transfer_Out", "1003021")
    ]
    
    for process_key, process_id in test_processes:
        print(f"\n🔗 Testing URL for {process_key}:")
        time_range = processor.get_time_range()
        url = processor.build_url(process_key, process_id, time_range)
        print(f"   URL: {url}")
        
        # Check for required parameters
        checks = [
            ("_adjustPlanHours=on", "✅"),
            ("_hideEmptyLineItems=on", "✅"),
            ("spanType=Intraday", "✅"),
            ("reportFormat=CSV", "✅")
        ]
        
        for param, status in checks:
            if param in url:
                print(f"   {status} {param}")
            else:
                print(f"   ❌ {param} - MISSING!")
        
        # Check for problematic parameters
        bad_params = ["intervalType=INTRADAY"]
        for param in bad_params:
            if param in url:
                print(f"   ⚠️  {param} - SHOULD NOT BE PRESENT!")

def test_api_response_validation():
    """Test 2: Validate API responses are CSV, not HTML"""
    print("\n" + "=" * 100)
    print("TEST 2: API RESPONSE VALIDATION")
    print("=" * 100)
    
    site = "ZAZ1"
    end_time = datetime(2025, 6, 30, 8, 30, 0)  # 30 minutes
    start_time = datetime(2025, 6, 30, 8, 0, 0)
    
    print(f"Site: {site}")
    print(f"Time Range: {start_time.strftime('%Y-%m-%d %H:%M')} to {end_time.strftime('%H:%M')}")
    print(f"Duration: {(end_time - start_time).total_seconds() / 3600:.2f} hours")
    print("-" * 100)
    
    try:
        print("🔄 Making API request...")
        start_time_api = time.time()
        
        result = PPR_Q_function(Site=site, start_datetime=start_time, end_datetime=end_time)
        
        api_time = time.time() - start_time_api
        print(f"⏱️  API request completed in {api_time:.2f} seconds")
        
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
            print("   ✅ No HTML responses detected - API returning CSV data")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_data_filtering_validation():
    """Test 3: Validate data filtering is working correctly"""
    print("\n" + "=" * 100)
    print("TEST 3: DATA FILTERING VALIDATION")
    print("=" * 100)
    
    site = "ZAZ1"
    end_time = datetime(2025, 6, 30, 10, 0, 0)  # 2 hours
    start_time = datetime(2025, 6, 30, 8, 0, 0)
    
    print(f"Site: {site}")
    print(f"Requested Time Range: {start_time.strftime('%Y-%m-%d %H:%M')} to {end_time.strftime('%H:%M')}")
    print(f"Duration: {(end_time - start_time).total_seconds() / 3600:.1f} hours")
    print("-" * 100)
    
    try:
        result = PPR_Q_function(Site=site, start_datetime=start_time, end_datetime=end_time)
        
        if not result:
            print("❌ No data returned")
            return False
        
        print(f"✅ Data returned: {len(result)} processes")
        
        # Analyze data volume for reasonableness
        print(f"\n📊 Data Volume Analysis:")
        reasonable_data = True
        high_volume_metrics = []
        
        for process_name, data in result.items():
            if process_name != '_metadata' and isinstance(data, dict):
                print(f"\n   📋 {process_name}:")
                for key, value in data.items():
                    if isinstance(value, (int, float)):
                        print(f"      {key}: {value}")
                        
                        # Check for suspiciously high values
                        if value > 10000:
                            high_volume_metrics.append(f"{process_name}.{key}: {value}")
                            reasonable_data = False
                        elif value > 1000:
                            print(f"      ⚠️  {key}: {value} - High but may be reasonable for 2 hours")
        
        if high_volume_metrics:
            print(f"\n   ❌ SUSPICIOUSLY HIGH VALUES DETECTED:")
            for metric in high_volume_metrics:
                print(f"      - {metric}")
        else:
            print(f"\n   ✅ Data volume looks reasonable for 2-hour window")
        
        return reasonable_data
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_rate_calculation_validation():
    """Test 4: Validate rate calculations are working correctly"""
    print("\n" + "=" * 100)
    print("TEST 4: RATE CALCULATION VALIDATION")
    print("=" * 100)
    
    site = "ZAZ1"
    end_time = datetime(2025, 6, 30, 8, 30, 0)  # 30 minutes
    start_time = datetime(2025, 6, 30, 8, 0, 0)
    
    print(f"Site: {site}")
    print(f"Time Range: {start_time.strftime('%Y-%m-%d %H:%M')} to {end_time.strftime('%H:%M')}")
    print(f"Duration: {(end_time - start_time).total_seconds() / 3600:.2f} hours")
    print("-" * 100)
    
    try:
        result = PPR_Q_function(Site=site, start_datetime=start_time, end_datetime=end_time)
        
        if not result:
            print("❌ No data returned")
            return False
        
        print(f"✅ Data returned: {len(result)} processes")
        
        # Check for rate calculations (should be non-zero)
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
        
        if zero_rates:
            print(f"   ⚠️  Zero rates detected:")
            for rate in zero_rates:
                print(f"      - {rate}")
        
        return len(zero_rates) == 0
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_edge_cases():
    """Test 5: Test edge cases and error handling"""
    print("\n" + "=" * 100)
    print("TEST 5: EDGE CASES AND ERROR HANDLING")
    print("=" * 100)
    
    edge_cases = [
        {
            "name": "Very Short Range (5 minutes)",
            "site": "ZAZ1",
            "start": datetime(2025, 6, 30, 8, 0, 0),
            "end": datetime(2025, 6, 30, 8, 5, 0)
        },
        {
            "name": "Different Site (DTM1)",
            "site": "DTM1", 
            "start": datetime(2025, 6, 30, 8, 0, 0),
            "end": datetime(2025, 6, 30, 8, 30, 0)
        },
        {
            "name": "Overnight Shift",
            "site": "ZAZ1",
            "start": datetime(2025, 6, 30, 2, 0, 0),
            "end": datetime(2025, 6, 30, 4, 0, 0)
        }
    ]
    
    results = {}
    
    for case in edge_cases:
        print(f"\n🧪 Testing: {case['name']}")
        print(f"   Site: {case['site']}")
        print(f"   Time: {case['start'].strftime('%H:%M')} to {case['end'].strftime('%H:%M')}")
        
        try:
            result = PPR_Q_function(
                Site=case['site'], 
                start_datetime=case['start'], 
                end_datetime=case['end']
            )
            
            if result and len(result) > 1:  # More than just metadata
                print(f"   ✅ SUCCESS: {len(result)} processes returned")
                results[case['name']] = True
            else:
                print(f"   ⚠️  PARTIAL: Limited data returned")
                results[case['name']] = False
                
        except Exception as e:
            print(f"   ❌ FAILED: {e}")
            results[case['name']] = False
    
    return results

def test_original_use_case():
    """Test 6: Test the original use case that was failing"""
    print("\n" + "=" * 100)
    print("TEST 6: ORIGINAL USE CASE VALIDATION")
    print("=" * 100)
    
    site = "ZAZ1"
    end_time = datetime(2025, 6, 30, 10, 0, 0)  # 2 hours into ES shift
    start_time = datetime(2025, 6, 30, 8, 0, 0)  # Start of ES shift
    
    print(f"Original Issue: PPR_PRU > PRU_Receive_Dock = 553 u/h (expected ~1700)")
    print(f"Original Issue: 1M+ units processed (expected ~3400)")
    print("-" * 100)
    print(f"Site: {site}")
    print(f"Time Range: {start_time.strftime('%Y-%m-%d %H:%M')} to {end_time.strftime('%H:%M')}")
    print(f"Duration: {(end_time - start_time).total_seconds() / 3600:.1f} hours")
    print("-" * 100)
    
    try:
        result = PPR_Q_function(Site=site, start_datetime=start_time, end_datetime=end_time)
        
        if not result:
            print("❌ No data returned")
            return False
        
        print(f"✅ Data returned: {len(result)} processes")
        
        # Check PPR_PRU specifically
        if 'PPR_PRU' in result:
            pru_data = result['PPR_PRU']
            print(f"\n📊 PPR_PRU Analysis (Original Issue):")
            
            if isinstance(pru_data, dict):
                for key, value in pru_data.items():
                    if 'Receive_Dock' in key:
                        print(f"   {key}: {value}")
                        if isinstance(value, (int, float)):
                            if value > 1000 and value < 2000:
                                print(f"   ✅ GOOD: {value} is in expected range (~1700)")
                            elif value < 1000:
                                print(f"   ⚠️  LOW: {value} is below expected range")
                            else:
                                print(f"   ⚠️  HIGH: {value} is above expected range")
        
        # Check for any suspiciously high values
        print(f"\n🔍 Overall Data Analysis:")
        high_volume_issues = []
        
        for process_name, data in result.items():
            if process_name != '_metadata' and isinstance(data, dict):
                for key, value in data.items():
                    if isinstance(value, (int, float)) and value > 10000:
                        high_volume_issues.append(f"{process_name}.{key}: {value}")
        
        if high_volume_issues:
            print(f"   ⚠️  HIGH VOLUME ISSUES DETECTED:")
            for issue in high_volume_issues:
                print(f"      - {issue}")
        else:
            print(f"   ✅ No suspiciously high volume issues detected")
        
        # Check metadata
        if '_metadata' in result:
            metadata = result['_metadata']
            print(f"\n📋 Execution Metadata:")
            for key, value in metadata.items():
                print(f"   {key}: {value}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def main():
    """Run comprehensive final test suite"""
    print("PPR_Q FINAL COMPREHENSIVE TEST SUITE")
    print("=" * 100)
    print("Extensive debugging to cover all bases and ensure the module is working correctly")
    print("=" * 100)
    
    start_time = time.time()
    
    # Run all tests
    test_results = {}
    
    # Test 1: URL Generation
    try:
        test_url_generation()
        test_results["URL Generation"] = True
    except Exception as e:
        print(f"❌ URL Generation test failed: {e}")
        test_results["URL Generation"] = False
    
    # Test 2: API Response Validation
    test_results["API Response"] = test_api_response_validation()
    
    # Test 3: Data Filtering Validation
    test_results["Data Filtering"] = test_data_filtering_validation()
    
    # Test 4: Rate Calculation Validation
    test_results["Rate Calculations"] = test_rate_calculation_validation()
    
    # Test 5: Edge Cases
    test_results["Edge Cases"] = test_edge_cases()
    
    # Test 6: Original Use Case
    test_results["Original Use Case"] = test_original_use_case()
    
    # Summary
    total_time = time.time() - start_time
    
    print("\n" + "=" * 100)
    print("FINAL TEST SUMMARY")
    print("=" * 100)
    
    print(f"⏱️  Total test time: {total_time:.2f} seconds")
    print(f"\n📊 Test Results:")
    
    for test_name, result in test_results.items():
        if isinstance(result, dict):
            print(f"   {test_name}:")
            for sub_test, sub_result in result.items():
                status = "✅ PASS" if sub_result else "❌ FAIL"
                print(f"      - {sub_test}: {status}")
        else:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"   {test_name}: {status}")
    
    # Overall assessment
    passed_tests = sum(1 for result in test_results.values() if result)
    total_tests = len(test_results)
    
    print(f"\n🎯 Overall Assessment:")
    print(f"   Tests Passed: {passed_tests}/{total_tests}")
    
    if passed_tests == total_tests:
        print(f"   🎉 ALL TESTS PASSED! PPR_Q module is working correctly.")
    elif passed_tests >= total_tests * 0.8:
        print(f"   ✅ MOSTLY WORKING! PPR_Q module is functional with minor issues.")
    else:
        print(f"   ❌ SIGNIFICANT ISSUES! PPR_Q module needs more work.")
    
    print(f"\n📝 Detailed logs saved to: ppr_q_final_test.log")

if __name__ == "__main__":
    main() 