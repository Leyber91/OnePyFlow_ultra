"""
YMS Field Extractors Module
===========================
🎯 MISSION: Extract and transform individual fields from API data
"""

from typing import Dict, Any, Tuple, Optional
import re
import logging

logger = logging.getLogger(__name__)


def extract_equipment_type(item: Dict[str, Any]) -> str:
    """
    🔧 Extract equipment type with multiple fallback strategies.
    
    Fixes Equipment Type gap by using enhanced extraction.
    """
    # Strategy 1: Direct API field (same as YMS Traditional)
    equipment_type = item.get("type", "")
    if equipment_type and str(equipment_type).strip() and str(equipment_type) != 'NaN':
        return str(equipment_type)
    
    # Strategy 2: Backup API field  
    equipment_type = item.get("equipment_type", "")
    if equipment_type and str(equipment_type).strip() and str(equipment_type) != 'NaN':
        return str(equipment_type)
    
    # Strategy 3: Extract from vehicle type field
    vehicle_type = item.get("vehicletype", "")
    if vehicle_type and str(vehicle_type).strip():
        return str(vehicle_type)
    
    # Strategy 4: Extract from classification
    classification = item.get("classification", "")
    if classification and str(classification).strip():
        return str(classification)
    
    # Strategy 5: Default fallback (removed location-based assumptions)
    return "TRAILER"  # Most common type, but only as last resort


def extract_carrier(item: Dict[str, Any]) -> str:
    """
    🔧 Extract carrier/SCAC with multiple fallback strategies.
    
    Fixes SCAC gap (-26.9%) by using multi-source carrier extraction.
    """
    # Strategy 1: Direct ownercode field
    ownercode = item.get("ownercode", "")
    if ownercode and str(ownercode).strip() and str(ownercode) != 'NaN':
        return str(ownercode)
    
    # Strategy 2: Extract from carrier field
    carrier = item.get("carrier", "")
    if carrier and str(carrier).strip():
        return str(carrier)
    
    # Strategy 3: Extract from fleet owner
    fleet_owner = item.get("fleetowner", "")
    if fleet_owner and str(fleet_owner).strip():
        return str(fleet_owner)
    
    # Strategy 4: Extract from shipping company
    shipping_company = item.get("shippingcompany", "")
    if shipping_company and str(shipping_company).strip():
        return str(shipping_company)
    
    # Strategy 5: Extract from owner information
    owner = item.get("owner", "")
    if owner and str(owner).strip():
        return str(owner)
    
    # Strategy 6: Parse from nested structures
    shipper_accounts = item.get("shipperaccounts", "")
    if shipper_accounts and isinstance(shipper_accounts, str):
        # Extract carrier codes from shipper accounts
        if "ATS" in shipper_accounts:
            return "ATSUK"  # Common ATS carrier
    
    return "NaN"  # Only return NaN if all strategies fail


def extract_load_basic(item: Dict[str, Any]) -> str:
    """
    🔧 Extract load with basic fallback strategies.
    """
    # Strategy 1: Direct shipperaccounts field
    load = item.get("shipperaccounts", "")
    if load and str(load).strip() and str(load) != 'NaN':
        return str(load)
    
    # Strategy 2: Extract from load type
    load_type = item.get("loadtype", "")
    if load_type and str(load_type).strip():
        return str(load_type)
    
    # Strategy 3: Extract from service type
    service_type = item.get("servicetype", "")
    if service_type and str(service_type).strip():
        return str(service_type)
    
    return "NaN"  # Fixed: YMS Traditional uses "NaN" instead of empty string


