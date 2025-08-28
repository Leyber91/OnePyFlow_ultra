"""
FC configurations and shift definitions
"""

class FCConfigs:
    """Fulfilment Center configurations and shift schedules"""
    
    # FC shift configurations (hours in decimal format)
    SHIFT_CONFIGS = {
        'BHX4': {
            'es': (7.5, 18.0),
            'ns': (18.75, 29.25)  # 18:45 to 05:15 next day
        },
        'CDG7': {
            'es': (5.5, 13.0),    # 05:30 to 13:00
            'ls': (13.5, 21.0),   # 13:30 to 21:00
            'ns': (21.5, 29.0),   # 21:30 to 05:00 next day
            'cs-sat': (6.0, 18.5), # 06:00 to 18:30
            'cs-sun': (7.0, 19.5)  # 07:00 to 19:30
        },
        'DTM1': {
            'es': (6.25, 15.0),   # 06:15 to 15:00
            'ls': (15.0, 23.75),  # 15:00 to 23:45
            'ns': (23.75, 30.25)  # 23:45 to 06:15 next day
        },
        'DTM2': {
            'es': (6.25, 15.0),   # 06:15 to 15:00
            'ls': (15.0, 23.75),  # 15:00 to 23:45
            'ns': (23.75, 30.25)  # 23:45 to 06:15 next day
        },
        'HAJ1': {
            'es': (6.0, 14.0),    # 06:00 to 14:00
            'ls': (14.0, 22.0),   # 14:00 to 22:00
            'ns': (22.0, 30.0)    # 22:00 to 06:00 next day
        },
        'LBA4': {
            'es': (7.75, 18.25),  # 07:45 to 18:15
            'ns': (18.75, 29.5)   # 18:45 to 05:30 next day
        },
        'TRN3': {
            'es': (6.0, 14.0),    # 06:00 to 14:00
            'ls': (14.75, 22.5),  # 14:45 to 22:30
            'ns': (22.5, 30.0)    # 22:30 to 06:00 next day
        },
        'WRO5': {
            'es': (6.5, 17.0),    # 06:30 to 17:00
            'ns': (18.0, 28.5)    # 18:00 to 04:30 next day
        },
        'ZAZ1': {
            'es': (6.0, 14.5),    # 06:00 to 14:30
            'ls': (14.5, 23.0),   # 14:30 to 23:00
            'ns': (23.0, 30.0)    # 23:00 to 06:00 next day
        },
        'BCN1': {
            'es': (6.0, 14.0),    # Default schedule
            'ls': (14.0, 22.0),
            'ns': (22.0, 30.0)
        },
        'MXP5': {
            'es': (6.0, 14.0),    # Default schedule
            'ls': (14.0, 22.0),
            'ns': (22.0, 30.0)
        }
    }
    
    # Available FCs
    AVAILABLE_FCS = list(SHIFT_CONFIGS.keys())
    
    # Plan types
    PLAN_TYPES = ["Prior-Day", "Next-Shift", "SOS", "Real-Time"]
    
    @classmethod
    def get_shifts_for_fc(cls, fc):
        """Get available shifts for a specific FC"""
        return cls.SHIFT_CONFIGS.get(fc, cls.SHIFT_CONFIGS['DTM2'])
    
    @classmethod
    def get_shift_times(cls, fc, shift):
        """Get start and end times for a specific shift"""
        shifts = cls.get_shifts_for_fc(fc)
        return shifts.get(shift, (6.0, 14.0))
    
    @classmethod
    def format_time(cls, decimal_hour):
        """Convert decimal hour to HH:MM format"""
        hour = int(decimal_hour % 24)
        minute = int((decimal_hour % 1) * 60)
        return f"{hour:02d}:{minute:02d}"
    
    @classmethod
    def get_shift_display_name(cls, shift):
        """Get display name for shift"""
        display_names = {
            'es': 'ES (Early Shift)',
            'ls': 'LS (Late Shift)', 
            'ns': 'NS (Night Shift)',
            'cs-sat': 'CS-SAT (Saturday)',
            'cs-sun': 'CS-SUN (Sunday)'
        }
        return display_names.get(shift, shift.upper())
