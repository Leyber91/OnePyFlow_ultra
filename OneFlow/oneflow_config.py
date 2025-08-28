# oneflow_config.py
import logging
import os
import sys
from utils.shared_resources import FC_TO_COUNTRY  
import tempfile

# Configure logging to both console and file
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(), logging.FileHandler("data_collection.log")]
)
logger = logging.getLogger(__name__)

# Module order list
MODULE_ORDER = [
    "Echo",      # Debugging module that doesn't require authentication
    "PHC",       # Predicted Headcount module 
    "HCTool",    # Actual Headcount module
    "BackLog",   # Backlog and arrivals data module
    "CarrierMatrix", # Carrier Matrix data for FlexSim
    "IBBT",
    "SCACs",     # SCACs Mapping data for FlexSim
    "SPARK",     # SPARK snapshot data for FlexSim
    "KARIBA",    # Kariba-TSI picked units module
    "DockMaster",
    "DockMasterFiltered",
    "DockMaster2",
    "DockMaster2Filtered",
    "DockFlow",
    "Galaxy",
    "Galaxy_percentages",
    "Galaxy2",
    "Galaxy2_values",
    "ICQA",
    "F2P",
    "kNekro",
    "SSP",
    "SSPOT",
    "PPR",
    "PPR_Q",
    "ALPS",
    "ALPS_RC_Sort",
    "ALPSRoster",
    "RODEO",
    "YMS",       # Now uses API implementation for better performance
    "FMC",
    "QuipCSV"
]

# List of modules that can be run standalone without Midway authentication
STANDALONE_MODULES = [
    "Echo",
    "PHC",
    "HCTool",
    "BackLog",
    "CarrierMatrix",
    "KARIBA",
    "SCACs",
    "SPARK",  # Added SPARK as standalone module
    "VIP",
    "IBBT",
    "PPR_Q"  # Added PPR_Q as standalone module
]

# Function to get base directory
def get_base_dir():
    """
    Returns the directory where the executable is located or where the script is running from.
    Handles both C: and D: drive scenarios.
    """
    try:
        if getattr(sys, 'frozen', False):
            # The application is frozen (packaged)
            base_dir = os.path.dirname(sys.executable)
        else:
            # The application is running as a normal Python script
            # Go up one directory level from the module's directory
            current_dir = os.path.dirname(os.path.abspath(__file__))
            base_dir = os.path.dirname(current_dir)  # Go up one level
            
        # Verify we can write to this directory
        test_path = os.path.join(base_dir, 'test_write_permission.tmp')
        try:
            with open(test_path, 'w') as f:
                f.write('test')
            os.remove(test_path)
            logger.info(f"Using base directory with write permission: {base_dir}")
        except Exception as e:
            logger.warning(f"Base directory not writable: {e}")
            # Fall back to a directory we can write to
            base_dir = tempfile.gettempdir()
            logger.info(f"Falling back to system temp directory: {base_dir}")
            
        return base_dir
    except Exception as e:
        logger.error(f"Error determining base directory: {e}")
        # Last resort: use system temp directory
        return tempfile.gettempdir()

# Use the base_dir to create JSON output directory
JSON_OUTPUT_DIR = os.path.join(get_base_dir(), 'json_outputs')
os.makedirs(JSON_OUTPUT_DIR, exist_ok=True)
logger.info(f"JSON output directory: {JSON_OUTPUT_DIR}")

# Updated CSV Output Directory to the correct path
CSV_OUTPUT_DIR = r'\\ant\dept-eu\BCN1\ECFT\IXD\08.Files\OnePyFlow\Outputs\Exec_time'

# Define both legacy and new CSV filenames
SCRIPT_MODE = 'compiled' if getattr(sys, 'frozen', False) else 'script'
LEGACY_CSV_FILENAME = 'compiled_execTime.csv' if SCRIPT_MODE == 'compiled' else 'script_execTime.csv'
DETAILED_CSV_FILENAME = 'module_performance_metrics.csv'