#!/usr/bin/env python3
"""
Lane Differences Investigation
=============================
🎯 FOCUS: Investigate why YMS_API creates different lane values than YMS Traditional
- Check business name mapping logic
- Verify FMC data availability for specific locations
- Ensure no synthetic data fabrication
"""

import json
import sys

def investigate_lane_differences():
    """Investigate specific lane differences between YMS and YMS_API."""
    
    # Load the comparison report
    try:
        with open('yms_comparison_report_CDG7_20250704_023955.json', 'r') as f:
            report = json.load(f)
    except FileNotFoundError:
        print("❌ Comparison report not found")
        return

    print("="*80)
    print("LANE DIFFERENCES INVESTIGATION")
    print("="*80)
    
    # Extract data
    yms_data = report['yms_traditional']['data']['Main']
    api_data = report['yms_api']['data']['Main']
    
    # Create location dictionaries
    yms_locations = {}
    for i, name in enumerate(yms_data['YMS_name']):
        yms_locations[name] = {
            'status': yms_data['YMS_status'][i],
            'type': yms_data['YMS_type'][i],
            'scac': yms_data['YMS_SCAC'][i],
            'lane': yms_data['YMS_Lane'][i],
            'load': yms_data['YMS_Load'][i],
            'vrid': yms_data['YMS_VRID'][i]
        }
    
    api_locations = {}
    for i, name in enumerate(api_data['YMS_name']):
        api_locations[name] = {
            'status': api_data['YMS_status'][i],
            'type': api_data['YMS_type'][i],
            'scac': api_data['YMS_SCAC'][i],
            'lane': api_data['YMS_Lane'][i],
            'load': api_data['YMS_Load'][i],
            'vrid': api_data['YMS_VRID'][i]
        }
    
    # Focus on the specific problematic locations
    problem_locations = ['IB007', 'IB011', 'IB012']
    
    print(f"\n🔍 DETAILED ANALYSIS OF PROBLEMATIC LOCATIONS:")
    
    for location in problem_locations:
        if location in yms_locations and location in api_locations:
            yms_loc = yms_locations[location]
            api_loc = api_locations[location]
            
            print(f"\n📍 {location}:")
            print(f"  YMS Traditional:")
            print(f"    SCAC: '{yms_loc['scac']}'")
            print(f"    Lane: '{yms_loc['lane']}'")
            print(f"    Load: '{yms_loc['load']}'")
            print(f"    VRID: '{yms_loc['vrid']}'")
            
            print(f"  YMS_API:")
            print(f"    SCAC: '{api_loc['scac']}'")
            print(f"    Lane: '{api_loc['lane']}'")
            print(f"    Load: '{api_loc['load']}'")
            print(f"    VRID: '{api_loc['vrid']}'")
            
            # Analyze the difference
            yms_lane = str(yms_loc['lane']).strip()
            api_lane = str(api_loc['lane']).strip()
            
            if yms_lane != api_lane:
                print(f"  🚨 LANE DIFFERENCE:")
                print(f"    YMS: '{yms_lane}'")
                print(f"    API: '{api_lane}'")
                
                # Check if API lane looks like business name mapping
                if api_lane.endswith('_CDG7') and api_lane != yms_lane:
                    print(f"    ⚠️  API lane appears to be from business name mapping")
                    
                    # Extract business name from API lane
                    business_name = api_lane.replace('_CDG7', '')
                    print(f"    📝 Extracted business name: '{business_name}'")
                    
                    # Check SCAC mapping
                    yms_scac = str(yms_loc['scac']).strip()
                    api_scac = str(api_loc['scac']).strip()
                    print(f"    📦 SCAC comparison: YMS='{yms_scac}' vs API='{api_scac}'")
    
    print(f"\n🔍 LANE PATTERN ANALYSIS:")
    
    # Analyze all lane patterns
    yms_lane_patterns = {}
    api_lane_patterns = {}
    
    common_locations = set(yms_locations.keys()).intersection(set(api_locations.keys()))
    
    for location in common_locations:
        yms_lane = str(yms_locations[location]['lane']).strip()
        api_lane = str(api_locations[location]['lane']).strip()
        
        if yms_lane not in ['NaN', 'nan', '', 'None']:
            yms_lane_patterns[yms_lane] = yms_lane_patterns.get(yms_lane, 0) + 1
        
        if api_lane not in ['NaN', 'nan', '', 'None']:
            api_lane_patterns[api_lane] = api_lane_patterns.get(api_lane, 0) + 1
    
    print(f"\n📊 YMS Traditional Lane Patterns (top 10):")
    for lane, count in sorted(yms_lane_patterns.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {count:3d}x '{lane}'")
    
    print(f"\n📊 YMS_API Lane Patterns (top 10):")
    for lane, count in sorted(api_lane_patterns.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {count:3d}x '{lane}'")
    
    # Check for business name mapping pattern
    print(f"\n🧬 BUSINESS NAME MAPPING ANALYSIS:")
    
    api_business_names = set()
    for lane in api_lane_patterns.keys():
        if lane.endswith('_CDG7'):
            business_name = lane.replace('_CDG7', '')
            api_business_names.add(business_name)
    
    print(f"API business names found: {sorted(api_business_names)}")
    
    # Count differences
    lane_differences = 0
    exact_matches = 0
    
    for location in common_locations:
        yms_lane = str(yms_locations[location]['lane']).strip()
        api_lane = str(api_locations[location]['lane']).strip()
        
        if yms_lane == api_lane:
            exact_matches += 1
        else:
            lane_differences += 1
    
    print(f"\n📈 LANE COMPARISON SUMMARY:")
    print(f"  Total common locations: {len(common_locations)}")
    print(f"  Exact lane matches: {exact_matches}")
    print(f"  Lane differences: {lane_differences}")
    print(f"  Match rate: {(exact_matches/len(common_locations)*100):.1f}%")
    
    print(f"\n💡 INVESTIGATION CONCLUSIONS:")
    print(f"  🔍 YMS_API appears to be applying business name mapping")
    print(f"  ⚠️  This may be creating synthetic lane data")
    print(f"  📝 Recommendation: Preserve original lane if FMC mapping unavailable")
    
    return {
        'problem_locations': problem_locations,
        'yms_locations': yms_locations,
        'api_locations': api_locations,
        'lane_differences': lane_differences,
        'exact_matches': exact_matches
    }

def main():
    """Main investigation function."""
    print("🔍 Lane Differences Investigation")
    print("=" * 40)
    
    results = investigate_lane_differences()
    
    print(f"\n📋 NEXT STEPS:")
    print(f"  1. Check business name mapping logic in YMS_API")
    print(f"  2. Verify FMC data availability for problem locations")
    print(f"  3. Implement 'preserve original if no FMC data' logic")
    print(f"  4. Re-test with corrected lane extraction")

if __name__ == "__main__":
    main() 