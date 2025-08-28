"""
Configuration panel for site and schedule settings
"""

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from datetime import datetime, timedelta
from .theme import Theme
from .fc_configs import FCConfigs
from .schedule_picker import VisualSchedulePicker, ShiftPresetWidget

class ConfigPanel(QWidget):
    """Configuration panel for site and schedule settings"""
    
    fc_changed = pyqtSignal(str)
    schedule_changed = pyqtSignal(QDateTime, QDateTime)
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.setup_connections()
        
    def setup_ui(self):
        """Setup the configuration panel UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(Theme.SPACING['lg'])
        
        # Site configuration group
        site_group = QGroupBox("🏢 Site Configuration")
        site_group.setStyleSheet(Theme.STYLES['group_box'])
        site_layout = QGridLayout(site_group)
        site_layout.setSpacing(Theme.SPACING['md'])
        
        # Site selector
        site_label = QLabel("Site:")
        site_label.setStyleSheet(f"color: {Theme.COLORS['text_primary']}; font-weight: bold;")
        self.site_combo = QComboBox()
        self.site_combo.addItems(FCConfigs.AVAILABLE_FCS)
        self.site_combo.setCurrentText("DTM2")
        self.site_combo.setStyleSheet(Theme.STYLES['input_field'])
        
        # Plan type selector
        plan_label = QLabel("Plan Type:")
        plan_label.setStyleSheet(f"color: {Theme.COLORS['text_primary']}; font-weight: bold;")
        self.plan_combo = QComboBox()
        self.plan_combo.addItems(FCConfigs.PLAN_TYPES)
        self.plan_combo.setStyleSheet(Theme.STYLES['input_field'])
        
        site_layout.addWidget(site_label, 0, 0)
        site_layout.addWidget(self.site_combo, 0, 1)
        site_layout.addWidget(plan_label, 1, 0)
        site_layout.addWidget(self.plan_combo, 1, 1)
        
        layout.addWidget(site_group)
        
        # Schedule configuration group
        schedule_group = QGroupBox("⏰ Schedule Configuration")
        schedule_group.setStyleSheet(Theme.STYLES['group_box'])
        schedule_layout = QVBoxLayout(schedule_group)
        schedule_layout.setSpacing(Theme.SPACING['md'])
        
        # Visual schedule picker
        self.schedule_picker = VisualSchedulePicker("DTM2")
        schedule_layout.addWidget(self.schedule_picker)
        
        # Shift presets
        self.shift_presets = ShiftPresetWidget("DTM2")
        schedule_layout.addWidget(self.shift_presets)
        
        # DateTime inputs
        datetime_group = QGroupBox("Custom Times")
        datetime_group.setStyleSheet(f"""
            QGroupBox {{
                border: 1px solid {Theme.COLORS['border']};
                border-radius: 8px;
                margin: 4px;
                padding: 8px;
                font-size: {Theme.FONTS['small']}px;
                color: {Theme.COLORS['text_secondary']};
            }}
        """)
        datetime_layout = QGridLayout(datetime_group)
        datetime_layout.setSpacing(Theme.SPACING['sm'])
        
        # Start datetime
        start_label = QLabel("Start:")
        start_label.setStyleSheet(f"color: {Theme.COLORS['text_primary']}; font-weight: bold;")
        self.start_datetime = QDateTimeEdit(QDateTime.currentDateTime().addSecs(-3600))
        self.start_datetime.setDisplayFormat("yyyy-MM-dd HH:mm")
        self.start_datetime.setStyleSheet(Theme.STYLES['input_field'])
        
        # End datetime
        end_label = QLabel("End:")
        end_label.setStyleSheet(f"color: {Theme.COLORS['text_primary']}; font-weight: bold;")
        self.end_datetime = QDateTimeEdit(QDateTime.currentDateTime())
        self.end_datetime.setDisplayFormat("yyyy-MM-dd HH:mm")
        self.end_datetime.setStyleSheet(Theme.STYLES['input_field'])
        
        # Reset button
        reset_btn = QPushButton("Reset to Now")
        reset_btn.setStyleSheet(Theme.STYLES['button_secondary'])
        reset_btn.clicked.connect(self.reset_to_now)
        
        datetime_layout.addWidget(start_label, 0, 0)
        datetime_layout.addWidget(self.start_datetime, 0, 1)
        datetime_layout.addWidget(end_label, 1, 0)
        datetime_layout.addWidget(self.end_datetime, 1, 1)
        datetime_layout.addWidget(reset_btn, 2, 0, 1, 2)
        
        schedule_layout.addWidget(datetime_group)
        layout.addWidget(schedule_group)
        
        layout.addStretch()
        
    def setup_connections(self):
        """Setup signal connections"""
        self.site_combo.currentTextChanged.connect(self.on_site_changed)
        self.shift_presets.shift_selected.connect(self.on_shift_selected)
        self.schedule_picker.schedule_changed.connect(self.on_schedule_picker_changed)
        self.start_datetime.dateTimeChanged.connect(self.on_datetime_changed)
        self.end_datetime.dateTimeChanged.connect(self.on_datetime_changed)
        
    def on_site_changed(self, site):
        """Handle site change"""
        self.schedule_picker.set_fc(site)
        self.shift_presets.set_fc(site)
        self.fc_changed.emit(site)
        
    def on_shift_selected(self, shift):
        """Handle shift selection from presets"""
        self.schedule_picker.set_shift(shift)
        
    def on_schedule_picker_changed(self, start_hour, end_hour):
        """Handle schedule picker changes"""
        self.update_datetime_from_schedule(start_hour, end_hour)
        
    def on_datetime_changed(self):
        """Handle datetime input changes"""
        self.schedule_changed.emit(self.start_datetime.dateTime(), self.end_datetime.dateTime())
        
    def update_datetime_from_schedule(self, start_hour, end_hour):
        """Update datetime inputs from schedule picker"""
        current_date = QDateTime.currentDateTime().date()
        
        start_h = int(start_hour)
        start_m = int((start_hour % 1) * 60)
        end_h = int(end_hour)
        end_m = int((end_hour % 1) * 60)
        
        start_dt = QDateTime(current_date, QTime(start_h, start_m))
        
        # Handle overnight shifts
        if end_hour < start_hour:
            end_dt = QDateTime(current_date.addDays(1), QTime(end_h, end_m))
        else:
            end_dt = QDateTime(current_date, QTime(end_h, end_m))
            
        self.start_datetime.setDateTime(start_dt)
        self.end_datetime.setDateTime(end_dt)
        self.schedule_changed.emit(start_dt, end_dt)
        
    def reset_to_now(self):
        """Reset datetime to current time"""
        now = QDateTime.currentDateTime()
        self.start_datetime.setDateTime(now.addSecs(-3600))
        self.end_datetime.setDateTime(now)
        
    def get_config(self):
        """Get current configuration"""
        return {
            'site': self.site_combo.currentText(),
            'plan_type': self.plan_combo.currentText(),
            'start_datetime': self.start_datetime.dateTime(),
            'end_datetime': self.end_datetime.dateTime()
        }
        
    def set_config(self, config):
        """Set configuration from dict"""
        if 'site' in config:
            self.site_combo.setCurrentText(config['site'])
        if 'plan_type' in config:
            self.plan_combo.setCurrentText(config['plan_type'])
        if 'start_datetime' in config:
            self.start_datetime.setDateTime(config['start_datetime'])
        if 'end_datetime' in config:
            self.end_datetime.setDateTime(config['end_datetime'])
