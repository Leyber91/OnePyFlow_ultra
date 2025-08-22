#!/usr/bin/env python3
"""
PPR_Q Structure Test - Examine actual CSV structure from each module
to identify column index mismatches causing zero rate calculations.
"""

import sys
import os
import pandas as pd
import logging
from datetime import datetime, timedelta
from io import StringIO

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PPR_Q.PPR_Q_processor import PPRQProcessor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler()]
)

def analyze_csv_structure(csv_data: str, process_name: str) -> dict:
    """Analyze the structure of CSV data returned from API."""
    try:
        # Try to parse CSV
        df = pd.read_csv(StringIO(csv_data), delimiter=';', encoding='ISO-8859-1', on_bad_lines='skip')
        
        analysis = {
            'process_name': process_name,
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'column_names': list(df.columns),
            'sample_data': {}
        }
        
        # Get sample data from first few rows for key columns
        for i, col in enumerate(df.columns):
            analysis['sample_data'][f'Column_{i}'] = {
                'name': col,
                'sample_values': df[col].head(3).tolist() if not df.empty else []
            }
        
        # Look for rate-related columns
        rate_columns = []
        for i, col in enumerate(df.columns):
            col_lower = str(col).lower()
            if any(keyword in col_lower for keyword in ['rate', 'uph', 'per hour', 'productivity']):
                rate_columns.append({'index': i, 'name': col})
        
        analysis['potential_rate_columns'] = rate_columns
        
        return analysis
        
    except Exception as e:
        return {
            'process_name': process_name,
            'error': str(e),
            'raw_data_preview': csv_data[:500] if csv_data else 'No data'
        }

def test_individual_process_structure(site: str, process_name: str, process_id: str):
    """Test individual process to see raw CSV structure."""
    print(f"\n{'='*80}")
    print(f"TESTING PROCESS: {process_name}")
    print(f"Process ID: {process_id}")
    print(f"{'='*80}")
    
    # Create a short test time range (current time - 2 hours to current time)
    end_time = datetime.now()
    start_time = end_time - timedelta(hours=2)
    
    try:
        # Create processor instance
        processor = PPRQProcessor(site, start_time, end_time)
        
        # Build URL for this specific process
        time_range = processor.get_time_range()
        url = processor.build_url(process_name, process_id, time_range)
        
        print(f"🔗 URL: {url}")
        
        # Make direct API request to get raw CSV using the processor's method
        df = processor._make_request(process_name, url)
        
        if not df.empty:
            # Analyze the DataFrame structure
            analysis = {
                'process_name': process_name,
                'total_rows': len(df),
                'total_columns': len(df.columns),
                'column_names': list(df.columns)
            }
            
            print(f"📊 Response: SUCCESS - {len(df)} rows, {len(df.columns)} columns")
            
            print(f"\n📋 COLUMN MAPPING:")
            for i, col_name in enumerate(df.columns):
                print(f"   Column {i:2d}: {col_name}")
            
            # Show sample data for key columns (14, 15, 16 - expected rate columns)
            print(f"\n📊 SAMPLE DATA FOR KEY COLUMNS:")
            for col_idx in [14, 15, 16]:  # Volume, Hours, Rate columns
                if col_idx < len(df.columns):
                    col_name = df.columns[col_idx]
                    sample_values = df.iloc[:3, col_idx].tolist() if len(df) > 0 else []
                    print(f"   Column {col_idx:2d} ({col_name}): {sample_values}")
                else:
                    print(f"   Column {col_idx:2d}: NOT PRESENT (only {len(df.columns)} columns)")
            
            # Look for rate-related columns
            rate_columns = []
            for i, col in enumerate(df.columns):
                col_lower = str(col).lower()
                if any(keyword in col_lower for keyword in ['rate', 'uph', 'per hour', 'productivity']):
                    rate_columns.append({'index': i, 'name': col})
            
            if rate_columns:
                print(f"\n🎯 POTENTIAL RATE COLUMNS:")
                for rate_col in rate_columns:
                    sample_values = df.iloc[:3, rate_col['index']].tolist() if len(df) > 0 else []
                    print(f"   Column {rate_col['index']:2d}: {rate_col['name']} = {sample_values}")
            else:
                print(f"\n⚠️  NO OBVIOUS RATE COLUMNS FOUND")
        else:
            print(f"❌ No data returned from API")
        
        print(f"📊 Response Status: {response.status_code}")
        print(f"📊 Response Length: {len(response.text)} characters")
        
        if response.status_code == 200:
            # Analyze CSV structure
            analysis = analyze_csv_structure(response.text, process_name)
            
            print(f"\n📋 STRUCTURE ANALYSIS:")
            print(f"   Total Rows: {analysis.get('total_rows', 'Error')}")
            print(f"   Total Columns: {analysis.get('total_columns', 'Error')}")
            
            if 'column_names' in analysis:
                print(f"\n📋 COLUMN MAPPING:")
                for i, col_name in enumerate(analysis['column_names']):
                    print(f"   Column {i:2d}: {col_name}")
                
                # Show potential rate columns
                if analysis.get('potential_rate_columns'):
                    print(f"\n🎯 POTENTIAL RATE COLUMNS:")
                    for rate_col in analysis['potential_rate_columns']:
                        print(f"   Column {rate_col['index']:2d}: {rate_col['name']}")
                else:
                    print(f"\n⚠️  NO OBVIOUS RATE COLUMNS FOUND")
                
                # Show sample data for key columns (14, 15, 16 - expected rate columns)
                print(f"\n📊 SAMPLE DATA FOR KEY COLUMNS:")
                for col_idx in [14, 15, 16]:  # Volume, Hours, Rate columns
                    if col_idx < analysis['total_columns']:
                        col_info = analysis['sample_data'].get(f'Column_{col_idx}', {})
                        print(f"   Column {col_idx:2d} ({col_info.get('name', 'Unknown')}): {col_info.get('sample_values', [])}")
                    else:
                        print(f"   Column {col_idx:2d}: NOT PRESENT (only {analysis['total_columns']} columns)")
            
            if 'error' in analysis:
                print(f"\n❌ PARSING ERROR: {analysis['error']}")
                print(f"📄 Raw Data Preview:\n{analysis['raw_data_preview']}")
        
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"📄 Response Preview:\n{response.text[:500]}")
    
    except Exception as e:
        print(f"❌ Test Error: {str(e)}")

def main():
    """Test structure of key PPR_Q processes."""
    site = "BHX4"  # Use the same site as your JSON
    
    print(f"🔍 PPR_Q STRUCTURE ANALYSIS")
    print(f"Site: {site}")
    print(f"Testing CSV structure from API responses...")
    
    # Test key processes that should have rate calculations
    test_processes = [
        ("PPR_PRU", ""),  # No process ID - uses processPathRollup
        ("PPR_Prep_Recorder", "01003002"),
        ("PPR_Cubiscan", "1002971"),
        ("PPR_Each_Receive", "1003027"),
        ("PPR_Transfer_Out", "1003021"),
    ]
    
    for process_name, process_id in test_processes:
        test_individual_process_structure(site, process_name, process_id)
    
    print(f"\n{'='*80}")
    print(f"STRUCTURE ANALYSIS COMPLETE")
    print(f"{'='*80}")

if __name__ == "__main__":
    main()
