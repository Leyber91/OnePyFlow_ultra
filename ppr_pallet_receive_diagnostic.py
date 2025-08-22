#!/usr/bin/env python3
"""
PPR Pallet Receive Diagnostic Script
Tests API connectivity for affected sites and dates to identify failure modes.
"""

import requests
import pandas as pd
import logging
from datetime import datetime, timedelta
from http.cookiejar import MozillaCookieJar
from io import StringIO
from getpass import getuser
from typing import Dict, Any, List, Optional
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler()]
)

class PPRDiagnostic:
    def __init__(self):
        self.cookie_file_path = f'C:/Users/{getuser()}/.midway/cookie'
        self.process_id = "1003032"  # Pallet Receive process ID
        self.load_cookies()
        
    def load_cookies(self) -> None:
        """Load session cookies for API access."""
        logging.info('Loading cookies for diagnostic...')
        self.cookie_jar = MozillaCookieJar(self.cookie_file_path)
        try:
            self.cookie_jar.load(ignore_discard=True, ignore_expires=True)
            for cookie in self.cookie_jar:
                if 'session' in cookie.name:
                    self.midway_session = f'session={cookie.value}'
                    logging.info('Session cookie loaded successfully.')
                    break
            else:
                logging.warning('Session cookie not found in the cookie file.')
        except FileNotFoundError:
            logging.error(f'Cookie file not found at {self.cookie_file_path}.')
        except Exception as e:
            logging.error(f'Error loading cookies: {e}')

    def build_url(self, site: str, start_datetime: datetime, end_datetime: datetime, 
                  include_adjust_plan_hours: bool = True) -> str:
        """Build API URL with configurable parameters."""
        base_url = "https://fclm-portal.amazon.com/reports/"
        
        url = (
            f"{base_url}functionRollup?reportFormat=CSV&warehouseId={site}"
            f"&processId={self.process_id}&maxIntradayDays=1&spanType=Intraday&startDateIntraday="
            f"{start_datetime.strftime('%Y/%m/%d')}&startHourIntraday={start_datetime.strftime('%H')}"
            f"&startMinuteIntraday={start_datetime.strftime('%M').lstrip('0') or '0'}&endDateIntraday="
            f"{end_datetime.strftime('%Y/%m/%d')}&endHourIntraday={end_datetime.strftime('%H')}"
            f"&endMinuteIntraday={end_datetime.strftime('%M').lstrip('0') or '0'}"
        )
        
        if include_adjust_plan_hours:
            url += "&_adjustPlanHours=on&_hideEmptyLineItems=on&employmentType=AllEmployees"
            
        return url

    def test_api_request(self, url: str, test_name: str) -> Dict[str, Any]:
        """Test a single API request and return detailed results."""
        result = {
            "test_name": test_name,
            "url": url,
            "status_code": None,
            "response_size": 0,
            "has_data": False,
            "error": None,
            "success": False
        }
        
        try:
            logging.info(f"Testing: {test_name}")
            response = requests.get(url, cookies=self.cookie_jar, verify=False, timeout=30)
            result["status_code"] = response.status_code
            result["response_size"] = len(response.text)
            
            if response.status_code == 200:
                if response.text.strip():
                    try:
                        df = pd.read_csv(StringIO(response.text), delimiter=';', encoding='ISO-8859-1')
                        result["has_data"] = not df.empty
                        result["success"] = True
                        logging.info(f"✓ {test_name}: Success - {len(df)} rows")
                    except Exception as e:
                        result["error"] = f"CSV parsing error: {e}"
                        logging.warning(f"⚠ {test_name}: CSV parsing failed - {e}")
                else:
                    result["error"] = "Empty response body"
                    logging.warning(f"⚠ {test_name}: Empty response body")
            else:
                result["error"] = f"HTTP {response.status_code}"
                logging.error(f"✗ {test_name}: HTTP {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            result["error"] = f"Request exception: {e}"
            logging.error(f"✗ {test_name}: Request failed - {e}")
            
        return result

    def test_current_shift(self, site: str) -> List[Dict[str, Any]]:
        """Test current shift data fetching."""
        results = []
        
        # Current time
        now = datetime.now()
        start_time = now.replace(hour=now.hour - 1, minute=0, second=0, microsecond=0)
        end_time = now.replace(minute=0, second=0, microsecond=0)
        
        # Test 1: Current shift with _adjustPlanHours=on
        url1 = self.build_url(site, start_time, end_time, include_adjust_plan_hours=True)
        results.append(self.test_api_request(url1, f"{site} - Current Shift (with _adjustPlanHours)"))
        
        # Test 2: Current shift without _adjustPlanHours
        url2 = self.build_url(site, start_time, end_time, include_adjust_plan_hours=False)
        results.append(self.test_api_request(url2, f"{site} - Current Shift (without _adjustPlanHours)"))
        
        return results

    def test_historical_weeks(self, site: str) -> List[Dict[str, Any]]:
        """Test historical data fetching (1-4 weeks back)."""
        results = []
        base_time = datetime.now()
        
        for week in range(1, 5):
            # Calculate historical time (same as PPR module)
            historical_start = base_time - timedelta(weeks=week)
            historical_end = historical_start + timedelta(hours=2)
            
            url = self.build_url(site, historical_start, historical_end, include_adjust_plan_hours=True)
            results.append(self.test_api_request(url, f"{site} - {week} week(s) back"))
            
        return results

    def test_affected_dates(self, site: str) -> List[Dict[str, Any]]:
        """Test the specific dates mentioned in the issue (June 5-7, 2025)."""
        results = []
        
        # Test June 5-7, 2025 (these dates are in the future, so we'll test similar past dates)
        test_dates = [
            (datetime(2025, 6, 5, 6, 0), datetime(2025, 6, 5, 8, 0)),  # June 5, 2025
            (datetime(2025, 6, 6, 6, 0), datetime(2025, 6, 6, 8, 0)),  # June 6, 2025
            (datetime(2025, 6, 7, 6, 0), datetime(2025, 6, 7, 8, 0)),  # June 7, 2025
        ]
        
        for i, (start_time, end_time) in enumerate(test_dates):
            url = self.build_url(site, start_time, end_time, include_adjust_plan_hours=True)
            results.append(self.test_api_request(url, f"{site} - June {5+i}, 2025"))
            
        return results

    def test_extended_time_ranges(self, site: str) -> List[Dict[str, Any]]:
        """Test extended time ranges like PPR_Q module."""
        results = []
        now = datetime.now()
        
        # Test 1: Exact 2-hour range
        start_time = now.replace(hour=now.hour - 1, minute=0, second=0, microsecond=0)
        end_time = now.replace(minute=0, second=0, microsecond=0)
        url1 = self.build_url(site, start_time, end_time, include_adjust_plan_hours=True)
        results.append(self.test_api_request(url1, f"{site} - Exact 2-hour range"))
        
        # Test 2: Extended 6-hour range
        extended_start = start_time - timedelta(hours=2)
        extended_end = end_time + timedelta(hours=2)
        url2 = self.build_url(site, extended_start, extended_end, include_adjust_plan_hours=True)
        results.append(self.test_api_request(url2, f"{site} - Extended 6-hour range"))
        
        # Test 3: Extended 24-hour range
        full_extended_start = start_time - timedelta(hours=12)
        full_extended_end = end_time + timedelta(hours=12)
        url3 = self.build_url(site, full_extended_start, full_extended_end, include_adjust_plan_hours=True)
        results.append(self.test_api_request(url3, f"{site} - Extended 24-hour range"))
        
        return results

    def run_diagnostics(self) -> Dict[str, Any]:
        """Run comprehensive diagnostics for all affected sites."""
        sites = ["CDG7", "ZAZ1", "WRO5", "DTM1", "DTM2"]  # Include DTM sites for comparison
        all_results = {}
        
        logging.info("=" * 80)
        logging.info("PPR PALLET RECEIVE DIAGNOSTIC SCRIPT")
        logging.info("=" * 80)
        
        for site in sites:
            logging.info(f"\n{'='*20} TESTING SITE: {site} {'='*20}")
            site_results = {}
            
            # Test current shift
            logging.info(f"\n--- Current Shift Tests ---")
            site_results["current_shift"] = self.test_current_shift(site)
            
            # Test historical weeks
            logging.info(f"\n--- Historical Weeks Tests ---")
            site_results["historical_weeks"] = self.test_historical_weeks(site)
            
            # Test affected dates
            logging.info(f"\n--- Affected Dates Tests ---")
            site_results["affected_dates"] = self.test_affected_dates(site)
            
            # Test extended time ranges
            logging.info(f"\n--- Extended Time Range Tests ---")
            site_results["extended_ranges"] = self.test_extended_time_ranges(site)
            
            all_results[site] = site_results
            
        return all_results

    def generate_report(self, results: Dict[str, Any]) -> str:
        """Generate a comprehensive diagnostic report."""
        report = []
        report.append("=" * 80)
        report.append("PPR PALLET RECEIVE DIAGNOSTIC REPORT")
        report.append("=" * 80)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Summary statistics
        total_tests = 0
        successful_tests = 0
        failed_tests = 0
        
        for site, site_results in results.items():
            report.append(f"\n{'='*20} SITE: {site} {'='*20}")
            
            for test_category, tests in site_results.items():
                report.append(f"\n--- {test_category.upper().replace('_', ' ')} ---")
                
                for test in tests:
                    total_tests += 1
                    status = "✓ SUCCESS" if test["success"] else "✗ FAILED"
                    report.append(f"{status}: {test['test_name']}")
                    
                    if test["success"]:
                        successful_tests += 1
                    else:
                        failed_tests += 1
                        if test["error"]:
                            report.append(f"  Error: {test['error']}")
                        if test["status_code"]:
                            report.append(f"  Status: {test['status_code']}")
                        if test["response_size"] == 0:
                            report.append(f"  Response: Empty")
                        else:
                            report.append(f"  Response: {test['response_size']} bytes")
        
        # Overall summary
        report.append(f"\n{'='*20} SUMMARY {'='*20}")
        report.append(f"Total Tests: {total_tests}")
        report.append(f"Successful: {successful_tests}")
        report.append(f"Failed: {failed_tests}")
        report.append(f"Success Rate: {(successful_tests/total_tests*100):.1f}%" if total_tests > 0 else "N/A")
        
        # Recommendations
        report.append(f"\n{'='*20} RECOMMENDATIONS {'='*20}")
        if failed_tests > 0:
            report.append("1. Check API connectivity and session cookies")
            report.append("2. Verify process ID 1003032 is still valid")
            report.append("3. Test manual access to FCLM portal")
            report.append("4. Consider implementing PPR_Q fallback logic")
        else:
            report.append("✓ All tests passed - API connectivity is working")
            
        return "\n".join(report)

def main():
    """Main diagnostic function."""
    diagnostic = PPRDiagnostic()
    results = diagnostic.run_diagnostics()
    
    # Generate and save report
    report = diagnostic.generate_report(results)
    
    # Save to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_filename = f"ppr_diagnostic_report_{timestamp}.txt"
    
    with open(report_filename, 'w', encoding='utf-8') as f:
        f.write(report)
    
    # Also save raw results as JSON
    json_filename = f"ppr_diagnostic_results_{timestamp}.json"
    with open(json_filename, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    logging.info(f"\nDiagnostic report saved to: {report_filename}")
    logging.info(f"Raw results saved to: {json_filename}")
    
    # Print summary to console
    print("\n" + "="*80)
    print("DIAGNOSTIC COMPLETE")
    print("="*80)
    print(report)

if __name__ == "__main__":
    main() 