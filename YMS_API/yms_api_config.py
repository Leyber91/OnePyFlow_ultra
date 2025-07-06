"""
YMS API Configuration and Mappings
==================================
Central configuration for YMS API operations.
"""

from typing import Dict, List, Set
import re


# ============================================================================
# SITE AND EXTERNAL YARD CONFIGURATION
# ============================================================================

# External yard links (sites with secondary yards)
EXTERNAL_LINKS = {
    "DTM1": "VEEY",
    "DTM2": "VEEY",
    "HAJ1": "SHRT-HAJ1-1", 
    "WRO5": "YWRO"
}


# ============================================================================
# LOAD TYPE CONFIGURATION
# ============================================================================

# Standard load type classifications
STANDARD_LOAD_TYPES = [
    'TransfersTote',
    'ATSWarehouseTransfersIntermodal',
    'TransfersInitialPlacement',
    'ATSSeaWarehouseTransfersGround',
    'ATSWarehouseTransfersGround'
]

# Load type mapping patterns for fuzzy matching
LOAD_TYPE_PATTERNS = {
    'TransfersTote': {
        'TOTE', 'TRANSFER_TOTE', 'TOTES', 'TRANSFER TOTE',
        'TOTE_TRANSFER', 'CROSS_DOCK_TOTE'
    },
    'ATSWarehouseTransfersIntermodal': {
        'ATS', 'INTERMODAL', 'WAREHOUSE_TRANSFER', 'WHT',
        'ATS_INTERMODAL', 'WAREHOUSE TRANSFER', 'WH_TRANSFER',
        'INTERMODAL_TRANSFER', 'ATS_WAREHOUSE'
    },
    'TransfersInitialPlacement': {
        'INITIAL', 'PLACEMENT', 'NEW_ARRIVAL', 'INITIAL_PLACEMENT',
        'FIRST_PLACEMENT', 'NEW ARRIVAL', 'INITIAL PLACEMENT',
        'IP', 'INITIAL_DROP'
    },
    'ATSSeaWarehouseTransfersGround': {
        'SEA', 'GROUND', 'OCEAN', 'MARITIME', 'SEA_GROUND',
        'OCEAN_GROUND', 'MARITIME_TRANSFER', 'SEA GROUND',
        'PORT_TRANSFER'
    },
    'ATSWarehouseTransfersGround': {
        'GROUND_TRANSFER', 'ROAD', 'TRUCK_TRANSFER', 'GROUND',
        'ROAD_TRANSFER', 'TRUCK', 'GROUND TRANSFER'
    }
}


# ============================================================================
# LANE AND STATUS CONFIGURATION
# ============================================================================

# Lane pattern recognition for categorization
LANE_PATTERNS = {
    'inbound': ['_IN', 'INBOUND', 'IB_', 'ARRIVAL'],
    'outbound': ['_OUT', 'OUTBOUND', 'OB_', 'DEPARTURE'],
    'transfer': ['TRANSFER', 'XFER', '_TO_', 'RELAY'],
    'cross_dock': ['XDOCK', 'CROSS_DOCK', 'CD_', 'CROSSDOCK']
}

# Status indicators for IN_PROGRESS detection
IN_PROGRESS_INDICATORS = {
    'dock_operations': [
        'LOADING', 'UNLOADING', 'PROCESSING', 'IN_OPERATION',
        'DOCKING', 'UNDOCKING', 'ACTIVE', 'IN_PROGRESS'
    ],
    'unavailable_reasons': [
        'Loading in progress', 'Unloading', 'Processing',
        'Dock operation', 'Active operation', 'In transit'
    ]
}


# ============================================================================
# EQUIPMENT AND CARRIER CONFIGURATION
# ============================================================================

# Equipment type mappings (API value -> Standard value)
EQUIPMENT_TYPE_MAPPING = {
    'TRAILER': 'TRAILER',
    'TRAILER_SOFT': 'TRAILER_SOFT',
    'TRAILER_REFRIGERATED': 'TRAILER_REFRIGERATED',
    'CONTAINER': 'CONTAINER',
    'PERSON': 'PERSON',
    'VEHICLE': 'VEHICLE',
    'UNKNOWN': 'UNKNOWN'
}