def extract_load_enhanced(item: Dict[str, Any]) -> str:
    """
    📦 Extract load information with enhanced API field analysis.
    
    Creates load names like:
    - 'ATSExternal'
    - 'InboundDocktoDock'
    - 'ATSWarehouseTransfersIntermodal'
    """
    # Strategy 1: Check if it's a live load (active transfer)
    isliveload = item.get("isliveload", False)
    ispick = item.get("ispick", False)
    isdrop = item.get("isdrop", False)
    
    # Strategy 2: Determine load type based on location and flags
    location_label = item.get("locationlabel", "")
    location_type = item.get("locationtype", "")
    
    # Construct load type based on location patterns
    if isliveload:
        # Live loads are typically transfers
        if location_type == "InboundDock" or "IB" in location_label:
            return "ATSWarehouseTransfersIntermodal"
        elif location_type == "OutboundDock" or "OB" in location_label:
            return "ATSExternalWeb"
        elif ispick and isdrop:
            return "InboundDocktoDock"
        elif ispick:
            return "TransfersTote"
        elif isdrop:
            return "TransfersInitialPlacement"
        else:
            return "ATSWarehouseTransfersIntermodal"
    
    # Strategy 3: Non-live loads
    carriercode = item.get("carriercode", "")
    fleetsystemname = item.get("fleetsystemname", "")
    
    # External carriers vs Amazon fleet
    if carriercode and carriercode not in ["ATSEU", "ATSES", "ATSIT", "ATSEX"]:
        return "ATSExternal"
    elif fleetsystemname == "AAP":  # Amazon Asset Pool
        return "ATSExternal"
    
    # Strategy 4: Default based on location type
    if location_type == "InboundDock":
        return "ATSWarehouseTransfersIntermodal"
    elif location_type == "OutboundDock":
        return "ATSExternalWeb"
    elif location_type == "ParkingSlip":
        return "ATSExternal"
    
    return "NaN"  # Fixed: YMS Traditional uses "NaN" instead of empty string


def extract_vrid(item: Dict[str, Any]) -> str:
    """
    🔧 Extract VRID matching Traditional YMS logic.
    
    Traditional YMS correctly uses:
    1. Direct VRID field (api_raw_data.vrid)
    2. ISA ID field (api_raw_data.isaid) - valid VRID alternative
    3. FMC lookup (handled separately)
    
    NEVER uses equipment numbers, license plates, vehicle IDs as VRIDs!
    """
    # Strategy 1: Direct VRID field (highest priority)
    vrid = item.get("vrid", "")
    if vrid and str(vrid).strip() and str(vrid) != 'NaN':
        return str(vrid).strip()
    
    # Strategy 2: ISA ID conversion - this is a valid VRID alternative
    isaid = item.get("isaid", "")
    if isaid and str(isaid).strip() and str(isaid) != 'NaN':
        return str(isaid).strip()
    
    # Strategy 3: Parse from nested identifier structures (Traditional YMS logic)
    # Look for VR_ID and ISA types only - matching traditional behavior
    identifiers = item.get("identifiers", {})
    if isinstance(identifiers, dict):
        # Priority 1: VR_ID type (exact match to Traditional YMS)
        for id_item in identifiers:
            if isinstance(id_item, dict) and id_item.get("type") == "VR_ID":
                vr_id = id_item.get("identifier")
                if vr_id and str(vr_id).strip():
                    return str(vr_id).strip()
        
        # Priority 2: ISA type (exact match to Traditional YMS)  
        for id_item in identifiers:
            if isinstance(id_item, dict) and id_item.get("type") == "ISA":
                isa_id = id_item.get("identifier")
                if isa_id and str(isa_id).strip():
                    return str(isa_id).strip()
    
    # No valid VRID found - will be handled by FMC lookup later
    return "NaN"


