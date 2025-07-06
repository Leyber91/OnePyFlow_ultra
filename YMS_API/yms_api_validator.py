"""
YMS API Validator - Modular Version
===================================
🎯 MISSION: Validate YMS output quality using modular components
"""

import logging
import pandas as pd
from typing import Dict, List, Any
import json
from datetime import datetime

from .yms_api_config import QUALITY_THRESHOLDS, get_quality_grade

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class YMSValidator:
    """Modular validator class to check YMS output quality"""
    
    def __init__(self, site: str):
        self.site = site
        self.validation_results = {
            'passed': [],
            'failed': [],
            'warnings': [],
            'metrics': {}
        }
    
    def validate_yms_output(self, yms_output: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate the complete YMS output for all known issues.
        
        Args:
            yms_output: The output from YMSfunction
            
        Returns:
            Validation results with pass/fail status
        """
        logger.info(f"Starting validation for site {self.site}")
        
        # Extract main data
        main_data = yms_output.get('Main', {})
        
        # Run validation checks using modular functions
        self._validate_lane_fields(main_data)
        self._validate_load_fields(main_data)
        self._validate_status_distribution(main_data)
        self._validate_availability_accuracy(main_data)
        self._validate_vrid_handling(main_data)
        self._validate_data_completeness(main_data)
        
        # Calculate overall score
        self._calculate_overall_score()
        
        return self.validation_results
    
    def _validate_lane_fields(self, data: Dict):
        """Check that lane fields don't contain site codes and have valid data."""
        logger.info("Validating lane fields...")
        
        lanes = data.get('YMS_Lane', [])
        if not lanes:
            self._add_failure("No lane data found")
            return
        
        # Count different value types
        site_code_count = sum(1 for lane in lanes if lane == f'{self.site}_{self.site}')
        business_name_count = sum(1 for lane in lanes if lane and '_' in lane and not lane.startswith(self.site))
        empty_count = sum(1 for lane in lanes if lane in ['', 'NaN'])
        valid_count = len(lanes) - site_code_count - empty_count
        
        # Calculate percentage
        valid_pct = (valid_count / len(lanes)) * 100 if lanes else 0
        
        # Validation logic
        if site_code_count > 0:
            self._add_failure(f"Found {site_code_count} lanes with site code pattern ({self.site}_{self.site})")
        
        quality_grade = get_quality_grade(valid_pct)
        if quality_grade == 'Poor':
            self._add_failure(f"Lane completeness is {valid_pct:.1f}% - {quality_grade}")
        elif quality_grade == 'Acceptable':
            self._add_warning(f"Lane completeness is {valid_pct:.1f}% - {quality_grade}")
        else:
            self._add_success(f"Lane data quality: {valid_pct:.1f}% - {quality_grade}")
        
        self.validation_results['metrics']['lane_completeness'] = valid_pct
        self.validation_results['metrics']['business_names_found'] = business_name_count
    
    def _validate_load_fields(self, data: Dict):
        """Check that load fields contain proper classifications."""
        logger.info("Validating load fields...")
        
        loads = data.get('YMS_Load', [])
        if not loads:
            self._add_failure("No load data found")
            return
        
        # Expected load types from config
        from .yms_api_config import STANDARD_LOAD_TYPES
        
        # Count different value types
        site_code_count = sum(1 for load in loads if load == self.site or load == f'{self.site}_{self.site}')
        standard_type_count = sum(1 for load in loads if load in STANDARD_LOAD_TYPES)
        empty_count = sum(1 for load in loads if load in ['', 'NaN'])
        
        # Calculate percentages
        standard_pct = (standard_type_count / len(loads)) * 100 if loads else 0
        
        # Validation logic
        if site_code_count > 0:
            self._add_failure(f"Found {site_code_count} loads with site code instead of proper type")
        
        if standard_pct < 20:
            self._add_failure(f"Only {standard_pct:.1f}% of loads have standard types (expected >20%)")
        else:
            self._add_success(f"Load classification working: {standard_pct:.1f}% standard types")
        
        self.validation_results['metrics']['load_classification'] = standard_pct
    
    def _validate_status_distribution(self, data: Dict):
        """Check for proper status distribution including IN_PROGRESS."""
        logger.info("Validating status distribution...")
        
        statuses = data.get('YMS_status', [])
        if not statuses:
            self._add_failure("No status data found")
            return
        
        # Count status types
        status_counts = pd.Series(statuses).value_counts().to_dict()
        total = len(statuses)
        
        # Calculate percentages
        in_progress_count = status_counts.get('IN_PROGRESS', 0)
        in_progress_pct = (in_progress_count / total) * 100 if total else 0
        
        # Validation logic
        if in_progress_count == 0:
            self._add_failure("No IN_PROGRESS status found (expected ~6%)")
        elif in_progress_pct < 2:
            self._add_warning(f"Low IN_PROGRESS count: {in_progress_pct:.1f}% (expected ~6%)")
        else:
            self._add_success(f"IN_PROGRESS detection working: {in_progress_pct:.1f}%")
        
        # Log distribution for debugging
        logger.info(f"Status distribution: {status_counts}")
        self.validation_results['metrics']['in_progress_pct'] = in_progress_pct
        self.validation_results['metrics']['status_distribution'] = status_counts
    
    def _validate_availability_accuracy(self, data: Dict):
        """Check availability field accuracy and consistency."""
        logger.info("Validating availability...")
        
        unavailable = data.get('YMS_Unavailable', [])
        reasons = data.get('YMS_UnavailableReason', [])
        
        if not unavailable:
            self._add_failure("No availability data found")
            return
        
        # Check consistency between unavailable flags and reasons
        unavail_count = sum(1 for u in unavailable if u == 1)
        valid_reasons_count = sum(1 for r in reasons if r and r != 'NaN' and r != 'UNKNOWN_REASON')
        
        # Validation logic
        if abs(unavail_count - valid_reasons_count) > 5:
            self._add_warning(f"Mismatch: {unavail_count} unavailable but {valid_reasons_count} have valid reasons")
        else:
            self._add_success(f"Availability data consistent: {unavail_count} unavailable items")
        
        unavail_pct = (unavail_count / len(unavailable)) * 100 if unavailable else 0
        self.validation_results['metrics']['unavailable_pct'] = unavail_pct
    
    def _validate_vrid_handling(self, data: Dict):
        """Check VRID handling and format validation."""
        logger.info("Validating VRID handling...")
        
        vrids = data.get('YMS_VRID', [])
        if not vrids:
            self._add_failure("No VRID data found")
            return
        
        # Count different VRID types
        site_code_count = sum(1 for vrid in vrids if str(vrid) == self.site)
        valid_format_count = sum(1 for vrid in vrids if self._is_valid_vrid_format(str(vrid)))
        empty_count = sum(1 for vrid in vrids if vrid in ['NaN', '0', '', None])
        
        # Validation logic
        if site_code_count > 0:
            self._add_failure(f"Found {site_code_count} VRIDs incorrectly using site code")
        
        valid_pct = (valid_format_count / len(vrids)) * 100 if vrids else 0
        quality_grade = get_quality_grade(valid_pct)
        
        self._add_success(f"VRID quality: {valid_pct:.1f}% valid format - {quality_grade}")
        self.validation_results['metrics']['vrid_completeness'] = valid_pct
    
    def _validate_data_completeness(self, data: Dict):
        """Overall data quality and completeness check."""
        logger.info("Checking overall data completeness...")
        
        # Check record counts
        total_entries = data.get('YMS_total_entries', 0)
        if total_entries == 0:
            self._add_failure("No records processed")
            return
        
        # Validate record processing
        self._add_success(f"Processed {total_entries} total records")
        
        # Check FMC enrichment availability
        fmc_records = data.get('FMC_total_entries', 0)
        vrid_filled = data.get('YMS_VRID_filled_from_FMC', 0)
        
        if fmc_records == 0:
            self._add_warning("No FMC data loaded for enrichment")
        else:
            self._add_success(f"FMC enrichment active: {fmc_records} records, {vrid_filled} VRIDs filled")
    
    def _calculate_overall_score(self):
        """Calculate weighted overall validation score."""
        metrics = self.validation_results['metrics']
        
        # Weight different metrics based on importance
        weights = {
            'lane_completeness': 0.25,
            'load_classification': 0.20,
            'in_progress_pct': 0.15,
            'unavailable_pct': 0.15,
            'vrid_completeness': 0.25
        }
        
        # Calculate weighted score
        score = 0
        total_weight = 0
        
        for metric, weight in weights.items():
            if metric in metrics:
                value = metrics[metric]
                
                # Special handling for percentage-based metrics
            if metric == 'in_progress_pct':
                    # Expect ~6%, normalize to 100 scale
                    normalized_value = min(value / 6 * 100, 100)
            elif metric == 'unavailable_pct':
                    # Expect ~9%, normalize to 100 scale
                    normalized_value = min(value / 9 * 100, 100)
            else:
                    normalized_value = value
                
                score += normalized_value * weight
                total_weight += weight
        
        # Normalize score
        final_score = score / total_weight if total_weight > 0 else 0
        
        self.validation_results['overall_score'] = final_score
        self.validation_results['grade'] = get_quality_grade(final_score)
    
    def _is_valid_vrid_format(self, vrid_str: str) -> bool:
        """Check if VRID has a valid format."""
        if not vrid_str or vrid_str in ['NaN', '0', '', 'None']:
            return False
        
        # Basic validation - longer than site code and contains numbers
        return len(vrid_str) > 5 and any(c.isdigit() for c in vrid_str)
    
    def _add_success(self, message: str):
        """Add success message."""
        self.validation_results['passed'].append(f"✓ {message}")
        logger.info(f"✓ {message}")
    
    def _add_failure(self, message: str):
        """Add failure message."""
        self.validation_results['failed'].append(f"✗ {message}")
        logger.error(f"✗ {message}")
    
    def _add_warning(self, message: str):
        """Add warning message."""
        self.validation_results['warnings'].append(f"⚠ {message}")
        logger.warning(f"⚠ {message}")


def generate_validation_report(validation_results: Dict, site: str) -> str:
    """Generate a formatted validation report."""
    report = f"""
YMS API Validation Report for {site}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{'='*60}

OVERALL GRADE: {validation_results.get('grade', 'N/A')}
OVERALL SCORE: {validation_results.get('overall_score', 0):.1f}/100

PASSED CHECKS ({len(validation_results['passed'])})
{'-'*30}
"""
    for check in validation_results['passed']:
        report += f"{check}\n"
    
    if validation_results['failed']:
    report += f"\nFAILED CHECKS ({len(validation_results['failed'])})\n{'-'*30}\n"
    for check in validation_results['failed']:
        report += f"{check}\n"
    
    if validation_results['warnings']:
    report += f"\nWARNINGS ({len(validation_results['warnings'])})\n{'-'*30}\n"
    for warning in validation_results['warnings']:
        report += f"{warning}\n"
    
    report += f"\nDETAILED METRICS\n{'-'*30}\n"
    for metric, value in validation_results['metrics'].items():
        if isinstance(value, (int, float)):
            report += f"{metric}: {value:.2f}\n"
        else:
            report += f"{metric}: {value}\n"
    
    return report


def validate_yms_fixes(site: str):
    """
    Main function to validate YMS fixes.
    
    Args:
        site: Site code to validate
    """
    try:
        logger.info(f"Starting YMS validation for site {site}")
        
        # Import and run the YMS function
        from .yms_ultra_main import YMSfunction
        
        # Get output from enhanced system
        logger.info("Running enhanced YMS function...")
        yms_output = YMSfunction(site)
        
        # Validate the output
        validator = YMSValidator(site)
        validation_results = validator.validate_yms_output(yms_output)
        
        # Generate and save report
        report = generate_validation_report(validation_results, site)
        print(report)
        
        # Save files
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        report_file = f'yms_validation_report_{site}_{timestamp}.txt'
        with open(report_file, 'w') as f:
            f.write(report)
        
        results_file = f'yms_validation_results_{site}_{timestamp}.json'
        with open(results_file, 'w') as f:
            json.dump({
                'site': site,
                'timestamp': datetime.now().isoformat(),
                'validation_results': validation_results,
                'sample_data': {
                    'lanes': yms_output['Main'].get('YMS_Lane', [])[:10],
                    'loads': yms_output['Main'].get('YMS_Load', [])[:10],
                    'statuses': yms_output['Main'].get('YMS_status', [])[:10]
                }
            }, f, indent=2)
        
        logger.info(f"Validation complete. Report: {report_file}, Results: {results_file}")
        
    except Exception as e:
        logger.error(f"Validation failed: {e}", exc_info=True)


if __name__ == "__main__":
    # Run validation for a test site
    validate_yms_fixes("CDG7")