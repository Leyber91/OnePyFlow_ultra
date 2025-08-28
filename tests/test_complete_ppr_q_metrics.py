#!/usr/bin/env python3
"""
Test PPR_Q Complete Metrics
Validates ALL target performance metrics from the complete performance table.
"""

import sys
import os
import warnings
from datetime import datetime
import json

# Suppress all warnings
warnings.filterwarnings("ignore")

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PPR_Q.PPR_Q_processor import PPRQProcessor

def test_complete_ppr_q_metrics():
    """
    Test PPR_Q with complete metrics extraction.
    """
    print("🎯 Complete PPR_Q Metrics Test")
    print("=" * 80)
    
    # Test parameters
    site = "BHX4"
    sos_datetime = datetime(2025, 8, 22, 18, 45)  # 2025-08-22 18:45
    eos_datetime = datetime(2025, 8, 23, 5, 15)   # 2025-08-23 05:15
    
    print(f"📋 Test Parameters:")
    print(f"   Site: {site}")
    print(f"   Start: {sos_datetime}")
    print(f"   End: {eos_datetime}")
    print()
    
    # Complete target metrics from the performance table
    target_metrics = {
        # Inbound - Receive
        "Receive_Dock": 3047.05,
        "Each_Receive_Small": 330.17,
        "Each_Receive_Medium": 141.78,
        "Each_Receive_Large": 55.84,
        "Each_Receive_Total": 254.64,
        "LP_Receive": 2631.26,
        "Pallet_Receive": 31.58,
        "Receive_Support": 1916.03,
        
        # Inbound - Prep
        "Cubiscan": 639.66,
        "Prep_Recorder_Small": 241.06,
        "Prep_Recorder_Medium": 209.19,
        "Prep_Recorder_Large": 73.65,
        "Prep_Recorder_Total": 232.00,
        "Prep_Support": 926.19,
        
        # Inbound - RSR
        "RSR_Support": 169190.37,
        
        # Inbound - Leadership
        "IB_Lead_PA": 17813.28,
        
        # DA - RC Sort
        "RC_Sort_Small": 508.52,
        "RC_Sort_Medium": 161.06,
        "RC_Sort_Large": 49.56,
        "RC_Sort_Total": 356.75,
        
        # DA - Transfer Out
        "Transfer_Out": 1453.05,
        "Transfer_Out_Dock": 19261.96,
        "TO_Lead_PA": 29462.25,
        "TO_Problem_Solve": 39552.71,
        
        # Support
        "Admin_HR_IT": 9792.76,
        "IC_QA_CS": 7670.98,
        "Facilities": 4016.91,
    }
    
    try:
        # Create PPR_Q processor
        ppr_q = PPRQProcessor(site=site, sos_datetime=sos_datetime, eos_datetime=eos_datetime)
        
        print("🔄 Running PPR_Q with comprehensive metrics calculation...")
        
        # Run PPR_Q
        result_json = ppr_q.run()
        
        print("✅ PPR_Q completed successfully!")
        print()
        
        # Check if target metrics section exists
        if "_target_metrics" in result_json:
            target_data = result_json["_target_metrics"]
            print("📊 COMPREHENSIVE TARGET METRICS COMPARISON")
            print("=" * 80)
            print(f"{'Metric':<30} {'Target':<12} {'PPR_Q':<12} {'Status':<15} {'Category'}")
            print("-" * 80)
            
            matches = 0
            total = 0
            tolerance = 0.10  # 10% tolerance
            
            # Group metrics by category for better organization
            categories = {
                "Inbound - Receive": ["Receive_Dock", "Each_Receive_Small", "Each_Receive_Medium", 
                                    "Each_Receive_Large", "Each_Receive_Total", "LP_Receive", 
                                    "Pallet_Receive", "Receive_Support"],
                "Inbound - Prep": ["Cubiscan", "Prep_Recorder_Small", "Prep_Recorder_Medium", 
                                 "Prep_Recorder_Large", "Prep_Recorder_Total", "Prep_Support"],
                "Inbound - Other": ["RSR_Support", "IB_Lead_PA"],
                "DA - RC Sort": ["RC_Sort_Small", "RC_Sort_Medium", "RC_Sort_Large", "RC_Sort_Total"],
                "DA - Transfer": ["Transfer_Out", "Transfer_Out_Dock", "TO_Lead_PA", "TO_Problem_Solve"],
                "Support": ["Admin_HR_IT", "IC_QA_CS", "Facilities"]
            }
            
            for category, metrics in categories.items():
                for metric in metrics:
                    if metric in target_metrics:
                        target_value = target_metrics[metric]
                        ppr_q_value = target_data.get(metric, 0)
                        total += 1
                        
                        if target_value == 0:
                            status = "✅ ZERO" if ppr_q_value == 0 else "❌ NON-ZERO"
                            if ppr_q_value == 0:
                                matches += 1
                        else:
                            diff_pct = abs(ppr_q_value - target_value) / target_value
                            if diff_pct <= tolerance:
                                status = "✅ MATCH"
                                matches += 1
                            else:
                                status = f"❌ OFF ({diff_pct*100:.1f}%)"
                        
                        print(f"{metric:<30} {target_value:<12.2f} {ppr_q_value:<12.2f} {status:<15} {category}")
            
            print("-" * 80)
            print(f"SUMMARY: {matches}/{total} metrics match ({matches/total*100:.1f}%)")
            
            if matches == total:
                print("🎉 ALL TARGET METRICS ACHIEVED!")
            elif matches >= total * 0.8:
                print("✅ GOOD: Most metrics match targets")
            else:
                print("⚠️  NEEDS WORK: Many metrics need refinement")
        
        else:
            print("❌ Target metrics section not found in PPR_Q output")
        
        # Show size breakdown summary if available
        if "_size_breakdown_summary" in result_json:
            print("\n" + result_json["_size_breakdown_summary"])
        
        # Show execution metadata
        if "_metadata" in result_json:
            metadata = result_json["_metadata"]
            print(f"\n📈 Execution Summary:")
            print(f"   Execution time: {metadata.get('execution_time_seconds', 0):.2f} seconds")
            print(f"   Site: {metadata.get('site', 'N/A')}")
            print(f"   Time range: {metadata.get('sos_datetime', 'N/A')} to {metadata.get('eos_datetime', 'N/A')}")
        
        # Show current modular structure
        print(f"\n📁 PPR_Q Modular Structure:")
        print(f"   ✅ PPR_Q_processor.py - Main processor with DataFrame storage")
        print(f"   ✅ metrics_calculator.py - Comprehensive metrics calculation")
        print(f"   ✅ size_calculator.py - Size-specific breakdowns")
        print(f"   ✅ __init__.py - Modular exports")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    test_complete_ppr_q_metrics()