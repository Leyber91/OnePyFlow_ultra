import subprocess
import requests
import os
import json
import time
import logging
import pandas as pd
from datetime import datetime, timedelta
from http.cookiejar import MozillaCookieJar
from io import StringIO
from getpass import getuser
from typing import Dict, Any, List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configure logging
logging.basicConfig(
    level=logging.INFO,  # Set to DEBUG for more detailed logs
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

class PPRProcessor:
    """
    A processor for handling PPR (Process Performance Reports) data fetching, cleaning, and processing.
    """

    def __init__(self, site: str, sos_datetime: datetime, eos_datetime: datetime):
        """
        Initializes the PPRProcessor with site details and datetime range.

        Args:
            site (str): The warehouse site identifier.
            sos_datetime (datetime): Start of the shift datetime.
            eos_datetime (datetime): End of the shift datetime.
        """
        self.site = site
        self.sos_datetime = sos_datetime
        self.eos_datetime = eos_datetime
        self.cookie_file_path = f'C:/Users/{getuser()}/.midway/cookie'

        # Define all processes with their corresponding process IDs
        self.processes = {
            "PPR_PRU": "",
            "PPR_Case_Receive": "1003025",
            "PPR_Cubiscan": "1002971",
            "PPR_Each_Receive": "1003027",
            "PPR_LP_Receive": "1003031",
            "PPR_Pallet_Receive": "1003032",
            "PPR_Prep_Recorder": "01003002",
            "PPR_RC_Presort": "1003008",
            "PPR_RC_Sort": "1003009",
            "PPR_Receive_Dock": "1003010",
            "PPR_Receive_Support": "1003033",
            "PPR_Transfer_Out": "1003021",
            "PPR_Transfer_Out_Dock": "1003022"
        }

        # Dictionary to store processed data
        self.PPR_JSON: Dict[str, Any] = {}

        # Track execution time
        self.start_time = time.time()

        # Load session cookies
        self.load_cookies()

        # Configuration for each process
        self.process_config: Dict[str, Dict[str, Any]] = self.initialize_process_config()

    def initialize_process_config(self) -> Dict[str, Dict[str, Any]]:
        """
        Initializes the configuration for each process to define how they should be processed.

        Returns:
            Dict[str, Dict[str, Any]]: Configuration dictionary for each process.
        """
        return {
            # ---------------------------------------------------------------------
            # CONFIG: PPR_PRU
            # ---------------------------------------------------------------------
            "PPR_PRU": {
                "columns": {
                    "PRU_LineItem_Name": 3,
                    "PRU_Actual_Volume": 14,
                    "PRU_Actual_Hours": 15,
                    "PRU_Actual_Rate": 16
                },
                "sums": {
                    "PrepRecorder_Volume": {"condition": (3, "Prep Recorder - Total"), "column": 7},
                    "PrepRecorder_Hours": {"condition": (3, "Prep Recorder - Total"), "column": 8},
                    "Cubi_Rate": {"condition": (3, "Cubiscan"), "column": 9, "divide_by": 4},
                    "PRU_Receive_Dock": {"condition": (3, "Receive Dock"), "column": 9, "divide_by": 4},
                    "PRU_Receive_Support": {"condition": (3, "Receive Support"), "column": 9, "divide_by": 4},
                    "PRU_Prep_Support": {"condition": (3, "Prep Support"), "column": 9, "divide_by": 4},
                    "PRU_RSR_Support": {"condition": (3, "RSR Support"), "column": 9, "divide_by": 4},
                    "PRU_IB_Lead_PA": {"condition": (3, "IB Lead/PA"), "column": 9, "divide_by": 4},
                    "PRU_IB_ProblemSolve": {"condition": (3, "IB Problem Solve"), "column": 9, "divide_by": 4},
                    "PRU_Transfer_Out_Dock": {"condition": (3, "Transfer Out Dock"), "column": 9, "divide_by": 4},
                    "PRU_TO_Lead_PA": {"condition": (3, "TO Lead/PA"), "column": 9, "divide_by": 4},
                    "PRU_TO_ProblemSolve": {"condition": (3, "TO Problem Solve"), "column": 9, "divide_by": 4},
                    "PRU_Each_Receive_Total": {"condition": (3, "Each Receive - Total"), "column": 9, "divide_by": 4},
                    "PRU_LP_Receive": {"condition": (3, "LP Receive"), "column": 9, "divide_by": 4},
                    "PRU_RC_Sort_Total": {"condition": (3, "RC Sort - Total"), "column": 9, "divide_by": 4},
                    "PRU_Transfer_Out": {"condition": (3, "Transfer Out"), "column": 9, "divide_by": 4}
                }
            },

            # ---------------------------------------------------------------------
            # CONFIG: PPR_Case_Receive
            # ---------------------------------------------------------------------
            "PPR_Case_Receive": {
                "columns": {
                    "Case_Receive_Paid_Hours": 10,
                    "Case_Receive_Unit_Type": 14,
                    "Case_Receive_Size": 15,
                    "Case_Receive_Units": 16
                },
                "sums": {
                    "Cases": {
                        "conditions": [(15, "Total"), (14, "Case")],
                        "column": 16
                    },
                    "Hours": {
                        "conditions": [(15, "Total"), (14, "EACH")],
                        "column": 10
                    }
                }
            },

            # ---------------------------------------------------------------------
            # CONFIG: PPR_Cubiscan
            # ---------------------------------------------------------------------
            "PPR_Cubiscan": {
                "columns": {
                    "Cubiscan_Function_Name": 1,
                    "Cubiscan_Unit_Type": 14,
                    "Cubiscan_Size": 15,
                    "Cubiscan_Units": 16
                },
                "sums": {
                    "ATACEgress_TotalUnits": {
                        "conditions": [(15, "Total"), (14, "EACH"), (1, "ATAC Egress")],
                        "column": 16
                    },
                    "ATACEgress_TotalCases": {
                        "conditions": [(15, "Total"), (14, "Bin"), (1, "ATAC Egress")],
                        "column": 16
                    },
                    "Cubiscan_TotalUnits": {
                        "conditions": [(15, "Total"), (14, "EACH"), (1, "Cubiscan")],
                        "column": 16
                    },
                    "Cubiscan_TotalCases": {
                        "conditions": [(15, "Total"), (14, "Bin"), (1, "Cubiscan")],
                        "column": 16
                    },
                    "SmallsTotal": {
                        "conditions": [(15, "Small")],
                        "column": 16
                    },
                    "Total": {
                        "conditions": [(15, "Total")],
                        "column": 16
                    }
                }
            },

            # ---------------------------------------------------------------------
            # CONFIG: PPR_Each_Receive
            # ---------------------------------------------------------------------
            "PPR_Each_Receive": {
                "columns": {
                    "Each_Receive_function_name": 1,
                    "Each_Receive_unit_type": 14,
                    "Each_Receive_Size": 15,
                    "Each_Receive_Units": 16
                },
                "sums": {
                    "Each_Receive_TotalUnits": {
                        "conditions": [(15, "Total"), (14, "EACH"), (1, "Each Receive")],
                        "column": 16
                    },
                    "No_Prep_Req_Prep_Rcv_TotalUnits": {
                        "conditions": [(15, "Total"), (14, "EACH"), (1, "No Prep Req Prep Rcv")],
                        "column": 16
                    },
                    "ReceiveUniversal_BEG_TotalUnits": {
                        "conditions": [(15, "Total"), (14, "EACH"), (1, "ReceiveUniversal.BEG")],
                        "column": 16
                    },
                    "ReceiveUniversal_INT_TotalUnits": {
                        "conditions": [(15, "Total"), (14, "EACH"), (1, "ReceiveUniversal.INT")],
                        "column": 16
                    },
                    "Receive_Small_A_TotalUnits": {
                        "conditions": [(15, "Total"), (14, "EACH"), (1, "Receive Small A")],
                        "column": 16
                    },
                    "Receive_Universal_EXP_TotalUnits": {
                        "conditions": [(15, "Total"), (14, "EACH"), (1, "ReceiveUniversal.EXP")],
                        "column": 16
                    },
                    "Receive_Large_A_TotalUnits": {
                        "conditions": [(15, "Total"), (14, "EACH"), (1, "Receive Large A")],
                        "column": 16
                    },
                    "SmallsTotal": {
                        "conditions": [(15, "Small")],
                        "column": 16
                    },
                    "Total": {
                        "conditions": [(15, "Total")],
                        "column": 16
                    }
                }
            },

            # ---------------------------------------------------------------------
            # CONFIG: PPR_LP_Receive
            # ---------------------------------------------------------------------
            "PPR_LP_Receive": {
                "columns": {
                    "LP_Receive_function_name": 1,
                    "LP_Receive_paid_hours_total": 10,
                    "LP_Receive_unit_type": 14,
                    "LP_Receive_Size": 15,
                    "LP_Receive_Units": 16
                },
                "sums": {
                    "PID_Receive_TotalUnits": {
                        "conditions": [(15, "Total"), (14, "EACH"), (1, "PID Receive")],
                        "column": 16
                    },
                    "PrEditor_Receive_TotalUnits": {
                        "conditions": [(15, "Total"), (14, "EACH"), (1, "PrEditor Receive")],
                        "column": 16
                    },
                    "PrEditor_Receive_TotalHours": {
                        "conditions": [(15, "Total"), (14, "EACH"), (1, "PrEditor Receive")],
                        "column": 10
                    },
                    "PrEditor_Receive_TotalCases": {
                        "conditions": [(15, "Total"), (14, "Case"), (1, "PrEditor Receive")],
                        "column": 16
                    },
                    "SmallsTotal": {
                        "conditions": [(15, "Small")],
                        "column": 16
                    },
                    "Total": {
                        "conditions": [(15, "Total")],
                        "column": 16
                    }
                }
            },

            # ---------------------------------------------------------------------
            # CONFIG: PPR_Pallet_Receive
            # ---------------------------------------------------------------------
            "PPR_Pallet_Receive": {
                "columns": {
                    "Pallet_Receive_function_name": 1,
                    "Pallet_Receive_paid_hours_total": 10,
                    "Pallet_Receive_unit_type": 14,
                    "Pallet_Receive_Size": 15,
                    "Pallet_Receive_Units": 16
                },
                "sums": {
                    # PalletPrEditor-LP total units for EACH and TOTAL size lines
                    "PalletPrEditor_LP_TotalUnits": {
                        "conditions": [
                            (15, "Total"),        # Size = Total
                            (14, "EACH"),         # Unit Type = EACH
                            (1, "PalletPrEditor-LP")
                        ],
                        "column": 16
                    },
                    # PalletPrEditorManual total UNITS => STILL filters to (Size=Total, Unit=EACH)
                    "PalletPrEditorManual_TotalUnits": {
                        "conditions": [
                            (15, "Total"),
                            (14, "EACH"),
                            (1, "PalletPrEditorManual")
                        ],
                        "column": 16
                    },
                    # PalletPrEditorManual total HOURS => BROADEN to ANY row with (1, "PalletPrEditorManual")
                    "PalletPrEditorManual_TotalHours": {
                        "conditions": [
                            (1, "PalletPrEditorManual")
                        ],
                        "column": 10
                    },
                    # Total cases: Unit Type=Case + Size=Total
                    "Pallet_Receive_TotalCases": {
                        "conditions": [
                            (14, "Case"),
                            (15, "Total")
                        ],
                        "column": 16
                    },
                    # Total pallets: Unit Type=Pallet + Size=Total
                    "Pallet_Receive_TotalPallets": {
                        "conditions": [
                            (14, "Pallet"),
                            (15, "Total")
                        ],
                        "column": 16
                    },
                    "SmallsTotal": {
                        "conditions": [
                            (15, "Small")
                        ],
                        "column": 16
                    },
                    "Total": {
                        "conditions": [
                            (15, "Total")
                        ],
                        "column": 16
                    }
                }
            },

            # ---------------------------------------------------------------------
            # CONFIG: PPR_Prep_Recorder
            # ---------------------------------------------------------------------
            "PPR_Prep_Recorder": {
                "columns": {
                    "Prep_Recorder_paid_hours_total": 10,
                    "Prep_Recorder_job_action": 11,
                    "Prep_Recorder_unit_type": 14,
                    "Prep_Recorder_Size": 15,
                    "Prep_Recorder_Units": 16
                },
                "sums": {
                    "EachReceived_TotalUnits": {
                        "conditions": [(15, "Total"), (14, "EACH"), (11, "EachReceived")],
                        "column": 16
                    },
                    "ItemPrepped_TotalUnits": {
                        "conditions": [(15, "Total"), (14, "EACH"), (11, "ItemPrepped")],
                        "column": 16
                    },
                    "ItemPrepped_TotalHours": {
                        "conditions": [(15, "Total"), (14, "EACH"), (11, "ItemPrepped")],
                        "column": 10
                    },
                    "PrepAssortment_TotalUnits": {
                        "conditions": [(15, "Total"), (14, "EACH"), (11, "PrepAssortment")],
                        "column": 16
                    },
                    "PrepAssortment_TotalHours": {
                        "conditions": [(15, "Total"), (14, "EACH"), (11, "PrepAssortment")],
                        "column": 10
                    },
                    "PalletReceived_TotalUnits": {
                        "conditions": [(15, "Total"), (14, "EACH"), (11, "PalletReceived")],
                        "column": 16
                    },
                    "SmallsTotal": {
                        "conditions": [(15, "Small")],
                        "column": 16
                    },
                    "Total": {
                        "conditions": [(15, "Total")],
                        "column": 16
                    }
                }
            },

            # ---------------------------------------------------------------------
            # CONFIG: PPR_RC_Presort
            # ---------------------------------------------------------------------
            "PPR_RC_Presort": {
                "columns": {},
                "sums": {
                    "RC_Presort_size": {"conditions": [(15, "Total")], "column": 16},
                    "RC_Presort_units": {"conditions": [(15, "Total")], "column": 16},
                    "Total": {"conditions": [(15, "Total")], "column": 16}
                }
            },

            # ---------------------------------------------------------------------
            # CONFIG: PPR_RC_Sort
            # ---------------------------------------------------------------------
            "PPR_RC_Sort": {
                "columns": {
                    "RC_Sort_function_name": 1,
                    "RC_Sort_paid_hours_total": 10,
                    "RC_Sort_unit_type": 14,
                    "RC_Sort_size": 15,
                    "RC_Sort_units": 16
                },
                "sums": {
                    "RC_Sort_Primary_TotalUnits": {
                        "conditions": [(15, "Total"), (14, "EACH"), (1, "RC Sort Primary")],
                        "column": 16
                    },
                    "RC_Sort_Primary_TotalHours": {
                        "conditions": [(15, "Total"), (14, "EACH"), (1, "RC Sort Primary")],
                        "column": 10
                    },
                    "UIS_5lb_Induct_TotalUnits": {
                        "conditions": [(15, "Total"), (14, "EACH"), (1, "UIS_5lb_Induct")],
                        "column": 16
                    },
                    "UIS_5lb_Induct_TotalHours": {
                        "conditions": [(15, "Total"), (14, "EACH"), (1, "UIS_5lb_Induct")],
                        "column": 10
                    },
                    "UIS_20lb_Induct_TotalUnits": {
                        "conditions": [(15, "Total"), (14, "EACH"), (1, "UIS_20lb_Induct")],
                        "column": 16
                    },
                    "UIS_20lb_Induct_TotalHours": {
                        "conditions": [(15, "Total"), (14, "EACH"), (1, "UIS_20lb_Induct")],
                        "column": 10
                    },
                    "Small_Units_Manual": {
                        "conditions": [(15, "Small"), (14, "EACH"), (1, "RC Sort Primary")],
                        "column": 16
                    },
                    "Small_Units_UIS5": {
                        "conditions": [(15, "Small"), (14, "EACH"), (1, "UIS_5lb_Induct")],
                        "column": 16
                    },
                    "Small_Units_UIS20": {
                        "conditions": [(15, "Small"), (14, "EACH"), (1, "UIS_20lb_Induct")],
                        "column": 16
                    }
                }
            },

            # ---------------------------------------------------------------------
            # CONFIG: PPR_Receive_Dock
            # ---------------------------------------------------------------------
            "PPR_Receive_Dock": {
                "columns": {},
                "sums": {}
                # No calculations needed
            },

            # ---------------------------------------------------------------------
            # CONFIG: PPR_Receive_Support
            # ---------------------------------------------------------------------
            "PPR_Receive_Support": {
                "columns": {
                    "Receive_Support_function_name": 1,
                    "Receive_Support_paid_hours": 10,
                    "Receive_Support_unit_type": 14,
                    "Receive_Support_size": 15,
                    "Receive_Support_units": 16
                },
                "sums": {
                    "Decant_NonTI_Units": {
                        "conditions": [(15, "Total"), (14, "EACH"), (1, "Decant Non-TI")],
                        "column": 16
                    },
                    "Decant_NonTI_Hours": {
                        "conditions": [(15, "Total"), (14, "EACH"), (1, "Decant Non-TI")],
                        "column": 10
                    },
                    "Cases_Decanat": {
                        "conditions": [(15, "Total"), (14, "Case"), (1, "Decant Non-TI")],
                        "column": 16
                    },
                    "SmallsTotal": {
                        "conditions": [(15, "Small")],
                        "column": 16
                    },
                    "Total": {
                        "conditions": [(15, "Total")],
                        "column": 16
                    }
                }
            },

            # ---------------------------------------------------------------------
            # CONFIG: PPR_Transfer_Out
            # ---------------------------------------------------------------------
            "PPR_Transfer_Out": {
                "columns": {
                    "Transfer_Out_function_name": 1,
                    "Transfer_Out_name": 4,
                    "Transfer_Out_paid_hours_total": 10,
                    "Transfer_Out_paid_job_action": 11,
                    "Transfer_Out_unit_type": 14,
                    "Transfer_Out_Size": 15,
                    "Transfer_Out_Units": 16
                },
                "sums": {
                    "Fluid_Load_Tote": {
                        "conditions": [(15, "Total"), (14, "EACH"), (11, "FluidLoadTote")],
                        "column": 16
                    },
                    "Fluid_Load_Case": {
                        "conditions": [(15, "Total"), (14, "EACH"), (11, "FluidLoadCase")],
                        "column": 16
                    },
                    "LP_Received": {
                        "conditions": [(15, "Total"), (14, "EACH"), (11, "LPReceived")],
                        "column": 16
                    },
                    "Merged_Container": {
                        "conditions": [(15, "Total"), (14, "EACH"), (11, "MergeContainer")],
                        "column": 16
                    },
                    "Pallet_Checkin": {
                        "conditions": [(15, "Total"), (14, "EACH"), (11, "PalletCheckin")],
                        "column": 16
                    },
                    "Presort_Item_Scanned": {
                        "conditions": [(15, "Total"), (14, "EACH"), (11, "PresortItemScanned")],
                        "column": 16
                    },
                    "Scan_Case_To_Pallet": {
                        "conditions": [(15, "Total"), (14, "EACH"), (11, "ScanCaseToPallet")],
                        "column": 16
                    },
                    "Scan_Tote_To_Pallet": {
                        "conditions": [(15, "Total"), (14, "EACH"), (11, "ScanToteToPallet")],
                        "column": 16
                    },
                    "Transship_Pallet_Verified": {
                        "conditions": [(15, "Total"), (14, "EACH"), (11, "TransshipPalletVerified")],
                        "column": 16
                    },
                    "Palletized_Robot": {
                        "conditions": [(4, "Anonymous"), (14, "EACH"), (15, "Total"), (11, "ScanToteToPallet")],
                        "column": 16
                    },
                    "Palletized_Cases": {
                        "conditions": [(14, "EACH"), (15, "Total"), (11, "ScanCaseToPallet")],
                        "column": 16
                    },
                    "Fluid_Totes": {
                        "conditions": [(15, "Total"), (14, "EACH"), (11, "FluidLoadTote")],
                        "column": 16
                    },
                    "Fluid_Cases": {
                        "conditions": [(15, "Total"), (14, "EACH"), (11, "FluidLoadCase")],
                        "column": 16
                    },
                    "Totes_Robot_Palletized": {
                        "conditions": [(4, "Anonymous"), (14, "Tote"), (15, "Total"), (11, "ScanToteToPallet")],
                        "column": 16
                    },
                    "Totes_Totales_Palletized": {
                        "conditions": [(14, "Tote"), (15, "Total"), (11, "ScanToteToPallet")],
                        "column": 16
                    },
                    "Cajas_Manual": {
                        "conditions": [(14, "Case"), (15, "Total"), (11, "ScanCaseToPallet")],
                        "column": 16
                    },
                    "Containers_Fluids_Totes": {
                        "conditions": [(14, "Tote"), (15, "Total"), (11, "FluidLoadTote")],
                        "column": 16
                    },
                    "Containers_Fluids_Cases": {
                        "conditions": [(14, "Case"), (15, "Total"), (11, "FluidLoadCase")],
                        "column": 16
                    },
                    "Wall_Builder_Hours": {
                        "conditions": [(1, "Wall Builder")],
                        "column": 10
                    },
                    "Palletized_Cases_Hours": {
                        "conditions": [(1, "Palletize - Case"), (14, "EACH"), (15, "Total"), (11, "ScanCaseToPallet")],
                        "column": 10
                    },
                    "Units_Merged": {
                        "conditions": [(14, "EACH"), (15, "Total"), (11, "MergeContainer")],
                        "column": 16
                    },
                    "Containers_Merged": {
                        "conditions": [(14, "Container"), (15, "Total"), (11, "MergeContainer")],
                        "column": 16
                    },
                    "Merge_Hours": {
                        "conditions": [(14, "EACH"), (15, "Total"), (11, "MergeContainer")],
                        "column": 10
                    },
                    "Palletized_Totes_Manual": {
                        "conditions": [(14, "Tote"), (15, "Total"), (11, "ScanToteToPallet")],
                        "column": 16
                    }
                }
            },

            # ---------------------------------------------------------------------
            # CONFIG: PPR_Transfer_Out_Dock
            # ---------------------------------------------------------------------
            "PPR_Transfer_Out_Dock": {
                "columns": {
                    "Transfer_Out_Dock_job_action": 11,
                    "Transfer_Out_Dock_unit_type": 14,
                    "Transfer_Out_Dock_Size": 15,
                    "Transfer_Out_Dock_Units": 16
                },
                "sums": {
                    "Fluid_Load_Tote": {
                        "conditions": [(15, "Total"), (14, "EACH"), (11, "FluidLoadTote")],
                        "column": 16
                    },
                    "Fluid_Load_Case": {
                        "conditions": [(15, "Total"), (14, "EACH"), (11, "FluidLoadCase")],
                        "column": 16
                    }
                }
            }
        }

    def load_cookies(self) -> None:
        """
        Loads cookies from the specified cookie file to maintain session.
        """
        logging.info('Loading cookies for PPR pulling...')
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

    def build_url(self, process_key: str, process_id: str, shift: Dict[str, str]) -> str:
        """
        Constructs the URL for the API request based on process and shift details.
        """
        base_url = "https://fclm-portal.amazon.com/reports/"
        if not process_id:
            # For processes without a specific process_id
            url = (
                f"{base_url}processPathRollup?reportFormat=CSV&warehouseId={self.site}"
                f"&maxIntradayDays=1&spanType=Intraday&startDateIntraday={shift['start_year']}/"
                f"{shift['start_month']}/{shift['start_day']}&startHourIntraday={shift['start_hour']}"
                f"&startMinuteIntraday={shift['start_minute']}&endDateIntraday={shift['end_year']}/"
                f"{shift['end_month']}/{shift['end_day']}&endHourIntraday={shift['end_hour']}"
                f"&endMinuteIntraday={shift['end_minute']}&_adjustPlanHours=on&_hideEmptyLineItems=on"
                f"&employmentType=AllEmployees"
            )
        else:
            # For processes with a specific process_id
            url = (
                f"{base_url}functionRollup?reportFormat=CSV&warehouseId={self.site}"
                f"&processId={process_id}&maxIntradayDays=1&spanType=Intraday&startDateIntraday="
                f"{shift['start_year']}/{shift['start_month']}/{shift['start_day']}&startHourIntraday="
                f"{shift['start_hour']}&startMinuteIntraday={shift['start_minute']}&endDateIntraday="
                f"{shift['end_year']}/{shift['end_month']}/{shift['end_day']}&endHourIntraday="
                f"{shift['end_hour']}&endMinuteIntraday={shift['end_minute']}"
            )
        logging.debug(f"Request URL for {process_key}: {url}")
        return url

    def get_shifts(self, weeks_back: int = 4) -> List[Dict[str, str]]:
        """
        Generates a list of shift dictionaries for the past 'weeks_back' weeks.
        """
        shifts = []
        for i in range(1, weeks_back + 1):
            shift_start = self.sos_datetime - timedelta(weeks=i)
            shift_end = self.eos_datetime - timedelta(weeks=i)
            shift = {
                'start_hour': shift_start.strftime("%H"),
                'start_minute': shift_start.strftime("%M").lstrip('0') or '0',
                'start_day': shift_start.strftime("%d"),
                'start_month': shift_start.strftime("%m"),
                'start_year': shift_start.strftime("%Y"),
                'end_hour': shift_end.strftime("%H"),
                'end_minute': shift_end.strftime("%M").lstrip('0') or '0',
                'end_day': shift_end.strftime("%d"),
                'end_month': shift_end.strftime("%m"),
                'end_year': shift_end.strftime("%Y")
            }
            shifts.append(shift)
            logging.debug(f"Generated shift {i}: {shift}")
        return shifts

    def fetch_process_data(self, process_key: str, process_id: str) -> pd.DataFrame:
        """
        Fetches data for a specific process across multiple shifts.
        """
        logging.info(f"Fetching data for process: {process_key}")
        process_df = pd.DataFrame()
        shifts = self.get_shifts()

        for idx, shift in enumerate(shifts, 1):
            logging.info(f"Fetching data for week {idx}/{len(shifts)} for process {process_key}...")
            url = self.build_url(process_key, process_id, shift)
            try:
                response = requests.get(url, cookies=self.cookie_jar, verify=False, timeout=30)
                if response.status_code == 200:
                    logging.info(f"Data fetched successfully for week {idx} of process {process_key}.")
                    df = pd.read_csv(
                        StringIO(response.text),
                        delimiter=';',
                        encoding='ISO-8859-1',
                        on_bad_lines='skip'
                    )
                    if not df.empty:
                        process_df = pd.concat([process_df, df], ignore_index=True)
                        logging.debug(f"Appended data for week {idx} of process {process_key}.")
                    else:
                        logging.warning(f"Empty response for week {idx} of process {process_key}.")
                else:
                    logging.error(f"Failed to fetch data for week {idx} of process {process_key}: "
                                  f"Status Code {response.status_code}")
            except requests.exceptions.RequestException as e:
                logging.error(f"Request exception for process {process_key} week {idx}: {e}")

        return process_df

    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Cleans the raw DataFrame by removing extra quotes and delimiters.
        """
        logging.info("Cleaning data...")
        try:
            csv_data = df.to_csv(index=False)
            rows_clean = [
                row.replace('""', '"').strip('"').replace(',,,', '').replace(',,', '')
                for row in csv_data.splitlines()
            ]
            csv_clean = "\n".join(rows_clean)
            cleaned_df = pd.read_csv(StringIO(csv_clean), delimiter=',', header=0)
            logging.info("Data cleaned successfully.")
            return cleaned_df
        except Exception as e:
            logging.error(f"Error during data cleaning: {e}")
            return pd.DataFrame()

    def process_all_processes(self) -> None:
        """
        Fetches, cleans, and processes all PPR data concurrently.
        """
        max_workers = 4
        logging.info(f"Starting concurrent processing with {max_workers} workers...")

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_process = {
                executor.submit(self.handle_process, key, pid): key
                for key, pid in self.processes.items()
            }
            for future in as_completed(future_to_process):
                process_key = future_to_process[future]
                try:
                    future.result()
                    logging.info(f"Process {process_key} completed successfully.")
                except Exception as e:
                    logging.error(f"Process {process_key} generated an exception: {e}")

        self.execution_time = time.time() - self.start_time
        logging.info(f"Total execution time: {self.execution_time:.2f} seconds")

    def handle_process(self, key: str, pid: str) -> None:
        """
        Handles fetching, cleaning, and processing for a single process.
        """
        logging.info(f"Handling process: {key}")
        raw_df = self.fetch_process_data(key, pid)
        if raw_df.empty:
            logging.warning(f"No data fetched for process {key}. Skipping processing.")
            return

        cleaned_df = self.clean_data(raw_df)
        if cleaned_df.empty:
            logging.warning(f"Cleaned data is empty for process {key}. Skipping processing.")
            return

        # Find a specific method for the process, or use default
        process_method = self.get_process_method(key)
        if process_method:
            process_method(cleaned_df)
        else:
            self.process_default(cleaned_df, key)

        logging.info(f"Finished processing for process {key}.")

    def get_process_method(self, process_key: str) -> Optional[Any]:
        """
        Retrieves the processing method for a given process key if it exists.
        """
        method_name = f"process_{process_key}"
        return getattr(self, method_name, None)

    def save_json(self) -> None:
        """
        Saves the accumulated PPR_JSON data to a JSON file.
        """
        try:
            with open('PPR_result.json', 'w') as json_file:
                json.dump(self.PPR_JSON, json_file, indent=4)
            logging.info("PPR_JSON saved successfully.")
        except Exception as e:
            logging.error(f"Error saving PPR_JSON: {e}")

    def generic_process(self, df: pd.DataFrame, config: Dict[str, Any], process_key: str) -> None:
        """
        A generic method to process different PPR data based on the config rules.
        """
        try:
            logging.info(f"Calculating metrics for {process_key}...")
            process_data = {}

            # 1) Extract specified columns
            for col_name, col_idx in config.get("columns", {}).items():
                process_data[col_name] = df.iloc[:, col_idx].fillna('NaN').tolist()

            # 2) Calculate sums based on conditions
            for sum_key, sum_config in config.get("sums", {}).items():
                if "conditions" in sum_config:
                    condition = self.build_conditions(sum_config["conditions"], df)
                    total = df[condition].iloc[:, sum_config["column"]].sum()
                else:
                    cond_col_idx, cond_val = sum_config["condition"]
                    total = df[df.iloc[:, cond_col_idx] == cond_val].iloc[:, sum_config["column"]].sum()

                if "divide_by" in sum_config:
                    total /= sum_config["divide_by"]

                process_data[sum_key] = float(total)

            # 3) Update the shared dictionary
            self.PPR_JSON[process_key] = process_data
            logging.info(f"Metrics calculated for {process_key}.")

        except Exception as e:
            logging.error(f"Error processing {process_key}: {e}")

    def build_conditions(self, conditions: List[tuple], df: pd.DataFrame) -> pd.Series:
        """
        Builds a boolean mask for multiple conditions: (col_idx, expected_value).
        """
        mask = pd.Series([True] * len(df))
        for col_idx, expected in conditions:
            mask &= (df.iloc[:, col_idx] == expected)
        return mask

    def process_default(self, df: pd.DataFrame, process_key: str) -> None:
        """
        Fallback for processes with no dedicated method.
        """
        logging.info(f"Processing default data for {process_key}...")
        pru_config = self.process_config.get("PPR_PRU", {})
        if pru_config:
            self.generic_process(df, pru_config, "PPR_PRU")
        else:
            logging.error("Configuration for PPR_PRU not found.")

    # -------------------------------------------------------------------------
    # SPECIFIC PROCESSING METHODS
    # -------------------------------------------------------------------------
    def process_PPR_PRU(self, df: pd.DataFrame) -> None:
        config = self.process_config.get("PPR_PRU")
        if config:
            self.generic_process(df, config, "PPR_PRU")
        else:
            logging.error("Configuration for PPR_PRU not found.")

    def process_PPR_Case_Receive(self, df: pd.DataFrame) -> None:
        config = self.process_config.get("PPR_Case_Receive")
        if config:
            self.generic_process(df, config, "PPR_Case_Receive")
        else:
            logging.error("Configuration for PPR_Case_Receive not found.")

    def process_PPR_Cubiscan(self, df: pd.DataFrame) -> None:
        config = self.process_config.get("PPR_Cubiscan")
        if config:
            self.generic_process(df, config, "PPR_Cubiscan")
        else:
            logging.error("Configuration for PPR_Cubiscan not found.")

    def process_PPR_Each_Receive(self, df: pd.DataFrame) -> None:
        config = self.process_config.get("PPR_Each_Receive")
        if config:
            self.generic_process(df, config, "PPR_Each_Receive")
        else:
            logging.error("Configuration for PPR_Each_Receive not found.")

    def process_PPR_LP_Receive(self, df: pd.DataFrame) -> None:
        config = self.process_config.get("PPR_LP_Receive")
        if config:
            self.generic_process(df, config, "PPR_LP_Receive")
        else:
            logging.error("Configuration for PPR_LP_Receive not found.")

    def process_PPR_Pallet_Receive(self, df: pd.DataFrame) -> None:
        """
        Handles custom logic for PPR_Pallet_Receive. After the generic processing,
        we add a new metric 'MonoAsinUPP', which is the ratio:
            PalletPrEditorManual_TotalUnits / Pallet_Receive_TotalPallets
        """
        config = self.process_config.get("PPR_Pallet_Receive")
        if config:
            # 1) Perform the generic processing to populate metrics in PPR_JSON
            self.generic_process(df, config, "PPR_Pallet_Receive")

            # 2) Retrieve the dictionary for "PPR_Pallet_Receive"
            pallet_data = self.PPR_JSON.get("PPR_Pallet_Receive", {})

            # 3) Extract needed values (defaults to 0.0 if missing)
            pallet_pr_editor_manual_units = pallet_data.get("PalletPrEditorManual_TotalUnits", 0.0)
            pallet_receive_total_pallets = pallet_data.get("Pallet_Receive_TotalPallets", 0.0)

            # 4) Compute the new metric. Avoid division by zero if total pallets = 0.
            if pallet_receive_total_pallets != 0.0:
                mono_asin_upp = pallet_pr_editor_manual_units / pallet_receive_total_pallets
            else:
                mono_asin_upp = 0.0

            # 5) Store the new metric back into the dictionary
            pallet_data["MonoAsinUPP"] = mono_asin_upp

            # 6) Save it back to self.PPR_JSON
            self.PPR_JSON["PPR_Pallet_Receive"] = pallet_data

            logging.info(
                f"Added MonoAsinUPP metric to PPR_Pallet_Receive: {mono_asin_upp:.2f}"
            )
        else:
            logging.error("Configuration for PPR_Pallet_Receive not found.")


    def process_PPR_Prep_Recorder(self, df: pd.DataFrame) -> None:
        config = self.process_config.get("PPR_Prep_Recorder")
        if config:
            self.generic_process(df, config, "PPR_Prep_Recorder")
            prep_data = self.PPR_JSON.get("PPR_Prep_Recorder", {})
            item_prepped_units = prep_data.get("ItemPrepped_TotalUnits", 0.0)
            item_prepped_hours = prep_data.get("ItemPrepped_TotalHours", 0.0)

            # Compute extra rate
            if item_prepped_hours != 0:
                prep_data["ItemPrepped_Rate"] = item_prepped_units / item_prepped_hours
            else:
                prep_data["ItemPrepped_Rate"] = 0.0

            self.PPR_JSON["PPR_Prep_Recorder"] = prep_data
        else:
            logging.error("Configuration for PPR_Prep_Recorder not found.")

    def process_PPR_RC_Presort(self, df: pd.DataFrame) -> None:
        config = self.process_config.get("PPR_RC_Presort")
        if config:
            self.generic_process(df, config, "PPR_RC_Presort")
        else:
            logging.error("Configuration for PPR_RC_Presort not found.")

    def process_PPR_RC_Sort(self, df: pd.DataFrame) -> None:
        config = self.process_config.get("PPR_RC_Sort")
        if config:
            self.generic_process(df, config, "PPR_RC_Sort")
        else:
            logging.error("Configuration for PPR_RC_Sort not found.")

    def process_PPR_Receive_Dock(self, df: pd.DataFrame) -> None:
        logging.info("No calculations needed for Receive Dock.")
        self.PPR_JSON["PPR_Receive_Dock"] = "No data required"

    def process_PPR_Receive_Support(self, df: pd.DataFrame) -> None:
        config = self.process_config.get("PPR_Receive_Support")
        if config:
            self.generic_process(df, config, "PPR_Receive_Support")
        else:
            logging.error("Configuration for PPR_Receive_Support not found.")

    def process_PPR_Transfer_Out(self, df: pd.DataFrame) -> None:
        config = self.process_config.get("PPR_Transfer_Out")
        if config:
            self.generic_process(df, config, "PPR_Transfer_Out")
        else:
            logging.error("Configuration for PPR_Transfer_Out not found.")

    def process_PPR_Transfer_Out_Dock(self, df: pd.DataFrame) -> None:
        config = self.process_config.get("PPR_Transfer_Out_Dock")
        if config:
            self.generic_process(df, config, "PPR_Transfer_Out_Dock")
        else:
            logging.error("Configuration for PPR_Transfer_Out_Dock not found.")

    # Note: user also has a second definition for PPR_Case_Receive 
    # to ensure PPR_JSON["PPR_Case_Receive"] is always present. 
    def process_PPR_Case_Receive(self, df: pd.DataFrame) -> None:
        self.PPR_JSON["PPR_Case_Receive"] = {}
        config = self.process_config.get("PPR_Case_Receive")
        if config:
            self.generic_process(df, config, "PPR_Case_Receive")
        else:
            logging.error("Configuration for PPR_Case_Receive not found.")

    def run(self) -> Dict[str, Any]:
        """
        Executes the entire PPR processing workflow.
        """
        logging.info('Starting PPR processing...')
        self.process_all_processes()
        logging.info('PPR processing completed.')
        return self.PPR_JSON


def PPRfunction(Site: str, SOSdatetime: datetime, EOSdatetime: datetime) -> Dict[str, Any]:
    """
    Interface function to execute PPR processing.
    """
    processor = PPRProcessor(Site, SOSdatetime, EOSdatetime)
    return processor.run()


# Example usage:
# if __name__ == "__main__":
#     Site = "ZAZ1"
#     SOSdatetime = datetime(2024, 11, 15, 6, 0, 0)
#     EOSdatetime = datetime(2024, 11, 15, 14, 30, 0)
#     result = PPRfunction(Site, SOSdatetime, EOSdatetime)
#     print(json.dumps(result, indent=4))
