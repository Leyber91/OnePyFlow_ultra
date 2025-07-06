"""
YMS FMC Module - Simplified
===========================
🎯 MISSION: Load FMC data for YMS enhancement
"""

import logging
import pandas as pd
from typing import Tuple, List, Dict, Any

logger = logging.getLogger(__name__)


def load_fmc_data(site: str) -> Tuple[pd.DataFrame, dict]:
    """
    Load FMC data for a given site with enhanced logging and verification.
    
    Args:
        site (str): Site code to load FMC data for
        
    Returns:
        Tuple[pd.DataFrame, dict]: DataFrame containing FMC data and stats dictionary
    """
    stats = {
        "total_records": 0,
        "records_with_vrid": 0,
        "records_with_facility_seq": 0,
        "error": None
    }
    
    try:
        from FMC import FMCfunction
        logger.info(f"Loading FMC data for site {site}")
        
        fmc_json = FMCfunction(site)
        if isinstance(fmc_json, pd.DataFrame):
            df = fmc_json
        else:
            df = pd.DataFrame(fmc_json)
            
        if df.empty:
            logger.warning(f"No FMC data found for site {site}")
            return pd.DataFrame(), stats
            
        # Calculate statistics
        stats["total_records"] = len(df)
        stats["records_with_vrid"] = df["VR ID"].notna().sum() if "VR ID" in df.columns else 0
        stats["records_with_facility_seq"] = df["Facility Sequence"].notna().sum() if "Facility Sequence" in df.columns else 0
        
        # Log statistics
        logger.info(f"FMC data loaded for {site}:")
        logger.info(f"[OK] Total records: {stats['total_records']}")
        logger.info(f"[OK] Records with VRID: {stats['records_with_vrid']}")
        logger.info(f"[OK] Records with Facility Sequence: {stats['records_with_facility_seq']}")
        
        return df, stats
        
    except Exception as exc:
        error_msg = f"FMCfunction error for '{site}': {exc}"
        logger.error(error_msg, exc_info=True)
        stats["error"] = error_msg
        return pd.DataFrame(), stats


def create_truck_assignments_from_fmc(fmc_df: pd.DataFrame, site_code: str) -> Tuple[List[Dict], List[Dict]]:
    """
    Create truck assignments and truck list from FMC data in the format FlexSim expects.
    
    Args:
        fmc_df (pd.DataFrame): FMC data
        site_code (str): Site code for filtering
        
    Returns:
        Tuple[List[Dict], List[Dict]]: (truck_assignments, truck_list)
    """
    truck_assignments = []
    truck_list = []
    
    if fmc_df.empty:
        logger.warning("No FMC data available for truck assignments")
        return truck_assignments, truck_list
    
    logger.info(f"Creating truck assignments from FMC data for {site_code}")
    
    # Group FMC data by destination (arc lanes)
    arc_lane_assignments = {}
    
    for _, row in fmc_df.iterrows():
        facility_seq = row.get('Facility Sequence', '')
        if not facility_seq or pd.isna(facility_seq):
            continue
            
        # Parse facility sequence to extract destination
        # Format: "SITE_DESTINATION" -> extract DESTINATION
        if '_' in str(facility_seq) and str(facility_seq).startswith(site_code):
            destination = str(facility_seq).split('_', 1)[1]
            
            # Initialize arc lane if not exists
            if destination not in arc_lane_assignments:
                arc_lane_assignments[destination] = {
                    'destination': destination,
                    'carriers': {},
                    'trucks': [],
                    'total_trucks': 0
                }
            
            # Get carrier and truck info
            carrier = row.get('Carrier', 'UNKNOWN')
            vrid = row.get('VR ID', '')
            status = row.get('Status', '')
            equipment_type = row.get('Equipment Type', '')
            
            # Only count non-cancelled trucks
            if status != 'CANCELLED':
                # Count trucks by carrier
                if carrier not in arc_lane_assignments[destination]['carriers']:
                    arc_lane_assignments[destination]['carriers'][carrier] = 0
                arc_lane_assignments[destination]['carriers'][carrier] += 1
                arc_lane_assignments[destination]['total_trucks'] += 1
                
                # Create truck list entry
                truck_info = {
                    'ARC': destination,
                    'Carrier': carrier,
                    'Parking Slot': f"HS-T-{len(arc_lane_assignments[destination]['trucks']) + 1:03d}",
                    'Notes': f"VRID: {vrid}" if vrid else "Negotiate VRID",
                    'VRID': vrid,
                    'Status': status,
                    'Equipment Type': equipment_type,
                    'Facility Sequence': facility_seq
                }
                
                arc_lane_assignments[destination]['trucks'].append(truck_info)
                truck_list.append(truck_info)
    
    # Create truck assignments summary
    for destination, data in arc_lane_assignments.items():
        for carrier, truck_count in data['carriers'].items():
            truck_assignment = {
                'Destination': destination,
                'Carrier': carrier,
                '# Trucks': truck_count
            }
            truck_assignments.append(truck_assignment)
    
    logger.info(f"Created truck assignments for {site_code}:")
    logger.info(f"[OK] Arc lanes: {len(arc_lane_assignments)}")
    logger.info(f"[OK] Total truck assignments: {len(truck_assignments)}")
    logger.info(f"[OK] Total trucks in list: {len(truck_list)}")
    
    # Log arc lane summary
    for destination, data in list(arc_lane_assignments.items())[:5]:  # Show first 5
        logger.info(f"[OK] {destination}: {data['total_trucks']} trucks, {len(data['carriers'])} carriers")
    
    return truck_assignments, truck_list


def validate_fmc_data(fmc_df: pd.DataFrame) -> Dict[str, Any]:
    """
    Validate FMC data quality and completeness.
    
    Args:
        fmc_df: FMC DataFrame
        
    Returns:
        Dictionary with validation results
    """
    validation = {
        'is_valid': False,
        'total_records': 0,
        'required_columns_present': False,
        'vrid_coverage': 0.0,
        'facility_coverage': 0.0,
        'warnings': [],
        'errors': []
    }
    
    if fmc_df.empty:
        validation['errors'].append("FMC DataFrame is empty")
        return validation
    
    validation['total_records'] = len(fmc_df)
    
    # Check required columns
    required_columns = ['VR ID', 'Facility Sequence', 'Carrier']
    missing_columns = [col for col in required_columns if col not in fmc_df.columns]
    
    if missing_columns:
        validation['errors'].append(f"Missing required columns: {missing_columns}")
        return validation
    
    validation['required_columns_present'] = True
    
    # Calculate coverage metrics
    validation['vrid_coverage'] = (fmc_df['VR ID'].notna().sum() / len(fmc_df)) * 100
    validation['facility_coverage'] = (fmc_df['Facility Sequence'].notna().sum() / len(fmc_df)) * 100
    
    # Add warnings for low coverage
    if validation['vrid_coverage'] < 50:
        validation['warnings'].append(f"Low VRID coverage: {validation['vrid_coverage']:.1f}%")
    
    if validation['facility_coverage'] < 50:
        validation['warnings'].append(f"Low Facility Sequence coverage: {validation['facility_coverage']:.1f}%")
    
    # Mark as valid if basic requirements are met
    validation['is_valid'] = (
        validation['required_columns_present'] and
        validation['vrid_coverage'] > 0 and
        validation['facility_coverage'] > 0
    )
    
    return validation
