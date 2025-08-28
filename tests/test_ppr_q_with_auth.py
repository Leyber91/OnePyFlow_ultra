#!/usr/bin/env python3
"""
Test PPR_Q with proper credential handling to ensure authentication works.
"""

import sys
import os
from datetime import datetime
import json
import requests
from http.cookiejar import MozillaCookieJar
from getpass import getuser

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PPR_Q.PPR_Q_processor import PPRQProcessor

def test_authentication():
    """
    Test authentication with FCLM portal first.
    """
    print("🔐 Testing Authentication with FCLM Portal")
    print("=" * 50)
    
    cookie_file_path = f'C:/Users/{getuser()}/.midway/cookie'
    
    # Check if cookie file exists
    if not os.path.exists(cookie_file_path):
        print(f"❌ Cookie file not found at: {cookie_file_path}")
        print("   Please log into Midway first and access FCLM portal")
        return False
    
    print(f"✅ Cookie file found at: {cookie_file_path}")
    
    # Load cookies
    cookie_jar = MozillaCookieJar(cookie_file_path)
    try:
        cookie_jar.load(ignore_discard=True, ignore_expires=True)
        print(f"✅ Loaded {len(cookie_jar)} cookies")
        
        # Check for session cookie
        session_cookies = [c for c in cookie_jar if 'session' in c.name.lower()]
        if session_cookies:
            print(f"✅ Found {len(session_cookies)} session cookies")
        else:
            print("⚠️  No session cookies found")
            
    except Exception as e:
        print(f"❌ Error loading cookies: {e}")
        return False
    
    # Test basic connectivity to FCLM portal with a specific report endpoint
    test_url = "https://fclm-portal.amazon.com/reports/processPathRollup"
    try:
        print(f"🌐 Testing connectivity to: {test_url}")
        response = requests.get(test_url, cookies=cookie_jar, verify=False, timeout=10)
        print(f"✅ Response status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Successfully connected to FCLM portal")
            return True
        elif response.status_code == 401:
            print("❌ Authentication failed - cookies may be expired")
            return False
        elif response.status_code == 404:
            print("✅ Authentication works (404 is expected for base endpoint)")
            return True
        else:
            print(f"⚠️  Unexpected status code: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False

def test_ppr_q_with_auth():
    """
    Test PPR_Q with proper authentication handling.
    """
    print("\n🎯 Testing PPR_Q with Authentication")
    print("=" * 50)
    
    # Parameters from the FCLM portal URL
    site = "BHX4"
    sos_datetime = datetime(2025, 8, 22, 18, 45)  # 2025-08-22 18:45
    eos_datetime = datetime(2025, 8, 23, 5, 15)   # 2025-08-23 05:15
    duration_hours = (eos_datetime - sos_datetime).total_seconds() / 3600
    
    print("📋 Test Parameters:")
    print(f"   Site: {site}")
    print(f"   Start: {sos_datetime}")
    print(f"   End: {eos_datetime}")
    print(f"   Duration: {duration_hours:.2f} hours")
    print()
    
    # Target metrics from the performance table
    target_metrics = {
        "Receive Dock": {"volume": 1373776, "hours": 450.85, "rate": 3047.05},
        "Each Receive - Small": {"volume": 93608, "hours": 283.52, "rate": 330.17},
        "Each Receive - Medium": {"volume": 24980, "hours": 176.19, "rate": 141.78},
        "Each Receive - Large": {"volume": 429, "hours": 7.68, "rate": 55.84},
        "Each Receive - Total": {"volume": 119017, "hours": 467.39, "rate": 254.64},
        "LP Receive": {"volume": 34479, "hours": 13.1, "rate": 2631.26},
        "Pallet Receive": {"volume": 258, "hours": 8.17, "rate": 31.58},
        "Receive Support": {"volume": 1373776, "hours": 716.99, "rate": 1916.03},
        "Cubiscan": {"volume": 2626, "hours": 4.11, "rate": 639.66},
        "Prep Recorder - Small": {"volume": 16451, "hours": 68.25, "rate": 241.06},
        "Prep Recorder - Medium": {"volume": 4858, "hours": 23.22, "rate": 209.19},
        "Prep Recorder - Total": {"volume": 21350, "hours": 92.03, "rate": 232.00},
        "RSR Support": {"volume": 2759777, "hours": 16.31, "rate": 169190.37}
    }
    
    # Process mapping to PPR_Q identifiers
    process_mapping = {
        "Receive Dock": "PPR_Receive_Dock",
        "Each Receive - Small": "PPR_Each_Receive",
        "Each Receive - Medium": "PPR_Each_Receive",
        "Each Receive - Large": "PPR_Each_Receive",
        "Each Receive - Total": "PPR_Each_Receive",
        "LP Receive": "PPR_LP_Receive",
        "Pallet Receive": "PPR_Pallet_Receive",
        "Receive Support": "PPR_Receive_Support",
        "Cubiscan": "PPR_Cubiscan",
        "Prep Recorder - Small": "PPR_Prep_Recorder",
        "Prep Recorder - Medium": "PPR_Prep_Recorder",
        "Prep Recorder - Total": "PPR_Prep_Recorder",
        "RSR Support": "PPR_RSR_Support"
    }
    
    print("🎯 Target Metrics from Performance Table:")
    print("-" * 50)
    for process, metrics in target_metrics.items():
        print(f"   {process}: {metrics['volume']:,} units, {metrics['hours']:.2f} hrs, {metrics['rate']:.2f} u/h")
    print()
    
    # Create PPR_Q processor
    ppr_q = PPRQProcessor(site=site, sos_datetime=sos_datetime, eos_datetime=eos_datetime)
    
    print("🔄 Running PPR_Q processing with authentication...")
    print("-" * 50)
    
    try:
        # Run the complete PPR_Q processing
        result_json = ppr_q.run()
        
        print("✅ PPR_Q processing completed successfully!")
        print()
        
        # Compare results with target metrics
        print("📊 Comparison: PPR_Q Results vs Target Metrics")
        print("=" * 70)
        print(f"{'Process':<25} {'Target Rate':<12} {'PPR_Q Rate':<12} {'Match':<8} {'Status'}")
        print("-" * 70)
        
        matches = 0
        total_comparisons = 0
        
        for process_name, target_data in target_metrics.items():
            ppr_q_key = process_mapping.get(process_name)
            target_rate = target_data["rate"]
            
            if ppr_q_key and ppr_q_key in result_json:
                ppr_q_data = result_json[ppr_q_key]
                
                # Find the rate in PPR_Q data
                ppr_q_rate = None
                rate_fields = [
                    f"{ppr_q_key}_Rate",
                    "Rate",
                    "UPH",
                    "JPH",
                    f"{process_name.replace(' ', '_')}_Rate"
                ]
                
                # Debug: Show all available fields
                print(f"   Available fields in {ppr_q_key}: {list(ppr_q_data.keys())}")
                
                for field in rate_fields:
                    if field in ppr_q_data:
                        ppr_q_rate = ppr_q_data[field]
                        print(f"   Found rate in field '{field}': {ppr_q_rate}")
                        break
                
                if ppr_q_rate is not None:
                    total_comparisons += 1
                    
                    # Check if rates are within 10% tolerance
                    tolerance = 0.10  # 10%
                    rate_diff = abs(ppr_q_rate - target_rate) / target_rate
                    
                    if rate_diff <= tolerance:
                        status = "✅ MATCH"
                        matches += 1
                    else:
                        status = "❌ DIFFERENT"
                    
                    print(f"{process_name:<25} {target_rate:<12.2f} {ppr_q_rate:<12.2f} {rate_diff*100:<8.1f}% {status}")
                else:
                    print(f"{process_name:<25} {target_rate:<12.2f} {'N/A':<12} {'N/A':<8} ❌ NO_RATE")
            else:
                print(f"{process_name:<25} {target_rate:<12.2f} {'N/A':<12} {'N/A':<8} ❌ NO_PROCESS")
        
        print("-" * 70)
        if total_comparisons > 0:
            print(f"Matches: {matches}/{total_comparisons} ({matches/total_comparisons*100:.1f}%)")
        else:
            print(f"Matches: {matches}/{total_comparisons} (0%)")
        
        if matches == total_comparisons and total_comparisons > 0:
            print("🎉 SUCCESS: PPR_Q produces the same metrics as target table!")
        elif matches > total_comparisons * 0.8:
            print("✅ GOOD: PPR_Q mostly matches target metrics")
        else:
            print("⚠️  NEEDS WORK: PPR_Q rates differ significantly from target")
        
        # Show execution metadata
        if "_metadata" in result_json:
            metadata = result_json["_metadata"]
            print(f"\n📈 Execution Summary:")
            print(f"   Execution time: {metadata.get('execution_time_seconds', 0):.2f} seconds")
            print(f"   Site: {metadata.get('site', 'N/A')}")
            print(f"   Time range: {metadata.get('sos_datetime', 'N/A')} to {metadata.get('eos_datetime', 'N/A')}")
        
    except Exception as e:
        print(f"❌ Error running PPR_Q: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 70)

def main():
    """
    Main test function with authentication check.
    """
    print("🧪 PPR_Q Authentication and Metrics Test")
    print("=" * 70)
    
    # First test authentication
    auth_success = test_authentication()
    
    if auth_success:
        # If authentication works, test PPR_Q
        test_ppr_q_with_auth()
    else:
        print("\n❌ Authentication failed. Please:")
        print("   1. Log into Midway")
        print("   2. Navigate to FCLM portal")
        print("   3. Verify you can access reports")
        print("   4. Run this test again")
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    main()