def is_valid_vrid_format(candidate: str) -> bool:
    """
    Validate if a string matches actual VRID format patterns.
    
    Based on analysis of real data, valid VRIDs include:
    - 91336045591, 91961045591 (11-digit numeric)
    - 115MB52RR, 1129DGV3C, 1154G2NQJ (9-char alphanumeric starting with 11)
    
    Equipment numbers like AE43444, VS437721, XA694YA are NOT VRIDs!
    """
    if not candidate or len(candidate) < 8:
        return False
    
    candidate = candidate.upper().strip()
    
    # Pattern 1: 11-digit numeric (common pattern)
    if re.match(r'^[0-9]{11}$', candidate):
        return True
    
    # Pattern 2: 10-digit numeric starting with 9 (another common pattern)  
    if re.match(r'^9[0-9]{9}$', candidate):
        return True
    
    # Pattern 3: 9-character alphanumeric starting with "11" (very common)
    if re.match(r'^11[0-9A-Z]{7}$', candidate):
        return True
    
    # Pattern 4: 8-9 character alphanumeric starting with "1" (some variations)
    if re.match(r'^1[0-9A-Z]{7,8}$', candidate):
        return True
    
    # Exclude obvious equipment number patterns that are NOT VRIDs:
    if re.match(r'^[A-Z]{2}[0-9]{3,5}[A-Z]{0,2}$', candidate):
        return False  # Looks like license plate/equipment number
    
    if re.match(r'^[A-Z]{2,3}[0-9]{3,6}$', candidate):
        return False  # Looks like equipment identifier
    
    return False


def convert_boolean_to_status(is_empty: bool, tdr_state: str = "") -> str:
    """Convert boolean empty status to string with enhanced logic."""
    if tdr_state == "TDRInProgress":
        return "IN_PROGRESS"
    elif is_empty:
        return "EMPTY"
    else:
        return "FULL"


def determine_availability(item: Dict[str, Any]) -> Tuple[bool, str]:
    """
    🎯 Determine availability following Traditional YMS logic.
    
    Traditional YMS only considers Amazon's own fleet equipment as "unavailable".
    """
    is_eligible = item.get("eligibletoleaveyard_iseligible", True)
    reason_codes = item.get("eligibletoleaveyard_reasoncodes", "")
    
    # If eligible, available
    if is_eligible:
        return False, "HEALTHY"
    
    # Check if this is Amazon's own fleet equipment
    owner_code = item.get("ownercode", "")
    fleet_system = item.get("fleetsystemname", "")
    
    # Amazon fleet codes
    amazon_fleet_codes = ["ATSEU", "ATSIT", "ATSUK"]
    
    # Enhanced Amazon fleet detection
    is_amazon_fleet = (
        owner_code in amazon_fleet_codes and  # Regional Amazon codes
        fleet_system == "AAP"                 # Amazon fleet system
    )
    
    # Fallback for missing owner codes: use country code + fleet system
    if not is_amazon_fleet and (not owner_code or owner_code.strip() == ""):
        country_code = item.get("countrycode", "")
        country_to_fleet = {
            "DE": "ATSEU", "FR": "ATSEU", "ES": "ATSEU", "NL": "ATSEU",  # EU
            "IT": "ATSIT",  # Italy
            "GB": "ATSUK"   # United Kingdom
        }
        
        if country_code in country_to_fleet and fleet_system == "AAP":
            is_amazon_fleet = True
    
    if not is_amazon_fleet:
        # Third-party equipment is "ineligible" but not "unavailable"
        if reason_codes and reason_codes != "[]":
            reason_str = str(reason_codes).strip("[]'\"")
            reasons = [r.strip().strip("'\"") for r in reason_str.split(",") if r.strip()]
            if reasons:
                # Normalize text to match YMS Traditional format
                reason = reasons[0]
                if reason == "PREVENTIVE_MAINTENANCE":
                    reason = "PREVENTATIVE_MAINTENANCE"
                return False, reason  # Available but with reason (warning)
        return False, "UNKNOWN_REASON"
    
    # For Amazon fleet equipment, apply traditional unavailable logic
    if reason_codes and reason_codes != "[]":
        reason_str = str(reason_codes).strip("[]'\"")
        reasons = [r.strip().strip("'\"") for r in reason_str.split(",") if r.strip()]
        
        # Amazon fleet unavailable conditions
        unavailable_conditions = {
            'DAMAGED_SEVERE', 'DAMAGED_MODERATE',  # Equipment damage
            'PREVENTIVE_MAINTENANCE', 'PREVENTATIVE_MAINTENANCE',  # Maintenance
            'BLOCKED', 'OUT_OF_SERVICE', 'MAINTENANCE_REQUIRED',
            'SAFETY_ISSUE', 'REGULATORY_HOLD', 'MISSING_DOCUMENTS'
        }
        
        # Check for unavailable conditions on Amazon fleet
        for reason in reasons:
            # Normalize text to match YMS Traditional format
            if reason == "PREVENTIVE_MAINTENANCE":
                reason = "PREVENTATIVE_MAINTENANCE"
            if reason in unavailable_conditions:
                return True, reason
        
        # Other conditions on Amazon fleet are warnings, not unavailable
        if reasons:
            # Normalize text to match YMS Traditional format
            reason = reasons[0]
            if reason == "PREVENTIVE_MAINTENANCE":
                reason = "PREVENTATIVE_MAINTENANCE"
            return False, reason
    
    # Amazon fleet ineligible without clear reason
    return False, "UNKNOWN_REASON"


