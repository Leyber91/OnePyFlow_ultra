#!/usr/bin/env python3
"""
YMS Mapping Analyzer
====================

This script analyzes the key differences between Traditional YMS and YMS_API:

1. Field Mapping Analysis - How each field is extracted and mapped
2. Raw Data Structure Comparison - What data is available in each approach
3. Data Quality Metrics - Completeness and accuracy comparison
4. Transformation Logic Review - Understanding the mapping pipeline

Key Focus Areas:
- VRID extraction and mapping
- Equipment Type preservation
- SCAC/Carrier mapping
- Lane extraction and transformation
- Load/Shipper Accounts mapping
- FMC integration differences
"""

import json
import logging
import pandas as pd
from typing import Dict, List, Any, Optional
from datetime import datetime
import os

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class YMSMappingAnalyzer:
    """
    Analyzes and compares field mappings between Traditional YMS and YMS_API.
    """
    
    def __init__(self):
        self.key_fields = [
            'YMS_status', 'YMS_name', 'YMS_type', 'YMS_SCAC', 
            'YMS_Unavailable', 'YMS_UnavailableReason', 'YMS_Lane', 
            'YMS_Load', 'YMS_VRID'
        ]
        
        self.raw_field_mappings = {
            # Traditional YMS raw field -> API raw field mappings
            'vrid': ['vrid', 'isaid', 'visitreasonid'],
            'equipment_type': ['equipment_type', 'type', 'vehicletype'],
            'ownercode': ['ownercode', 'carrier', 'carriercode', 'scac'],
            'lane': ['lane', 'complete_lane', 'dockdoor'],
            'load': ['load', 'shipperaccounts', 'shipperAccounts'],
            'isempty': ['isempty', 'status', 'containerstatus'],
            'unavailable': ['unavailable', 'available', 'blocked'],
            'unavailableReason': ['unavailableReason', 'blockedReason', 'unavailReason']
        }
    
    def analyze_field_mapping_differences(self, site: str, trad_file: str, api_file: str) -> Dict[str, Any]:
        """
        Analyze field mapping differences between traditional and API data.
        """
        logger.info(f"Analyzing field mapping differences for {site}")
        
        # Load data files
        try:
            with open(trad_file, 'r') as f:
                trad_data = json.load(f)
            with open(api_file, 'r') as f:
                api_data = json.load(f)
        except FileNotFoundError as e:
            logger.error(f"Data file not found: {e}")
            return {"error": f"Data file not found: {e}"}
        
        analysis = {
            'site': site,
            'timestamp': datetime.now().isoformat(),
            'record_counts': self._compare_record_counts(trad_data, api_data),
            'field_completeness': self._analyze_field_completeness(trad_data, api_data),
            'raw_data_structure': self._analyze_raw_data_structure(trad_data, api_data),
            'mapping_quality': self._analyze_mapping_quality(trad_data, api_data),
            'vrid_analysis': self._analyze_vrid_mapping(trad_data, api_data),
            'fmc_integration': self._analyze_fmc_integration(trad_data, api_data),
            'recommendations': []
        }
        
        # Generate recommendations
        analysis['recommendations'] = self._generate_recommendations(analysis)
        
        return analysis
    
    def _compare_record_counts(self, trad_data: Dict, api_data: Dict) -> Dict[str, Any]:
        """Compare record counts between traditional and API data."""
        trad_main = trad_data.get("Main", {})
        api_main = api_data.get("Main", {})
        
        trad_unfiltered = trad_main.get("YMS_unfiltered", [])
        api_unfiltered = api_main.get("YMS_unfiltered", [])
        
        return {
            'traditional_count': len(trad_unfiltered),
            'api_count': len(api_unfiltered),
            'difference': len(api_unfiltered) - len(trad_unfiltered),
            'traditional_totals': {
                'YMS_total_entries': trad_main.get('YMS_total_entries', 0),
                'FMC_total_entries': trad_main.get('FMC_total_entries', 0)
            },
            'api_totals': {
                'YMS_total_entries': api_main.get('YMS_total_entries', 0),
                'FMC_total_entries': api_main.get('FMC_total_entries', 0)
            }
        }
    
    def _analyze_field_completeness(self, trad_data: Dict, api_data: Dict) -> Dict[str, Any]:
        """Analyze field completeness comparison."""
        trad_main = trad_data.get("Main", {})
        api_main = api_data.get("Main", {})
        
        completeness = {}
        
        for field in self.key_fields:
            trad_field = trad_main.get(field, [])
            api_field = api_main.get(field, [])
            
            trad_completeness = self._calculate_completeness(trad_field)
            api_completeness = self._calculate_completeness(api_field)
            
            completeness[field] = {
                'traditional': {
                    'total': len(trad_field),
                    'non_empty': len([x for x in trad_field if x not in ['', 'NaN', None]]),
                    'completeness_pct': trad_completeness
                },
                'api': {
                    'total': len(api_field),
                    'non_empty': len([x for x in api_field if x not in ['', 'NaN', None]]),
                    'completeness_pct': api_completeness
                },
                'difference': api_completeness - trad_completeness
            }
        
        return completeness
    
    def _analyze_raw_data_structure(self, trad_data: Dict, api_data: Dict) -> Dict[str, Any]:
        """Analyze raw data structure differences."""
        trad_unfiltered = trad_data.get("Main", {}).get("YMS_unfiltered", [])
        api_unfiltered = api_data.get("Main", {}).get("YMS_unfiltered", [])
        
        if not trad_unfiltered or not api_unfiltered:
            return {"error": "No unfiltered data available"}
        
        trad_fields = set(trad_unfiltered[0].keys()) if trad_unfiltered else set()
        api_fields = set(api_unfiltered[0].keys()) if api_unfiltered else set()
        
        return {
            'traditional_fields': list(trad_fields),
            'api_fields': list(api_fields),
            'common_fields': list(trad_fields.intersection(api_fields)),
            'traditional_only': list(trad_fields - api_fields),
            'api_only': list(api_fields - trad_fields),
            'sample_traditional': trad_unfiltered[0] if trad_unfiltered else {},
            'sample_api': api_unfiltered[0] if api_unfiltered else {},
            'field_mapping_analysis': self._analyze_field_sources(trad_unfiltered[0], api_unfiltered[0])
        }
    
    def _analyze_field_sources(self, trad_sample: Dict, api_sample: Dict) -> Dict[str, Any]:
        """Analyze how key fields are sourced from raw data."""
        field_sources = {}
        
        for field, possible_sources in self.raw_field_mappings.items():
            field_sources[field] = {
                'traditional_available': {src: trad_sample.get(src) for src in possible_sources if src in trad_sample},
                'api_available': {src: api_sample.get(src) for src in possible_sources if src in api_sample},
                'mapping_strategy': self._determine_mapping_strategy(field, trad_sample, api_sample)
            }
        
        return field_sources
    
    def _determine_mapping_strategy(self, field: str, trad_sample: Dict, api_sample: Dict) -> str:
        """Determine the mapping strategy for a specific field."""
        possible_sources = self.raw_field_mappings.get(field, [])
        
        trad_available = [src for src in possible_sources if src in trad_sample and trad_sample[src]]
        api_available = [src for src in possible_sources if src in api_sample and api_sample[src]]
        
        if not trad_available and not api_available:
            return "no_data_available"
        elif trad_available == api_available:
            return "same_source"
        elif len(trad_available) > len(api_available):
            return "traditional_has_more_sources"
        elif len(api_available) > len(trad_available):
            return "api_has_more_sources"
        else:
            return "different_sources"
    
    def _analyze_mapping_quality(self, trad_data: Dict, api_data: Dict) -> Dict[str, Any]:
        """Analyze mapping quality differences."""
        trad_main = trad_data.get("Main", {})
        api_main = api_data.get("Main", {})
        
        quality_metrics = {}
        
        # Analyze specific quality issues
        for field in self.key_fields:
            trad_values = trad_main.get(field, [])
            api_values = api_main.get(field, [])
            
            # Compare values at same indices
            if len(trad_values) == len(api_values):
                matches = sum(1 for t, a in zip(trad_values, api_values) if t == a)
                quality_metrics[field] = {
                    'total_comparisons': len(trad_values),
                    'exact_matches': matches,
                    'match_percentage': (matches / len(trad_values) * 100) if trad_values else 0,
                    'api_improvements': self._count_improvements(trad_values, api_values),
                    'api_regressions': self._count_regressions(trad_values, api_values)
                }
        
        return quality_metrics
    
    def _count_improvements(self, trad_values: List, api_values: List) -> int:
        """Count where API improved empty/NaN values."""
        improvements = 0
        for t, a in zip(trad_values, api_values):
            if t in ['', 'NaN', None] and a not in ['', 'NaN', None]:
                improvements += 1
        return improvements
    
    def _count_regressions(self, trad_values: List, api_values: List) -> int:
        """Count where API made good values empty/NaN."""
        regressions = 0
        for t, a in zip(trad_values, api_values):
            if t not in ['', 'NaN', None] and a in ['', 'NaN', None]:
                regressions += 1
        return regressions
    
    def _analyze_vrid_mapping(self, trad_data: Dict, api_data: Dict) -> Dict[str, Any]:
        """Analyze VRID mapping specifically."""
        trad_main = trad_data.get("Main", {})
        api_main = api_data.get("Main", {})
        
        return {
            'traditional_vrid_stats': {
                'total_entries': trad_main.get('YMS_total_entries', 0),
                'nonempty_vrid': trad_main.get('YMS_nonempty_VRID_count', 0),
                'filled_from_fmc': trad_main.get('YMS_VRID_filled_from_FMC', 0),
                'unfiltered_vrid': trad_main.get('YMS_VRID_count_unfiltered', 0),
                'filtered_vrid': trad_main.get('YMS_VRID_count_filtered', 0)
            },
            'api_vrid_stats': {
                'total_entries': api_main.get('YMS_total_entries', 0),
                'nonempty_vrid': api_main.get('YMS_nonempty_VRID_count', 0),
                'filled_from_fmc': api_main.get('YMS_VRID_filled_from_FMC', 0),
                'unfiltered_vrid': api_main.get('YMS_VRID_count_unfiltered', 0),
                'filtered_vrid': api_main.get('YMS_VRID_count_filtered', 0)
            }
        }
    
    def _analyze_fmc_integration(self, trad_data: Dict, api_data: Dict) -> Dict[str, Any]:
        """Analyze FMC integration differences."""
        trad_main = trad_data.get("Main", {})
        api_main = api_data.get("Main", {})
        
        return {
            'traditional_fmc': {
                'total_entries': trad_main.get('FMC_total_entries', 0),
                'nonempty_vrid': trad_main.get('FMC_nonempty_VRID_count', 0)
            },
            'api_fmc': {
                'total_entries': api_main.get('FMC_total_entries', 0),
                'nonempty_vrid': api_main.get('FMC_nonempty_VRID_count', 0)
            },
            'fmc_utilization': {
                'traditional_utilization': trad_main.get('YMS_VRID_filled_from_FMC', 0),
                'api_utilization': api_main.get('YMS_VRID_filled_from_FMC', 0)
            }
        }
    
    def _calculate_completeness(self, field_values: List) -> float:
        """Calculate field completeness percentage."""
        if not field_values:
            return 0.0
        
        non_empty = len([x for x in field_values if x not in ['', 'NaN', None]])
        return (non_empty / len(field_values)) * 100.0
    
    def _generate_recommendations(self, analysis: Dict) -> List[str]:
        """Generate recommendations based on analysis."""
        recommendations = []
        
        field_completeness = analysis.get('field_completeness', {})
        
        for field, data in field_completeness.items():
            difference = data.get('difference', 0)
            
            if difference < -10:  # API is significantly worse
                recommendations.append(
                    f"CRITICAL: {field} completeness is {abs(difference):.1f}% lower in API implementation. "
                    f"Review mapping logic in YMS_API transformation."
                )
            elif difference > 10:  # API is significantly better
                recommendations.append(
                    f"POSITIVE: {field} completeness is {difference:.1f}% higher in API implementation. "
                    f"Consider backporting improvements to traditional YMS."
                )
        
        # Check record count differences
        record_diff = analysis.get('record_counts', {}).get('difference', 0)
        if abs(record_diff) > 5:
            recommendations.append(
                f"ATTENTION: Record count difference of {record_diff} between implementations. "
                f"Investigate data source differences."
            )
        
        return recommendations
    
    def generate_comprehensive_report(self, analyses: Dict[str, Dict]) -> Dict[str, Any]:
        """Generate comprehensive report across all sites."""
        logger.info("Generating comprehensive mapping report...")
        
        report = {
            'analysis_timestamp': datetime.now().isoformat(),
            'sites_analyzed': list(analyses.keys()),
            'summary': {
                'critical_issues': [],
                'positive_findings': [],
                'field_performance': {},
                'overall_recommendations': []
            },
            'detailed_analyses': analyses
        }
        
        # Aggregate findings across sites
        for site, analysis in analyses.items():
            if 'error' in analysis:
                continue
                
            # Aggregate field performance
            field_completeness = analysis.get('field_completeness', {})
            for field, data in field_completeness.items():
                if field not in report['summary']['field_performance']:
                    report['summary']['field_performance'][field] = []
                
                report['summary']['field_performance'][field].append({
                    'site': site,
                    'traditional_completeness': data['traditional']['completeness_pct'],
                    'api_completeness': data['api']['completeness_pct'],
                    'difference': data['difference']
                })
            
            # Collect critical issues
            for rec in analysis.get('recommendations', []):
                if 'CRITICAL' in rec:
                    report['summary']['critical_issues'].append(f"[{site}] {rec}")
                elif 'POSITIVE' in rec:
                    report['summary']['positive_findings'].append(f"[{site}] {rec}")
        
        # Generate overall recommendations
        report['summary']['overall_recommendations'] = self._generate_overall_recommendations(report)
        
        return report
    
    def _generate_overall_recommendations(self, report: Dict) -> List[str]:
        """Generate overall recommendations based on all site analyses."""
        recommendations = []
        
        field_performance = report['summary']['field_performance']
        
        for field, site_data in field_performance.items():
            avg_difference = sum(d['difference'] for d in site_data) / len(site_data)
            
            if avg_difference < -15:  # Consistently poor performance
                recommendations.append(
                    f"HIGH PRIORITY: {field} mapping consistently underperforms in API implementation "
                    f"by {abs(avg_difference):.1f}% on average. Review YMS_API transformation logic."
                )
            elif avg_difference > 15:  # Consistently good performance
                recommendations.append(
                    f"BACKPORT OPPORTUNITY: {field} mapping consistently outperforms in API implementation "
                    f"by {avg_difference:.1f}% on average. Consider enhancing traditional YMS."
                )
        
        return recommendations

