"""
Ultra-Enhanced YMS API Transformation Module - REFACTORED
=========================================================
🎯 MAIN TRANSFORMATION LOGIC - Now modular and streamlined!

This module orchestrates the transformation process using specialized modules:
- yms_business_mapping: Business name mappings
- yms_field_extractors: Field extraction logic  
- yms_fmc_integration: FMC enhancement
- yms_quality_metrics: Quality validation
"""

import logging
import pandas as pd
from typing import Dict, List, Any, Tuple

# Import modular components
from .yms_business_mapping import extract_lane_with_business_mapping
from .yms_field_extractors import (
    extract_equipment_type, extract_carrier, extract_load_basic, 
    extract_vrid, convert_boolean_to_status, determine_availability,
    extract_load_traditional_style, extract_lane_traditional_style,
    extract_status_hybrid
)
from .yms_fmc_integration import apply_all_fmc_enhancements
from .yms_quality_metrics import (
    calculate_quality_metrics, validate_quality_improvements, 
    log_quality_summary, filter_unknown_reason_entries
)
from .yms_validation_framework import validate_yms_transformation

logger = logging.getLogger(__name__)


def ultra_yms_api_transform(api_records: List[Dict[str, Any]], fmc_df: pd.DataFrame, site: str) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    Ultra-enhanced YMS API transformation - now with validation framework!
    
    ✅ ENHANCED: Includes automated validation to prevent synthetic data generation
    
    Args:
        api_records: Raw records from YMS API
        fmc_df: FMC data for enrichment
        site: Site code
        
    Returns:
        Tuple of (final_json_dict, quality_metrics)
    """
    logger.info(f"Starting VALIDATED transformation for {len(api_records)} records")
    
    if not api_records:
        return _create_empty_result(), {'field_completeness': {}}
    
    # Step 1: Normalize API data using modular extractors
    normalized_records = _normalize_api_data_modular(api_records)
    logger.info(f"Normalized {len(normalized_records)} records using modular extractors")
    
    # Step 2: Convert to DataFrame for processing
    df = pd.DataFrame(normalized_records)
    original_count = len(df)
    
    # Step 3: Store pre-FMC state for validation
    pre_fmc_df = df.copy()
    
    # Step 4: Apply FMC enhancements using modular integration
    df, vrid_filled_count = apply_all_fmc_enhancements(df, fmc_df, site)
    
    # Step 5: ✅ VALIDATION CHECKPOINT - Validate transformation integrity
    validation_report = validate_yms_transformation(
        original_data=api_records,
        transformed_df=df,
        site=site,
        pre_fmc_df=pre_fmc_df
    )
    
    # Log validation results
    if validation_report['overall_passed']:
        logger.info(f"✅ VALIDATION PASSED for {site}")
    else:
        logger.warning(f"⚠️ VALIDATION ISSUES detected for {site}")
        for rec in validation_report['recommendations']:
            logger.warning(f"  - {rec}")
    
    # Step 6: Filter out UNKNOWN_REASON entries to match YMS Old behavior
    df, filtered_count = filter_unknown_reason_entries(df)
    
    # Step 7: Create final JSON structure
    final_json = _create_final_json_structure(df, site, fmc_df, vrid_filled_count)
    
    # Step 8: Calculate quality metrics using modular validation
    quality_metrics = calculate_quality_metrics(df, original_count)
    validation_results = validate_quality_improvements(quality_metrics)
    
    # Step 9: ✅ ENHANCED METRICS - Include validation results in quality metrics
    quality_metrics['validation_report'] = validation_report
    
    # Step 10: Log comprehensive quality summary
    log_quality_summary(quality_metrics, validation_results)
    
    logger.info(f"VALIDATED transformation complete. Records: {len(final_json.get('YMS_unfiltered', []))}")
    
    return final_json, quality_metrics


def _normalize_api_data_modular(raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Normalize API data using modular field extractors.
    
    Args:
        raw_data: Raw API records
        
    Returns:
        List of normalized records
    """
    logger.info(f"Normalizing {len(raw_data)} API records with modular extractors...")
    
    normalized = []
    for item in raw_data:
        # Use modular extractors for each field
        is_unavailable, unavailable_reason = determine_availability(item)
        
        normalized_item = {
            # Core fields using modular extractors
            "name": item.get("locationlabel", ""),
            "equipment_type": extract_equipment_type(item),
            "ownercode": extract_carrier(item),
            "vrid": extract_vrid(item),
            
            # Status conversion using original boolean-based logic
            "isempty": convert_boolean_to_status(
                item.get("isempty", True),
                item.get("tdrstate", "")
            ),
            
            # Availability using modular logic
            "unavailable": is_unavailable,
            "unavailableReason": unavailable_reason,
            
            # Enhanced fields using modular extractors
            "load": extract_load_traditional_style(item),
            "lane": extract_lane_traditional_style(item),
            "complete_lane": extract_lane_traditional_style(item),
            
            # Store raw data for potential future use
            "api_raw_data": item,
        }
        
        normalized.append(normalized_item)
    
    logger.info(f"Successfully normalized {len(normalized)} records")
    return normalized


