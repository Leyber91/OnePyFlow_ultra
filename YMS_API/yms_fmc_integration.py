"""
YMS FMC Integration Module
==========================
🎯 MISSION: Handle FMC data integration and enhancement logic
"""

from typing import Dict, Any, List, Optional, Tuple
import pandas as pd
import logging

logger = logging.getLogger(__name__)


def build_fmc_lookup_tables(fmc_df: pd.DataFrame, site: str) -> Dict[str, Any]:
    """
    Build comprehensive FMC lookup tables for faster matching.
    
    Args:
        fmc_df: FMC DataFrame
        site: Site code
        
    Returns:
        Dictionary with lookup tables
    """
    if fmc_df.empty:
        return {}
    
    lookups = {
        'vrid_direct': {},
        'location_exact': {},
        'location_pattern': {},
        'carrier_equipment': {},
        'fuzzy_location': []
    }
    
    for _, fmc_row in fmc_df.iterrows():
        fmc_dict = fmc_row.to_dict()
        vr_id = fmc_row.get('VR ID')
        
        if not vr_id:
            continue
        
        # Strategy 1: Direct VRID lookup
        lookups['vrid_direct'][str(vr_id)] = fmc_dict
        
        # Strategy 2: Location-based lookups
        facility_sequence = fmc_row.get('Facility Sequence', '')
        if facility_sequence:
            lookups['location_exact'][facility_sequence] = fmc_dict
            
            # Extract location patterns
            if '_' in facility_sequence:
                location_part = facility_sequence.split('_')[-1]
                lookups['location_pattern'][location_part] = fmc_dict
        
        # Strategy 3: Carrier + Equipment combination
        carrier = fmc_row.get('Carrier', '')
        equipment = fmc_row.get('Equipment Type', '')
        if carrier and equipment:
            key = f"{carrier}_{equipment}"
            lookups['carrier_equipment'][key] = fmc_dict
        
        # Strategy 4: Fuzzy matching data
        lookups['fuzzy_location'].append({
            'vrid': vr_id,
            'facility': facility_sequence,
            'carrier': carrier,
            'equipment': equipment,
            'record': fmc_dict
        })
    
    return lookups


def find_fmc_match(api_record: pd.Series, fmc_lookups: Dict[str, Any], site: str) -> Optional[Dict]:
    """
    Find FMC match for an API record using CONSERVATIVE strategies only.
    
    ⚠️  FIXED: Made more conservative to prevent over-filling of synthetic data
    
    Args:
        api_record: API record as pandas Series
        fmc_lookups: FMC lookup tables
        site: Site code
        
    Returns:
        Matching FMC record or None (only for high-confidence matches)
    """
    if not fmc_lookups:
        return None
    
    # Strategy 1: VRID direct match (HIGHEST PRIORITY - EXACT MATCH ONLY)
    vrid = api_record.get('vrid', '')
    if vrid and str(vrid).strip() and str(vrid) not in ['NaN', '', None]:
        vrid_str = str(vrid).strip()
        if vrid_str in fmc_lookups.get('vrid_direct', {}):
            return fmc_lookups['vrid_direct'][vrid_str]
    
    name = api_record.get('name', '')
    
    # Strategy 2: Location EXACT match only (no fuzzy matching)
    if name and name in fmc_lookups.get('location_exact', {}):
        return fmc_lookups['location_exact'][name]
    
    # 🚫 REMOVED: Fuzzy matching strategies that created synthetic data
    # The following strategies were creating false matches and are now removed:
    # - Location pattern matching (too broad)
    # - Carrier + Equipment matching (unreliable correlation)
    # - Fuzzy location similarity matching (created false confidence)
    # 
    # These were causing issues like:
    # - ZAZ1: Over-filling with TransfersInitialPlacement 
    # - CDG7: Missing real data due to poor correlation
    # 
    # ✅ NEW PRINCIPLE: Only exact matches to preserve data integrity
    
    return None


def calculate_location_similarity(api_location: str, fmc_location: str) -> float:
    """
    Calculate similarity between API location and FMC facility sequence.
    
    Args:
        api_location: API location string
        fmc_location: FMC facility sequence
        
    Returns:
        Similarity score between 0 and 1
    """
    if not api_location or not fmc_location:
        return 0.0
    
    # Simple similarity based on common substrings
    api_parts = set(api_location.replace('-', '_').split('_'))
    fmc_parts = set(fmc_location.replace('-', '_').split('_'))
    
    if not api_parts or not fmc_parts:
        return 0.0
    
    common = len(api_parts & fmc_parts)
    total = len(api_parts | fmc_parts)
    
    return common / total if total > 0 else 0.0


