#!/usr/bin/env python3
"""
Quick runner script for YMS comparison analysis
Usage: python run_yms_analysis.py [SITE_CODE]
"""

import sys
from enhanced_yms_comparison import analyze_yms_differences, analyze_specific_mismatches

def main():
    """Run YMS comparison analysis for specified site"""
    
    # Default site if none provided
    site = sys.argv[1] if len(sys.argv) > 1 else "CDG7"
    
    print(f"🚀 STARTING YMS COMPARISON ANALYSIS FOR {site}")
    print("=" * 60)
    
    try:
        # Run comprehensive analysis
        print(f"📊 Running comprehensive analysis for {site}...")
        results = analyze_yms_differences(site, save_detailed_analysis=True)
        
        if results:
            print(f"\n🔍 Running specific mismatch analysis for {site}...")
            mismatches = analyze_specific_mismatches(site, max_mismatches=20)
            
            print(f"\n✅ ANALYSIS COMPLETE FOR {site}")
            print(f"📁 Detailed results saved to JSON file")
            print(f"📋 Summary available in YMS_COMPARISON_SUMMARY.md")
        else:
            print(f"❌ Analysis failed for {site}")
            
    except Exception as e:
        print(f"❌ Error running analysis for {site}: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 