def _create_final_json_structure(df: pd.DataFrame, site: str, fmc_df: pd.DataFrame, vrid_filled_count: int) -> Dict[str, Any]:
    """
    Create final JSON structure matching traditional YMS format.
    
    Args:
        df: Processed DataFrame
        site: Site code
        fmc_df: FMC DataFrame
        vrid_filled_count: Number of VRIDs filled from FMC
        
    Returns:
        Final JSON structure
    """
    records = df.to_dict('records')
    
    return {
        "YMS_unfiltered": records,
        "YMS_status": [r.get('isempty', '') for r in records],
        "YMS_name": [r.get('name', '') for r in records],
        "YMS_type": [r.get('equipment_type', '') for r in records],
        "YMS_SCAC": [r.get('ownercode', '') for r in records],
        "YMS_Unavailable": [r.get('unavailable', 0) for r in records],
        "YMS_UnavailableReason": ['NaN' if r.get('unavailableReason', 'NaN') == 'HEALTHY' else r.get('unavailableReason', 'NaN') for r in records],
        "YMS_Lane": [r.get('lane', 'NaN') for r in records],
        "YMS_Load": [r.get('load', 'NaN') for r in records],
        "YMS_VRID": [r.get('vrid', 'NaN') for r in records],
        "YMS_total_entries": len(records),
        "YMS_empty_VRID_count": sum(1 for r in records if r.get('vrid') in ['NaN', '', None]),
        "YMS_nonempty_VRID_count": sum(1 for r in records if r.get('vrid') not in ['NaN', '', None]),
        "FMC_total_entries": len(fmc_df) if not fmc_df.empty else 0,
        "FMC_nonempty_VRID_count": len(fmc_df[fmc_df['VR ID'].notna()]) if not fmc_df.empty and 'VR ID' in fmc_df.columns else 0,
        "YMS_VRID_count_unfiltered": sum(1 for r in records if r.get('vrid') not in ['NaN', '', None]),
        "YMS_VRID_count_filtered": sum(1 for r in records if r.get('vrid') not in ['NaN', '', None]),
        "YMS_VRID_filled_from_FMC": vrid_filled_count
    }


def _create_empty_result() -> Dict[str, Any]:
    """Return empty result structure when no data is available."""
    return {
        "YMS_unfiltered": [],
        "YMS_status": [],
        "YMS_name": [],
        "YMS_type": [],
        "YMS_SCAC": [],
        "YMS_Unavailable": [],
        "YMS_UnavailableReason": [],
        "YMS_Lane": [],
        "YMS_Load": [],
        "YMS_VRID": [],
        "YMS_total_entries": 0,
        "YMS_empty_VRID_count": 0,
        "YMS_nonempty_VRID_count": 0,
        "FMC_total_entries": 0,
        "FMC_nonempty_VRID_count": 0,
        "YMS_VRID_count_unfiltered": 0,
        "YMS_VRID_count_filtered": 0,
        "YMS_VRID_filled_from_FMC": 0
    }