def enhance_vrid_with_fmc(df: pd.DataFrame, fmc_df: pd.DataFrame, site: str) -> Tuple[pd.DataFrame, int]:
    """
    Enhance VRID field using FMC data.
    
    Args:
        df: YMS DataFrame
        fmc_df: FMC DataFrame
        site: Site code
        
    Returns:
        Tuple of enhanced DataFrame and count of filled VRIDs
    """
    if fmc_df.empty or 'VR ID' not in fmc_df.columns:
        logger.warning("No FMC data available for VRID enhancement")
        return df, 0
    
    # Build lookup tables
    fmc_lookups = build_fmc_lookup_tables(fmc_df, site)
    
    filled_count = 0
    for idx in df.index:
        current_vrid = df.at[idx, 'vrid']
        
        # Skip if already has valid VRID
        if current_vrid and str(current_vrid).strip() and str(current_vrid) != 'NaN':
            continue
        
        # Find FMC match
        fmc_match = find_fmc_match(df.iloc[idx], fmc_lookups, site)
        
        if fmc_match:
            enhanced_vrid = fmc_match.get('VR ID', '')
            if enhanced_vrid:
                df.at[idx, 'vrid'] = str(enhanced_vrid)
                filled_count += 1
    
    logger.info(f"Enhanced FMC VRID enhancement: +{filled_count} VRIDs")
    return df, filled_count


def enhance_lane_with_fmc(df: pd.DataFrame, fmc_df: pd.DataFrame, site: str) -> pd.DataFrame:
    """
    Enhance lane field using FMC data - CONSERVATIVE approach.
    
    ⚠️  FIXED: More conservative to prevent synthetic lane creation
    
    Args:
        df: YMS DataFrame
        fmc_df: FMC DataFrame
        site: Site code
        
    Returns:
        Enhanced DataFrame
    """
    if fmc_df.empty:
        return df
    
    # Build lookup tables
    fmc_lookups = build_fmc_lookup_tables(fmc_df, site)
    
    enhanced_count = 0
    total_records = len(df)
    
    for idx in df.index:
        current_lane = df.at[idx, 'lane']
        
        # Skip if already has lane (from API extraction)
        if current_lane and str(current_lane).strip() and str(current_lane) not in ['', 'NaN']:
            continue
        
        # Find FMC match using CONSERVATIVE matching only
        fmc_match = find_fmc_match(df.iloc[idx], fmc_lookups, site)
        
        if fmc_match:
            facility_sequence = fmc_match.get('Facility Sequence', '')
            # ✅ ENHANCED VALIDATION: Only use facility sequence if it looks real
            if (facility_sequence and 
                facility_sequence.strip() and
                facility_sequence not in ['', 'NaN', 'NULL', 'UNKNOWN'] and
                len(facility_sequence.strip()) > 2):  # Minimum length check
                
                df.at[idx, 'lane'] = facility_sequence
                df.at[idx, 'complete_lane'] = facility_sequence
                enhanced_count += 1
    
    success_rate = (enhanced_count / total_records) * 100 if total_records > 0 else 0
    logger.info(f"CONSERVATIVE lane enhancement: {enhanced_count}/{total_records} ({success_rate:.1f}%)")
    
    return df


