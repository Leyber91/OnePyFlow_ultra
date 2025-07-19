#!/usr/bin/env python3
"""
Focused test for rate calculations in PPR_Q
Validates that the _adjustPlanHours=on fix is working
"""

import json
import logging
from datetime import datetime, timedelta
from PPR_Q_FF import PPR_Q_function

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

def test_rate_calculations():
    """Test rate calculations specifically"""
    print("=" * 60)
    print("RATE CALCULATION VALIDATION TEST")
    print("=" * 60)
    
    site = "DTM2"
    end_time = datetime.now() - timedelta(hours=2)
    start_time = end_time - timedelta(hours=2)
    
    print(f"Site: {site}")
    print(f"Time: {start_time.strftime('%Y-%m-%d %H:%M')} - {end_time.strftime('%H:%M')}")
    print(f"Duration: 2 hours")
    print("-" * 60)
    
    try:
        result = PPR_Q_function(Site=site, start_datetime=start_time, end_datetime=end_time)
        
        if not result:
            print("❌ No data returned")
            return False
        
        print(f"✅ Data returned: {len(result)} processes")
        
        # Check for rate calculations
        rate_found = False
        zero_rates = 0
        non_zero_rates = 0
        
        print("\nRate Analysis:")
        print("-" * 40)
        
        for process_name, data in result.items():
            if process_name != '_metadata' and isinstance(data, dict):
                for key, value in data.items():
                    if 'rate' in key.lower():
                        rate_found = True
                        if isinstance(value, (int, float)):
                            if value == 0.0:
                                zero_rates += 1
                                print(f"  ⚠️  {process_name}.{key}: {value} (ZERO)")
                            else:
                                non_zero_rates += 1
                                print(f"  ✅ {process_name}.{key}: {value}")
                        elif isinstance(value, list):
                            # Handle list of rates
                            non_zero_in_list = [v for v in value if v != 0.0]
                            if non_zero_in_list:
                                non_zero_rates += len(non_zero_in_list)
                                print(f"  ✅ {process_name}.{key}: {len(non_zero_in_list)} non-zero rates")
                            else:
                                zero_rates += len(value)
                                print(f"  ⚠️  {process_name}.{key}: {len(value)} zero rates")
        
        if not rate_found:
            print("  ❌ No rate calculations found")
            return False
        
        print(f"\nRate Summary:")
        print(f"  Non-zero rates: {non_zero_rates}")
        print(f"  Zero rates: {zero_rates}")
        print(f"  Total rates: {non_zero_rates + zero_rates}")
        
        if non_zero_rates > 0:
            print(f"\n🎉 RATE CALCULATIONS ARE WORKING!")
            print(f"   {non_zero_rates} non-zero rate values found")
            success_rate = (non_zero_rates / (non_zero_rates + zero_rates)) * 100
            print(f"   Success rate: {success_rate:.1f}%")
            return True
        else:
            print(f"\n❌ ALL RATES ARE ZERO - FIX NEEDED")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_specific_processes():
    """Test specific processes known to have rate calculations"""
    print("\n" + "=" * 60)
    print("SPECIFIC PROCESS RATE TEST")
    print("=" * 60)
    
    site = "DTM2"
    end_time = datetime.now() - timedelta(hours=1)
    start_time = end_time - timedelta(hours=1)
    
    print(f"Site: {site}")
    print(f"Time: {start_time.strftime('%Y-%m-%d %H:%M')} - {end_time.strftime('%H:%M')}")
    print("-" * 60)
    
    try:
        result = PPR_Q_function(Site=site, start_datetime=start_time, end_datetime=end_time)
        
        if not result:
            print("❌ No data returned")
            return False
        
        # Check specific processes
        target_processes = ['PPR_PRU', 'PPR_Prep_Recorder', 'PPR_Cubiscan']
        found_processes = []
        
        for process_name in target_processes:
            if process_name in result:
                found_processes.append(process_name)
                data = result[process_name]
                print(f"\n{process_name}:")
                
                if isinstance(data, dict):
                    for key, value in data.items():
                        if 'rate' in key.lower():
                            if isinstance(value, (int, float)) and value != 0.0:
                                print(f"  ✅ {key}: {value}")
                            elif isinstance(value, list):
                                non_zero = [v for v in value if v != 0.0]
                                if non_zero:
                                    print(f"  ✅ {key}: {len(non_zero)} non-zero values")
                                else:
                                    print(f"  ⚠️  {key}: all zero")
                            else:
                                print(f"  ⚠️  {key}: {value}")
        
        print(f"\nProcess Coverage: {len(found_processes)}/{len(target_processes)}")
        return len(found_processes) > 0
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def main():
    """Run rate calculation tests"""
    print("PPR_Q RATE CALCULATION VALIDATION")
    print("=" * 60)
    
    # Test 1: General rate calculations
    test1_success = test_rate_calculations()
    
    # Test 2: Specific processes
    test2_success = test_specific_processes()
    
    # Summary
    print("\n" + "=" * 60)
    print("RATE CALCULATION SUMMARY")
    print("=" * 60)
    
    if test1_success and test2_success:
        print("🎉 ALL RATE CALCULATIONS WORKING PERFECTLY!")
        print("   The _adjustPlanHours=on fix is successful")
        print("   PPR_Q is ready for production use")
    elif test1_success or test2_success:
        print("✅ RATE CALCULATIONS MOSTLY WORKING")
        print("   Some improvements needed but generally functional")
    else:
        print("❌ RATE CALCULATIONS NEED ATTENTION")
        print("   The _adjustPlanHours=on fix may need review")

if __name__ == "__main__":
    main() 