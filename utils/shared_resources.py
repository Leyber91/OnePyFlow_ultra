# shared_resources.py

# Mapping of FC to Country (MP)
FC_TO_COUNTRY = {
    'ZAZ1': 'ES',
    'LBA4': 'UK',
    'BHX4': 'UK',
    'CDG7': 'FR',
        
    'DTM1': 'DE',
    'DTM2': 'DE',
    
    'HAJ1': 'DE',
    'WRO5': 'PL',
    'TRN3': 'IT'
}

# Updated FC configurations with detailed schedules
FC_CONFIGS = {
    'BHX4': {
        'shifts': ['es', 'ns'],
        'hours': {
            'es': {'allDays': [8.5, 19]},
            'ns': {'allDays': [19.75, 5.75]}
        }
    },
    'LBA4': {
        'shifts': ['es', 'ns'],
        'hours': {
            'es': {'allDays': [8.75, 19.25]},
            'ns': {'allDays': [19.75, 6.25]}
        }
    },
    'DTM1': {
        'shifts': ['es', 'ls', 'ns'],
        'hours': {
            'es': {'monSat': [6.25, 15]},
            'ls': {'monSat': [15, 23.75]},
            'ns': {'monFri': [23.75, 6.25]}
        },
        'closed': ['sunday']
    },
    'DTM2': {
        'shifts': ['es', 'ls', 'ns'],
        'hours': {
            'es': {'monSat': [6.25, 15]},
            'ls': {'monSat': [15, 23.75]},
            'ns': {'monFri': [23.75, 6.25]}
        },
        'closed': ['sunday']
    },
    'HAJ1': {
        'shifts': ['es', 'ls', 'ns'],
        'hours': {
            'es': {'monSat': [6, 14]},
            'ls': {'monSat': [14, 22]},
            'ns': {'monFri': [22, 6]}
        },
        'closed': ['sunday']
    },
    'CDG7': {
        'shifts': ['es', 'ls', 'ns', 'cs'],
        'hours': {
            'es': {'monFri': [5.5, 13]},
            'ls': {'monFri': [13.5, 21]},
            'ns': {'monFri': [21.5, 5]},
            'cs': {'saturday': [6, 18.33], 'sunday': [7.17, 19.5]}
        }
    },
    'WRO5': {
        'shifts': ['es', 'ns'],
        'hours': {
            'es': {'monSat': [6.5, 17]},
            'ns': {'monSat': [18, 4.5]}
        },
        'closed': ['sunday']
    },
    'TRN3': {
        'shifts': ['es', 'ls', 'ns'],
        'hours': {
            'es': {'monSun': [6, 14.25]},
            'ls': {'monSun': [14.5, 22.25]},
            'ns': {'monSun': [22.5, 6]}
        }
    },
    'ZAZ1': {
        'shifts': ['es', 'ls', 'ns'],
        'hours': {
            'es': {'monSun': [6, 14.5]},
            'ls': {'monSun': [14.5, 23.25]},
            'ns': {'monFri': [23.33, 6.10]}
        }
    }
}