def enhance_load_with_fmc(df: pd.DataFrame, fmc_df: pd.DataFrame, site: str) -> pd.DataFrame:
    """
    Enhance load field using FMC data - CONSERVATIVE approach.
    
    ⚠️  FIXED: More conservative to prevent load type over-standardization
    
    Args:
        df: YMS DataFrame
        fmc_df: FMC DataFrame
        site: Site code
        
    Returns:
        Enhanced DataFrame
    """
    if fmc_df.empty:
        return df
    
    # Build lookup tables
    fmc_lookups = build_fmc_lookup_tables(fmc_df, site)
    
    enhanced_count = 0
    total_records = len(df)
    
    for idx in df.index:
        current_load = df.at[idx, 'load']
        
        # Skip if already has load (from API extraction)
        if current_load and str(current_load).strip() and str(current_load) not in ['', 'NaN']:
            continue
        
        # Find FMC match using CONSERVATIVE matching only
        fmc_match = find_fmc_match(df.iloc[idx], fmc_lookups, site)
        
        if fmc_match:
            shipper_accounts = fmc_match.get('Shipper Accounts', '')
            # ✅ ENHANCED VALIDATION: Only use shipper accounts if they look real
            if (shipper_accounts and 
                shipper_accounts.strip() and
                shipper_accounts not in ['', 'NaN', 'NULL', 'UNKNOWN', 'TransfersInitialPlacement'] and
                len(shipper_accounts.strip()) > 3):  # Minimum length check
                
                # 🚫 BLOCK OVER-STANDARDIZATION: Don't fill with generic load types
                # Prevent mass-filling with TransfersInitialPlacement unless it's specific
                if shipper_accounts == 'TransfersInitialPlacement':
                    # Only allow if we have very high confidence (exact VRID match)
                    vrid = df.at[idx, 'vrid']
                    if not (vrid and str(vrid).strip() and str(vrid) != 'NaN'):
                        continue  # Skip generic load type without exact VRID match
                
                df.at[idx, 'load'] = shipper_accounts
                enhanced_count += 1
    
    success_rate = (enhanced_count / total_records) * 100 if total_records > 0 else 0
    logger.info(f"CONSERVATIVE load enhancement: {enhanced_count}/{total_records} ({success_rate:.1f}%)")
    
    return df


def enhance_scac_with_fmc(df: pd.DataFrame, fmc_df: pd.DataFrame, site: str) -> pd.DataFrame:
    """
    Enhance SCAC field using FMC Subcarrier data.
    
    Args:
        df: YMS DataFrame
        fmc_df: FMC DataFrame
        site: Site code
        
    Returns:
        Enhanced DataFrame
    """
    if fmc_df.empty:
        return df
    
    # Build lookup tables
    fmc_lookups = build_fmc_lookup_tables(fmc_df, site)
    
    enhanced_count = 0
    total_records = len(df)
    
    for idx in df.index:
        current_scac = df.at[idx, 'ownercode']
        
        # Skip if already has valid SCAC (only enhance empty or generic ones)
        skip_enhancement = (current_scac and 
                          str(current_scac).strip() and 
                          str(current_scac) != 'NaN' and
                          # Allow enhancement of generic European/UK codes
                          current_scac not in ['ATSES', 'ATSIT', 'ATSEX', 'DPDUK'])
        
        if skip_enhancement:
            continue
        
        # Find FMC match
        fmc_match = find_fmc_match(df.iloc[idx], fmc_lookups, site)
        
        if fmc_match:
            subcarrier = fmc_match.get('Subcarrier', '')
            if subcarrier and subcarrier.strip() and subcarrier not in ['', '_____']:
                # Use FMC Subcarrier as SCAC enhancement
                df.at[idx, 'ownercode'] = subcarrier.strip()
                enhanced_count += 1
    
    success_rate = (enhanced_count / total_records) * 100 if total_records > 0 else 0
    logger.info(f"Enhanced SCAC enhancement: {enhanced_count}/{total_records} ({success_rate:.1f}%)")
    
    return df


def apply_all_fmc_enhancements(df: pd.DataFrame, fmc_df: pd.DataFrame, site: str) -> Tuple[pd.DataFrame, int]:
    """
    Apply all FMC enhancements to the DataFrame.
    
    Args:
        df: YMS DataFrame
        fmc_df: FMC DataFrame
        site: Site code
        
    Returns:
        Tuple of enhanced DataFrame and VRID fill count
    """
    if fmc_df.empty:
        logger.info("No FMC data available for enhancement")
        return df, 0
    
    logger.info(f"Applying FMC enhancements for {site} with {len(fmc_df)} FMC records")
    
    # Apply enhancements in order of priority
    df, vrid_filled_count = enhance_vrid_with_fmc(df, fmc_df, site)
    df = enhance_lane_with_fmc(df, fmc_df, site)
    df = enhance_load_with_fmc(df, fmc_df, site)
    df = enhance_scac_with_fmc(df, fmc_df, site)
    
    logger.info(f"FMC enhancements completed for {site}")
    return df, vrid_filled_count 