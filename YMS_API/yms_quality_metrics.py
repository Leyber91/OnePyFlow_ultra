"""
YMS Quality Metrics Module
==========================
🎯 MISSION: Calculate and validate YMS data quality metrics
"""

from typing import Dict, Any, List
import pandas as pd
import logging

logger = logging.getLogger(__name__)


def calculate_field_completeness(df: pd.DataFrame) -> Dict[str, Dict[str, float]]:
    """
    Calculate completeness percentage for each field.
    
    Args:
        df: DataFrame with YMS data
        
    Returns:
        Dictionary with field completeness metrics
    """
    total_records = len(df)
    if total_records == 0:
        return {}
    
    def calc_completeness(series, invalid_values=None):
        if invalid_values is None:
            invalid_values = ['NaN', '', None]
        valid = series[~series.isin(invalid_values)].count()
        return (valid / total_records * 100) if total_records > 0 else 0
    
    return {
        'YMS_SCAC': {
            'completeness_pct': calc_completeness(df['ownercode'], ['NaN', '', None])
        },
        'YMS_Load': {
            'completeness_pct': calc_completeness(df['load'], ['NaN', '', None])
        },
        'YMS_Lane': {
            'completeness_pct': calc_completeness(df['lane'], ['NaN', '', None])
        },
        'YMS_VRID': {
            'completeness_pct': calc_completeness(df['vrid'], ['NaN', '', None])
        },
        'YMS_type': {
            'completeness_pct': calc_completeness(df['equipment_type'], ['NaN', '', None])
        },
        'YMS_UnavailableReason': {
            'completeness_pct': calc_completeness(df['unavailableReason'], ['NaN', '', None, 'UNKNOWN_REASON'])
        }
    }


def calculate_transformation_stats(df: pd.DataFrame, original_count: int) -> Dict[str, Any]:
    """
    Calculate transformation statistics.
    
    Args:
        df: Final DataFrame
        original_count: Original record count
        
    Returns:
        Dictionary with transformation statistics
    """
    return {
        'total_records': len(df),
        'original_records': original_count,
        'empty_count': (df['isempty'] == 'EMPTY').sum(),
        'full_count': (df['isempty'] == 'FULL').sum(),
        'in_progress_count': (df['isempty'] == 'IN_PROGRESS').sum(),
        'unavailable_count': (df['unavailable'] == 1).sum()
    }


def get_gap_analysis_targets() -> Dict[str, float]:
    """
    Get target completeness percentages for gap analysis.
    
    Returns:
        Dictionary with target percentages
    """
    return {
        'vrid_gap_target': 63.2,  # Traditional YMS target
        'equipment_type_gap_target': 100.0,  # Traditional YMS target
        'scac_gap_target': 88.2,  # Traditional YMS target
        'unavailable_reason_gap_target': 66.4  # Traditional YMS target
    }


def calculate_quality_metrics(df: pd.DataFrame, original_count: int) -> Dict[str, Any]:
    """
    Calculate comprehensive quality metrics.
    
    Args:
        df: Final DataFrame
        original_count: Original record count
        
    Returns:
        Dictionary with comprehensive quality metrics
    """
    field_completeness = calculate_field_completeness(df)
    transformation_stats = calculate_transformation_stats(df, original_count)
    gap_targets = get_gap_analysis_targets()
    
    return {
        'field_completeness': field_completeness,
        'transformation_stats': transformation_stats,
        'gap_analysis': gap_targets
    }