# SCAC validation patterns
VALID_SCAC_PATTERNS = {
    'standard': re.compile(r'^[A-Z]{4}$'),  # Standard 4-letter SCAC
    'numeric': re.compile(r'^[A-Z]{3}[0-9]$'),  # 3 letters + 1 number
    'extended': re.compile(r'^[A-Z]{2,4}[0-9]{0,2}$')  # Extended format
}

# Amazon fleet carrier codes by region
AMAZON_FLEET_CODES = {
    'ATSEU',  # European Union
    'ATSIT',  # Italy
    'ATSUK',  # United Kingdom
    'ATSES',  # Spain
    'ATSEX'   # External/Generic
}


# ============================================================================
# DEFAULT VALUES AND THRESHOLDS
# ============================================================================

# Default values for empty fields
DEFAULT_VALUES = {
    'lane': 'NaN',
    'load': 'NaN',
    'vrid': 'NaN',
    'unavailableReason': 'NaN',
    'scac': 'UNKNOWN'
}

# Quality thresholds for assessment
QUALITY_THRESHOLDS = {
    'excellent': 95,    # >= 95% is excellent
    'good': 85,         # >= 85% is good
    'acceptable': 70,   # >= 70% is acceptable
    'poor': 0           # < 70% is poor
}


# ============================================================================
# FMC CONFIGURATION
# ============================================================================

# FMC data configuration
FMC_CONFIG = {
    'default_days_back': 7,
    'max_days_back': 30,
    'required_columns': ['VR ID', 'Equipment ID', 'Lane', 'Load Type', 'Date'],
    'date_formats': ['%Y-%m-%d', '%Y-%m-%d %H:%M:%S', '%m/%d/%Y']
}


# ============================================================================
# API FIELD MAPPINGS
# ============================================================================

# API field mappings (API field -> Internal field)
API_FIELD_MAPPINGS = {
    # Location fields
    'location': 'name',
    'locationName': 'name',
    'parkingSpot': 'name',
    
    # Equipment fields
    'equipmentType': 'equipment_type',
    'trailerType': 'equipment_type',
    
    # Carrier fields
    'carrierCode': 'ownercode',
    'scac': 'ownercode',
    'carrier': 'ownercode',
    
    # VRID fields
    'visitReasonId': 'vrid',
    'visitReason': 'vrid',
    'isaNumber': 'vrid',
    
    # Status fields
    'containerStatus': 'isempty',
    'status': 'isempty',
    'loadStatus': 'isempty',
    
    # Availability fields
    'isAvailable': 'available',
    'available': 'available',
    'unavailableFlag': 'unavailable',
    'blockedFlag': 'unavailable',
    'unavailReason': 'unavailableReason',
    'blockReason': 'unavailableReason',
    
    # Operational fields
    'dockDoor': 'dock_door',
    'doorNumber': 'dock_door',
    'operationStartTime': 'operation_start',
    'operationEndTime': 'operation_end',
    
    # Flags and restrictions
    'hasYellowMark': 'has_yellow_mark',
    'yellowFlag': 'has_yellow_mark',
    'operationalRestriction': 'operational_restriction',
    'maintenanceFlag': 'maintenance_flag',
    'onHold': 'on_hold',
    'blocked': 'blocked'
}


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def is_amazon_fleet_code(carrier_code: str) -> bool:
    """Check if a carrier code belongs to Amazon fleet."""
    return carrier_code in AMAZON_FLEET_CODES


def validate_scac_format(scac: str) -> bool:
    """Validate SCAC format against known patterns."""
    return any(pattern.match(scac) for pattern in VALID_SCAC_PATTERNS.values())


def get_load_type_category(load_string: str) -> str:
    """Get the standard load type category for a load string."""
    load_upper = load_string.upper()
    
    for category, patterns in LOAD_TYPE_PATTERNS.items():
        if any(pattern in load_upper for pattern in patterns):
            return category
    
    return 'Unknown'


def get_quality_grade(percentage: float) -> str:
    """Get quality grade based on percentage."""
    if percentage >= QUALITY_THRESHOLDS['excellent']:
        return 'Excellent'
    elif percentage >= QUALITY_THRESHOLDS['good']:
        return 'Good'
    elif percentage >= QUALITY_THRESHOLDS['acceptable']:
        return 'Acceptable'
    else:
        return 'Poor'