"""
YMS Validation Framework
=======================
🎯 MISSION: Prevent synthetic data generation and ensure data integrity
⚠️  CREATED: To catch issues like ZAZ1/CDG7 inconsistencies before they cause problems

This framework validates:
- Synthetic data detection
- Site consistency validation
- Field completeness patterns
- FMC enhancement quality
- Transformation integrity
"""

import logging
import pandas as pd
from typing import Dict, List, Any, Tuple, Set, Optional
from collections import defaultdict
import re

logger = logging.getLogger(__name__)


class ValidationResult:
    """Container for validation results"""
    def __init__(self, passed: bool, message: str, details: Optional[Dict] = None):
        self.passed = passed
        self.message = message
        self.details = details or {}
        
    def __bool__(self):
        return self.passed


class YMSValidationFramework:
    """
    Comprehensive validation framework for YMS API transformations
    
    🎯 GOALS:
    - Prevent synthetic data generation
    - Ensure site consistency
    - Validate transformation integrity
    - Catch regressions early
    """
    
    def __init__(self):
        self.synthetic_patterns = self._init_synthetic_patterns()
        self.validation_results = []
        
    def _init_synthetic_patterns(self) -> Dict[str, List[str]]:
        """Initialize patterns that indicate synthetic data generation"""
        return {
            'synthetic_lanes': [
                r'^[A-Z]+_[A-Z0-9]+$',  # Pattern like VITAKRAF_ZAZ1
                r'^[A-Z]+_[A-Z]{3,4}[0-9]$',  # Pattern like BUSINESS_CDG7
                r'^[A-Z]+_[A-Z]{3,4}[0-9]_[A-Z0-9]+$'  # Extended synthetic patterns
            ],
            'over_standardized_loads': [
                r'^TransfersInitialPlacement$',  # Exact match for over-standardization
                r'^[A-Z]{3,}Transfer[a-zA-Z]*$',  # Generic transfer patterns
                r'^[A-Z]{3,}Warehouse[a-zA-Z]*$'  # Generic warehouse patterns
            ],
            'synthetic_vrids': [
                r'^[0-9]{10,15}$',  # Very long numeric VRIDs might be synthetic
                r'^[A-Z]{2,4}[0-9]{8,12}$',  # Code + long number patterns
                r'^SYN_[A-Z0-9]+$'  # Explicitly synthetic patterns
            ]
        }
    
    def validate_transformation_integrity(self, 
                                        original_data: List[Dict[str, Any]], 
                                        transformed_df: pd.DataFrame,
                                        site: str) -> ValidationResult:
        """
        Validate that the transformation preserved data integrity
        
        Args:
            original_data: Original API data
            transformed_df: Transformed DataFrame
            site: Site code
            
        Returns:
            ValidationResult indicating if transformation maintained integrity
        """
        issues = []
        
        # Check 1: Record count consistency
        if len(original_data) != len(transformed_df):
            issues.append(f"Record count mismatch: {len(original_data)} -> {len(transformed_df)}")
        
        # Check 2: No excessive synthetic data generation
        synthetic_count = self._count_synthetic_data(transformed_df)
        if synthetic_count['total'] > len(transformed_df) * 0.3:  # >30% synthetic is suspicious
            issues.append(f"Excessive synthetic data: {synthetic_count['total']}/{len(transformed_df)} records")
        
        # Check 3: Field completeness hasn't drastically changed
        completeness_issues = self._validate_field_completeness(original_data, transformed_df)
        issues.extend(completeness_issues)
        
        passed = len(issues) == 0
        message = f"Transformation integrity: {'PASSED' if passed else 'FAILED'}"
        
        return ValidationResult(
            passed=passed,
            message=message,
            details={'issues': issues, 'synthetic_count': synthetic_count}
        )
    
    def validate_site_consistency(self, 
                                site_results: Dict[str, pd.DataFrame]) -> ValidationResult:
        """
        Validate that different sites show consistent behavior patterns
        
        Args:
            site_results: Dictionary of site -> DataFrame
            
        Returns:
            ValidationResult indicating site consistency
        """
        if len(site_results) < 2:
            return ValidationResult(True, "Site consistency: SKIPPED (insufficient sites)")
        
        issues = []
        site_stats = {}
        
        # Calculate stats for each site
        for site, df in site_results.items():
            site_stats[site] = {
                'total_records': len(df),
                'lane_completeness': self._calculate_completeness(df, 'lane'),
                'load_completeness': self._calculate_completeness(df, 'load'),
                'vrid_completeness': self._calculate_completeness(df, 'vrid'),
                'synthetic_count': self._count_synthetic_data(df)
            }
        
        # Check for major inconsistencies
        sites = list(site_stats.keys())
        for i, site1 in enumerate(sites):
            for site2 in sites[i+1:]:
                stats1 = site_stats[site1]
                stats2 = site_stats[site2]
                
                # Check for opposite synthetic patterns (like ZAZ1 vs CDG7)
                if (stats1['synthetic_count']['total'] > stats1['total_records'] * 0.5 and
                    stats2['synthetic_count']['total'] < stats2['total_records'] * 0.1):
                    issues.append(f"Opposite synthetic patterns: {site1} has {stats1['synthetic_count']['total']} synthetic, {site2} has {stats2['synthetic_count']['total']}")
                
                # Check for major completeness differences
                for field in ['lane', 'load', 'vrid']:
                    diff = abs(stats1[f'{field}_completeness'] - stats2[f'{field}_completeness'])
                    if diff > 50:  # >50% difference is suspicious
                        issues.append(f"Major {field} completeness difference: {site1}={stats1[f'{field}_completeness']:.1f}%, {site2}={stats2[f'{field}_completeness']:.1f}%")
        
        passed = len(issues) == 0
        message = f"Site consistency: {'PASSED' if passed else 'FAILED'}"
        
        return ValidationResult(
            passed=passed,
            message=message,
            details={'issues': issues, 'site_stats': site_stats}
        )
    
    def validate_fmc_enhancement_quality(self, 
                                       pre_fmc_df: pd.DataFrame, 
                                       post_fmc_df: pd.DataFrame,
                                       site: str) -> ValidationResult:
        """
        Validate that FMC enhancement improved data quality without over-filling
        
        Args:
            pre_fmc_df: DataFrame before FMC enhancement
            post_fmc_df: DataFrame after FMC enhancement
            site: Site code
            
        Returns:
            ValidationResult indicating FMC enhancement quality
        """
        issues = []
        
        # Check 1: Enhancement didn't create synthetic patterns
        pre_synthetic = self._count_synthetic_data(pre_fmc_df)
        post_synthetic = self._count_synthetic_data(post_fmc_df)
        
        if post_synthetic['total'] > pre_synthetic['total'] * 2:  # 2x increase is suspicious
            issues.append(f"FMC enhancement created synthetic data: {pre_synthetic['total']} -> {post_synthetic['total']}")
        
        # Check 2: Reasonable enhancement rates
        enhancement_stats = self._calculate_enhancement_stats(pre_fmc_df, post_fmc_df)
        for field, stats in enhancement_stats.items():
            if stats['enhancement_rate'] > 0.8:  # >80% enhancement is suspicious
                issues.append(f"Over-enhancement in {field}: {stats['enhancement_rate']:.1%} of records enhanced")
        
        # Check 3: Enhanced data looks realistic
        realistic_issues = self._validate_realistic_enhancements(pre_fmc_df, post_fmc_df)
        issues.extend(realistic_issues)
        
        passed = len(issues) == 0
        message = f"FMC enhancement quality: {'PASSED' if passed else 'FAILED'}"
        
        return ValidationResult(
            passed=passed,
            message=message,
            details={'issues': issues, 'enhancement_stats': enhancement_stats}
        )
    
    def detect_synthetic_data_patterns(self, df: pd.DataFrame) -> ValidationResult:
        """
        Detect patterns that indicate synthetic data generation
        
        Args:
            df: DataFrame to analyze
            
        Returns:
            ValidationResult with synthetic pattern detection results
        """
        synthetic_count = self._count_synthetic_data(df)
        total_records = len(df)
        
        # Calculate synthetic percentage
        synthetic_pct = (synthetic_count['total'] / total_records * 100) if total_records > 0 else 0
        
        # Determine if synthetic levels are acceptable
        acceptable_threshold = 20  # 20% synthetic data is the warning threshold
        passed = synthetic_pct <= acceptable_threshold
        
        severity = "CRITICAL" if synthetic_pct > 50 else "WARNING" if synthetic_pct > acceptable_threshold else "OK"
        
        message = f"Synthetic data detection: {severity} - {synthetic_pct:.1f}% synthetic data"
        
        return ValidationResult(
            passed=passed,
            message=message,
            details={
                'synthetic_count': synthetic_count,
                'total_records': total_records,
                'synthetic_percentage': synthetic_pct,
                'threshold': acceptable_threshold
            }
        )
    
    def _count_synthetic_data(self, df: pd.DataFrame) -> Dict[str, int]:
        """Count synthetic data patterns in DataFrame"""
        synthetic_count = {'lanes': 0, 'loads': 0, 'vrids': 0, 'total': 0}
        
        for _, row in df.iterrows():
            # Check lanes
            lane = str(row.get('lane', ''))
            if lane and lane != 'NaN':
                for pattern in self.synthetic_patterns['synthetic_lanes']:
                    if re.match(pattern, lane):
                        synthetic_count['lanes'] += 1
                        break
            
            # Check loads
            load = str(row.get('load', ''))
            if load and load != 'NaN':
                for pattern in self.synthetic_patterns['over_standardized_loads']:
                    if re.match(pattern, load):
                        synthetic_count['loads'] += 1
                        break
            
            # Check VRIDs
            vrid = str(row.get('vrid', ''))
            if vrid and vrid != 'NaN':
                for pattern in self.synthetic_patterns['synthetic_vrids']:
                    if re.match(pattern, vrid):
                        synthetic_count['vrids'] += 1
                        break
        
        synthetic_count['total'] = synthetic_count['lanes'] + synthetic_count['loads'] + synthetic_count['vrids']
        return synthetic_count
    
    def _calculate_completeness(self, df: pd.DataFrame, field: str) -> float:
        """Calculate field completeness percentage"""
        if field not in df.columns:
            return 0.0
        
        total = len(df)
        if total == 0:
            return 0.0
        
        non_empty = df[field].notna() & (df[field] != 'NaN') & (df[field] != '')
        return (non_empty.sum() / total) * 100
    
    def _validate_field_completeness(self, original_data: List[Dict], transformed_df: pd.DataFrame) -> List[str]:
        """Validate that field completeness hasn't changed dramatically"""
        issues = []
        
        # This is a simplified check - in practice, you'd want to calculate
        # original completeness and compare with transformed completeness
        key_fields = ['lane', 'load', 'vrid']
        
        for field in key_fields:
            completeness = self._calculate_completeness(transformed_df, field)
            if completeness > 95:  # >95% completeness might indicate over-filling
                issues.append(f"Suspiciously high {field} completeness: {completeness:.1f}%")
        
        return issues
    
    def _calculate_enhancement_stats(self, pre_df: pd.DataFrame, post_df: pd.DataFrame) -> Dict[str, Dict]:
        """Calculate enhancement statistics"""
        stats = {}
        
        for field in ['lane', 'load', 'vrid']:
            if field in pre_df.columns and field in post_df.columns:
                pre_filled = (pre_df[field] != 'NaN').sum()
                post_filled = (post_df[field] != 'NaN').sum()
                enhanced = post_filled - pre_filled
                
                stats[field] = {
                    'pre_filled': pre_filled,
                    'post_filled': post_filled,
                    'enhanced': enhanced,
                    'enhancement_rate': enhanced / len(pre_df) if len(pre_df) > 0 else 0
                }
        
        return stats
    
    def _validate_realistic_enhancements(self, pre_df: pd.DataFrame, post_df: pd.DataFrame) -> List[str]:
        """Validate that enhancements look realistic"""
        issues = []
        
        # Check for mass standardization to generic values
        for field in ['load']:
            if field in post_df.columns:
                post_values = post_df[field].value_counts()
                if len(post_values) > 0:
                    most_common_pct = post_values.iloc[0] / len(post_df) * 100
                    if most_common_pct > 70:  # >70% same value is suspicious
                        most_common_value = post_values.index[0]
                        issues.append(f"Mass standardization in {field}: {most_common_pct:.1f}% have '{most_common_value}'")
        
        return issues
    
    def generate_validation_report(self, 
                                 original_data: List[Dict[str, Any]], 
                                 transformed_df: pd.DataFrame,
                                 site: str,
                                 pre_fmc_df: Optional[pd.DataFrame] = None) -> Dict[str, Any]:
        """
        Generate comprehensive validation report
        
        Args:
            original_data: Original API data
            transformed_df: Final transformed DataFrame
            site: Site code
            pre_fmc_df: Optional pre-FMC DataFrame
            
        Returns:
            Comprehensive validation report
        """
        logger.info(f"Generating validation report for {site}")
        
        # Run all validations
        integrity_result = self.validate_transformation_integrity(original_data, transformed_df, site)
        synthetic_result = self.detect_synthetic_data_patterns(transformed_df)
        
        fmc_result = None
        if pre_fmc_df is not None:
            fmc_result = self.validate_fmc_enhancement_quality(pre_fmc_df, transformed_df, site)
        
        # Compile results
        report = {
            'site': site,
            'timestamp': pd.Timestamp.now().isoformat(),
            'validation_results': {
                'transformation_integrity': {
                    'passed': integrity_result.passed,
                    'message': integrity_result.message,
                    'details': integrity_result.details
                },
                'synthetic_data_detection': {
                    'passed': synthetic_result.passed,
                    'message': synthetic_result.message,
                    'details': synthetic_result.details
                }
            },
            'overall_passed': integrity_result.passed and synthetic_result.passed,
            'recommendations': self._generate_recommendations(integrity_result, synthetic_result, fmc_result)
        }
        
        if fmc_result:
            report['validation_results']['fmc_enhancement_quality'] = {
                'passed': fmc_result.passed,
                'message': fmc_result.message,
                'details': fmc_result.details
            }
            report['overall_passed'] = report['overall_passed'] and fmc_result.passed
        
        # Log summary
        status = "PASSED" if report['overall_passed'] else "FAILED"
        logger.info(f"Validation report for {site}: {status}")
        
        return report
    
    def _generate_recommendations(self, 
                                integrity_result: ValidationResult, 
                                synthetic_result: ValidationResult,
                                fmc_result: Optional[ValidationResult]) -> List[str]:
        """Generate recommendations based on validation results"""
        recommendations = []
        
        if not integrity_result.passed:
            recommendations.append("Review transformation logic to ensure data integrity")
        
        if not synthetic_result.passed:
            recommendations.append("Investigate synthetic data generation patterns")
            recommendations.append("Consider making FMC enhancement more conservative")
        
        if fmc_result and not fmc_result.passed:
            recommendations.append("Review FMC enhancement logic for over-filling")
            recommendations.append("Validate FMC data quality and matching criteria")
        
        if not recommendations:
            recommendations.append("All validations passed - transformation looks good")
        
        return recommendations


# Convenience functions for easy integration
def validate_yms_transformation(original_data: List[Dict[str, Any]], 
                              transformed_df: pd.DataFrame,
                              site: str,
                              pre_fmc_df: Optional[pd.DataFrame] = None) -> Dict[str, Any]:
    """
    Convenience function to validate YMS transformation
    
    Args:
        original_data: Original API data
        transformed_df: Final transformed DataFrame
        site: Site code
        pre_fmc_df: Optional pre-FMC DataFrame
        
    Returns:
        Validation report
    """
    framework = YMSValidationFramework()
    return framework.generate_validation_report(original_data, transformed_df, site, pre_fmc_df)


def validate_site_consistency(site_results: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
    """
    Convenience function to validate site consistency
    
    Args:
        site_results: Dictionary of site -> DataFrame
        
    Returns:
        Site consistency validation results
    """
    framework = YMSValidationFramework()
    result = framework.validate_site_consistency(site_results)
    
    return {
        'passed': result.passed,
        'message': result.message,
        'details': result.details,
        'timestamp': pd.Timestamp.now().isoformat()
    } 