def validate_quality_improvements(quality_metrics: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate that quality improvements meet targets.
    
    Args:
        quality_metrics: Quality metrics dictionary
        
    Returns:
        Dictionary with validation results
    """
    field_completeness = quality_metrics.get('field_completeness', {})
    gap_targets = quality_metrics.get('gap_analysis', {})
    
    # Check if we've closed the gaps
    improvements = {}
    
    field_target_mapping = [
        ('YMS_VRID', 'vrid_gap_target'),
        ('YMS_type', 'equipment_type_gap_target'), 
        ('YMS_SCAC', 'scac_gap_target'),
        ('YMS_UnavailableReason', 'unavailable_reason_gap_target')
    ]
    
    for field, target_key in field_target_mapping:
        current_pct = field_completeness.get(field, {}).get('completeness_pct', 0)
        target_pct = gap_targets.get(target_key, 0)
        
        improvement = current_pct - target_pct
        improvements[field] = {
            'current': current_pct,
            'target': target_pct,
            'improvement': improvement,
            'gap_closed': improvement >= -5  # Within 5% of target is acceptable
        }
        
        status = "GAP CLOSED" if improvement >= -5 else "NEEDS MORE WORK"
        logger.info(f"Quality Check - {field}: {current_pct:.1f}% (target: {target_pct:.1f}%) - {status}")
    
    # Overall assessment
    gaps_closed = sum(1 for imp in improvements.values() if imp['gap_closed'])
    total_gaps = len(improvements)
    
    return {
        'improvements': improvements,
        'gaps_closed': gaps_closed,
        'total_gaps': total_gaps,
        'success_rate': (gaps_closed / total_gaps * 100) if total_gaps > 0 else 0
    }


def log_quality_summary(quality_metrics: Dict[str, Any], validation_results: Dict[str, Any]) -> None:
    """
    Log a summary of quality metrics and validation results.
    
    Args:
        quality_metrics: Quality metrics dictionary
        validation_results: Validation results dictionary
    """
    logger.info("=" * 60)
    logger.info("QUALITY METRICS SUMMARY")
    logger.info("=" * 60)
    
    # Field completeness
    field_completeness = quality_metrics.get('field_completeness', {})
    for field, metrics in field_completeness.items():
        completeness = metrics.get('completeness_pct', 0)
        logger.info(f"{field}: {completeness:.1f}% completeness")
    
    # Transformation stats
    transform_stats = quality_metrics.get('transformation_stats', {})
    total_records = transform_stats.get('total_records', 0)
    unavailable_count = transform_stats.get('unavailable_count', 0)
    
    logger.info(f"Total Records: {total_records}")
    logger.info(f"Unavailable Equipment: {unavailable_count}")
    
    # Validation results
    gaps_closed = validation_results.get('gaps_closed', 0)
    total_gaps = validation_results.get('total_gaps', 0)
    success_rate = validation_results.get('success_rate', 0)
    
    logger.info(f"Quality Targets: {gaps_closed}/{total_gaps} gaps closed ({success_rate:.1f}%)")
    
    if gaps_closed == total_gaps:
        logger.info("🎉 ALL QUALITY TARGETS ACHIEVED!")
    elif gaps_closed >= total_gaps * 0.75:
        logger.info("✅ SIGNIFICANT QUALITY IMPROVEMENTS ACHIEVED!")
    else:
        logger.warning("⚠️ MORE QUALITY IMPROVEMENTS NEEDED")
    
    logger.info("=" * 60)


def filter_unknown_reason_entries(df: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    """
    Filter out entries with unavailableReason == 'UNKNOWN_REASON' to match YMS Old behavior.
    
    Args:
        df: DataFrame with YMS API data
        
    Returns:
        Tuple of (filtered_df, filtered_count)
    """
    original_count = len(df)
    
    # Filter out entries with UNKNOWN_REASON
    filtered_df = df[df['unavailableReason'] != 'UNKNOWN_REASON'].copy()
    
    filtered_count = original_count - len(filtered_df)
    
    if filtered_count > 0:
        logger.info(f"YMS Old Compatibility Filter: Removed {filtered_count} UNKNOWN_REASON entries")
        logger.info(f"Filtered from {original_count} to {len(filtered_df)} records (matching YMS Old)")
    else:
        logger.info("No UNKNOWN_REASON entries found - no filtering needed")
    
    return filtered_df, filtered_count 