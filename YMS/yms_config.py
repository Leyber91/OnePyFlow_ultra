# yms_config.py
import logging

logger = logging.getLogger(__name__)

# Mapping dictionaries for yard switch URLs
FC_URL_MAP = {
    'ZAZ1': 'https://trans-logistics-eu.amazon.com/transcore/putData?operation=setActiveAccount&accountId=A1TBTQ2PRMRJ6R',
    'LBA4': 'https://trans-logistics-eu.amazon.com/transcore/putData?operation=setActiveAccount&accountId=A2NUUKXUDY50AC',
    'BHX4': 'https://trans-logistics-eu.amazon.com/transcore/putData?operation=setActiveAccount&accountId=A336I0T792ISZT',
    'CDG7': 'https://trans-logistics-eu.amazon.com/transcore/putData?operation=setActiveAccount&accountId=A1XK6DE29OXHBW',
    'DTM1': 'https://trans-logistics-eu.amazon.com/transcore/putData?operation=setActiveAccount&accountId=A3EM063H1X4XBL',
    'DTM2': 'https://trans-logistics-eu.amazon.com/transcore/putData?operation=setActiveAccount&accountId=A3EM063H1X4XBL',
    'HAJ1': 'https://trans-logistics-eu.amazon.com/transcore/putData?operation=setActiveAccount&accountId=A3RSPQ6QYQJ722',
    'WRO5': 'https://trans-logistics-eu.amazon.com/transcore/putData?operation=setActiveAccount&accountId=AM2D5J5KVLIRM',
    'TRN3': 'https://trans-logistics-eu.amazon.com/transcore/putData?operation=setActiveAccount&accountId=ACY7ZIYJ0ITPF'
}

EXTERNAL_YARD_MAP = {
    "VEEY":        {"account_id": "A25THGKI82ZJ9J"},
    "SHRT-HAJ1-1": {"account_id": "A106NBY2LZDDVF"},
    "YWRO":        {"account_id": "A1IW1BAVBUZC61"}
}

EXPECTED_BUILDING_CODE = {
    'ZAZ1': 'ZAZ1',
    'LBA4': 'LBA4',
    'BHX4': 'BHX4',
    'CDG7': 'CDG7',
    'DTM1': 'DTM1',
    'DTM2': 'DTM2',
    'HAJ1': 'HAJ1',
    'WRO5': 'WRO5',
    'TRN3': 'TRN3',
    "VEEY": "VEEY",
    "YWRO": "YWRO"
}

# Mapping for external yards
EXTERNAL_LINKS = {
    "DTM1": "VEEY",
    "DTM2": "VEEY",
    "HAJ1": "SHRT-HAJ1-1",
    "WRO5": "YWRO"
}
