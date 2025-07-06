"""
YMS Business Name Mapping Module
===============================
🎯 MISSION: Manage carrier code to business name mappings for lane field enhancement
⚠️  FIXED: Removed synthetic lane creation that caused ZAZ1/CDG7 inconsistencies
"""

from typing import Dict, Tuple, Any
import logging

logger = logging.getLogger(__name__)

# 🎯 BUSINESS NAME MAPPING - Discovered from Lane Analysis
# Maps API carrier codes to business names that YMS Old extracts via web scraping
# ⚠️  WARNING: These mappings should NOT be used to create synthetic lanes
# ✅ PRINCIPLE: Only use for validation/enhancement when we have REAL lane data
CARRIER_BUSINESS_MAPPING = {
    # Format: (carriercode, subcarriercode): "business_name"
    
    # Original discovered mappings ✅ CONFIRMED WORKING (for validation only)
    ("ACCCF", ""): "SHAOKE",
    ("ABGDI", ""): "VITAKRAF", 
    ("AAGQB", ""): "HIPPOCAM",
    ("APZXD", "ATSEU"): "SKECHERS",
    ("AAGQB", "ATSEU"): "HIPPOCAM",
    ("ABGDI", "ATSEU"): "VITAKRAF",
    ("ACCCF", "ATSEU"): "SHAOKE",
    
    # New mappings discovered from analysis 🔍 ANALYSIS RESULTS (for validation only)
    ("ABJGB", "ATSEU"): "BIG",
    ("ARIAK", "ATSEU"): "BIG",
    
    # Missing business names from analysis 🎯 TARGETED ADDITIONS
    # These were found in OLD but missing from API - need to reverse engineer
    # TODO: Need to find the actual carrier codes for these business names:
    # - MXP6, BVA1, SOLUTION, FRA7
}


def get_business_name_for_carrier(carriercode: str, subcarriercode: str = "") -> str:
    """
    Get business name for a carrier code combination.
    
    ⚠️  NOTE: This should only be used for validation, not for creating synthetic lanes!
    
    Args:
        carriercode: Primary carrier code
        subcarriercode: Secondary carrier code (optional)
        
    Returns:
        Business name if mapping exists, empty string otherwise
    """
    mapping_key = (carriercode, subcarriercode if subcarriercode else "")
    return CARRIER_BUSINESS_MAPPING.get(mapping_key, "")


def extract_lane_with_business_mapping(item: Dict[str, Any]) -> str:
    """
    🛤️ Extract lane information WITHOUT creating synthetic data.
    
    🎯 FIXED PRINCIPLE: "Never create synthetic lanes - preserve data integrity"
    
    ⚠️  PREVIOUS ISSUE: This function was creating synthetic lanes like "VITAKRAF_ZAZ1"
        that didn't match real operational data, causing:
        - ZAZ1: 73% of lanes were synthetic/wrong
        - CDG7: API showed honest NaN values
        - Result: ZAZ1 appeared "complete" but was less accurate than CDG7
    
    ✅ NEW APPROACH: 
        - Return "NaN" for missing lane data (honest gaps)
        - Let FMC enhancement provide real lane data where available
        - No synthetic lane creation from carrier codes + site combinations
    
    Args:
        item: API item dictionary
        
    Returns:
        Always returns "NaN" to preserve data integrity
    """
    # 🚫 REMOVED: All synthetic lane creation logic
    # The following strategies created synthetic data and are now removed:
    # 
    # OLD CODE (REMOVED):
    # business_name = get_business_name_for_carrier(carriercode, subcarriercode)
    # if business_name:
    #     return f"{business_name}_{loadbuildingcode}"  # ❌ SYNTHETIC DATA
    #     return f"{business_name}_CDG7"                # ❌ SYNTHETIC DATA
    # 
    # These created synthetic lanes that didn't match YMS Traditional real data.
    
    # ✅ NEW APPROACH: Preserve data integrity - no synthetic lanes
    # Return "NaN" to allow FMC enhancement to provide real lane data
    # This makes all sites behave consistently and honestly about data gaps
    return "NaN"


def validate_lane_with_business_mapping(lane: str, carriercode: str, subcarriercode: str = "") -> bool:
    """
    Validate if a lane matches expected business mapping pattern.
    
    ✅ NEW FUNCTION: For validation only, not for creating synthetic data
    
    Args:
        lane: Lane to validate
        carriercode: Primary carrier code
        subcarriercode: Secondary carrier code (optional)
        
    Returns:
        True if lane matches expected business name pattern
    """
    if not lane or lane == "NaN":
        return False
        
    business_name = get_business_name_for_carrier(carriercode, subcarriercode)
    if not business_name:
        return False
        
    # Check if lane contains the business name (validation)
    return business_name.lower() in lane.lower()


def add_business_mapping(carriercode: str, subcarriercode: str, business_name: str) -> None:
    """
    Add a new business name mapping.
    
    Args:
        carriercode: Primary carrier code
        subcarriercode: Secondary carrier code
        business_name: Business name to map to
    """
    mapping_key = (carriercode, subcarriercode if subcarriercode else "")
    CARRIER_BUSINESS_MAPPING[mapping_key] = business_name
    logger.info(f"Added business mapping: {mapping_key} -> {business_name}")


def get_all_business_mappings() -> Dict[Tuple[str, str], str]:
    """Get all current business name mappings."""
    return CARRIER_BUSINESS_MAPPING.copy()


def get_mapping_statistics() -> Dict[str, Any]:
    """Get statistics about current mappings."""
    total_mappings = len(CARRIER_BUSINESS_MAPPING)
    business_names = set(CARRIER_BUSINESS_MAPPING.values())
    
    return {
        "total_mappings": total_mappings,
        "unique_business_names": len(business_names),
        "business_names": sorted(business_names)
    } 