def main():
    """Main function to run mapping analysis."""
    analyzer = YMSMappingAnalyzer()
    sites = ['CDG7', 'TRN3', 'ZAZ1', 'LBA4']
    
    logger.info("Starting YMS Mapping Analysis")
    
    all_analyses = {}
    
    for site in sites:
        trad_file = f"{site}_traditional.json"
        api_file = f"{site}_api.json"
        
        if os.path.exists(trad_file) and os.path.exists(api_file):
            logger.info(f"Analyzing {site}...")
            analysis = analyzer.analyze_field_mapping_differences(site, trad_file, api_file)
            all_analyses[site] = analysis
            
            # Save individual analysis
            with open(f"{site}_mapping_analysis.json", 'w') as f:
                json.dump(analysis, f, indent=2, default=str)
        else:
            logger.warning(f"Data files not found for {site}")
            all_analyses[site] = {"error": "Data files not found"}
    
    # Generate comprehensive report
    if all_analyses:
        comprehensive_report = analyzer.generate_comprehensive_report(all_analyses)
        
        with open("comprehensive_mapping_report.json", 'w') as f:
            json.dump(comprehensive_report, f, indent=2, default=str)
        
        logger.info("Comprehensive mapping report generated")
        
        # Print summary
        print("\n" + "="*80)
        print("YMS MAPPING ANALYSIS SUMMARY")
        print("="*80)
        
        for issue in comprehensive_report['summary']['critical_issues']:
            print(f"❌ {issue}")
        
        for finding in comprehensive_report['summary']['positive_findings']:
            print(f"✅ {finding}")
        
        for rec in comprehensive_report['summary']['overall_recommendations']:
            print(f"💡 {rec}")
        
        print("\n" + "="*80)

if __name__ == "__main__":
    main() 