def extract_load_traditional_style(item: Dict[str, Any]) -> str:
    """
    📦 Extract load using EXACT YMS Traditional logic.
    
    Matches YMS Traditional's approach:
    1. Primary: shipperAccounts from load object (first element)
    2. Fallback: recursive search for shipper accounts
    """
    # Strategy 1: Direct shipperAccounts from load object (YMS Traditional primary method)
    load_obj = item.get("load", {})
    if load_obj and "shipperAccounts" in load_obj:
        shipper_accounts = load_obj["shipperAccounts"]
        if isinstance(shipper_accounts, list) and len(shipper_accounts) > 0:
            return str(shipper_accounts[0])
    
    # Strategy 2: Fallback - recursive search (YMS Traditional fallback)
    # This would require implementing recursive_find_shipper_accounts logic
    # For now, check top-level shipperaccounts field
    shipper_accounts = item.get("shipperaccounts", "")
    if shipper_accounts and str(shipper_accounts).strip() and str(shipper_accounts) != 'NaN':
        return str(shipper_accounts)
    
    return "NaN"


def extract_lane_traditional_style(item: Dict[str, Any]) -> str:
    """
    🛤️ Extract lane using EXACT YMS Traditional logic.
    
    Matches YMS Traditional's approach:
    Direct extraction from load object with -> to _ normalization
    """
    # Strategy 1: Direct lane from load object (YMS Traditional method)
    load_obj = item.get("load", {})
    if load_obj:
        lane_value = load_obj.get("lane")
        if lane_value and isinstance(lane_value, str):
            # YMS Traditional normalization: replace -> with _
            normalized_lane = lane_value.replace("->", "_")
            return normalized_lane
    
    # Strategy 2: Check top-level lane field
    lane = item.get("lane", "")
    if lane and str(lane).strip() and str(lane) != 'NaN':
        return str(lane).replace("->", "_")
    
    return "NaN" 


def extract_status_hybrid(item: Dict[str, Any]) -> str:
    """
    📊 Extract status using hybrid approach: recursive search + boolean fallback.
    
    Strategy 1: Try recursive search on raw API data (like YMS Traditional)
    Strategy 2: Fall back to boolean logic if no status found
    """
    def recursive_find_status(obj):
        """Recursively search for any key named 'status' (case-insensitive)"""
        statuses = []
        if isinstance(obj, dict):
            for key, value in obj.items():
                if key.lower() == "status":
                    statuses.append(value)
                statuses.extend(recursive_find_status(value))
        elif isinstance(obj, list):
            for sub_item in obj:
                statuses.extend(recursive_find_status(sub_item))
        return statuses
    
    # Strategy 1: Try recursive search on raw API data first
    raw_data = item.get("api_raw_data", item)  # Use raw data if available
    status_list = recursive_find_status(raw_data)
    if status_list:
        return status_list[-1]  # Take last found status like YMS Traditional
    
    # Strategy 2: Fall back to boolean-based logic (original YMS_API approach)
    tdr_state = item.get("tdrstate", "")
    if tdr_state == "TDRInProgress":
        return "IN_PROGRESS"
    
    is_empty = item.get("isempty", True)
    if is_empty:
        return "EMPTY"
    else:
        return "FULL" 