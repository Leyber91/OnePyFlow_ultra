"""
🧩 UI Components for OnePyFlow Params Generator
Modular components with dark matrix theme
"""

import os
import json
from datetime import datetime
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from .themes import DarkMatrixTheme

class ModernButton(QPushButton):
    """Modern button with dark matrix styling"""
    def __init__(self, text, color="primary", parent=None, scale_factor=1.0):
        super().__init__(text, parent)
        self.color = color
        self.scale_factor = scale_factor
        self.setMinimumHeight(int(40 * scale_factor))
        self.setFont(QFont('Consolas', int(10 * scale_factor), QFont.Bold))
        self.setCursor(Qt.PointingHandCursor)
        self.setup_style()
        
    def setup_style(self):
        colors = {
            "primary": DarkMatrixTheme.COLORS['accent_primary'],
            "success": DarkMatrixTheme.COLORS['success'], 
            "warning": DarkMatrixTheme.COLORS['warning'],
            "danger": DarkMatrixTheme.COLORS['error'],
            "info": DarkMatrixTheme.COLORS['info'],
            "gold": DarkMatrixTheme.COLORS['ppr_q_highlight']
        }
        
        bg_color = colors.get(self.color, colors["primary"])
        
        self.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {bg_color}, 
                    stop:1 {self.darken_color(bg_color)});
                border: 2px solid {bg_color};
                border-radius: {int(8 * self.scale_factor)}px;
                color: {DarkMatrixTheme.COLORS['bg_primary']};
                font-weight: bold;
                padding: {int(10 * self.scale_factor)}px {int(20 * self.scale_factor)}px;
                min-height: {int(40 * self.scale_factor)}px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {self.lighten_color(bg_color)}, 
                    stop:1 {bg_color});
                border-color: {self.lighten_color(bg_color)};
            }}
            QPushButton:pressed {{
                background: {self.darken_color(bg_color)};
                border-color: {self.darken_color(bg_color)};
            }}
        """)
    
    def lighten_color(self, color):
        """Lighten a hex color"""
        if color == DarkMatrixTheme.COLORS['accent_primary']: return "#33ff66"
        if color == DarkMatrixTheme.COLORS['success']: return "#33ff66"
        if color == DarkMatrixTheme.COLORS['warning']: return "#ffcc33"
        if color == DarkMatrixTheme.COLORS['error']: return "#ff6666"
        if color == DarkMatrixTheme.COLORS['info']: return "#33ccff"
        if color == DarkMatrixTheme.COLORS['ppr_q_highlight']: return "#ffdf33"
        return color
    
    def darken_color(self, color):
        """Darken a hex color"""
        if color == DarkMatrixTheme.COLORS['accent_primary']: return "#00cc33"
        if color == DarkMatrixTheme.COLORS['success']: return "#00cc33"
        if color == DarkMatrixTheme.COLORS['warning']: return "#cc8800"
        if color == DarkMatrixTheme.COLORS['error']: return "#cc3333"
        if color == DarkMatrixTheme.COLORS['info']: return "#0088cc"
        if color == DarkMatrixTheme.COLORS['ppr_q_highlight']: return "#e6c200"
        return color

class SmartDateTimeWidget(QWidget):
    """Smart datetime widget with presets"""
    def __init__(self, label_text, scale_factor=1.0):
        super().__init__()
        self.scale_factor = scale_factor
        self.setup_ui(label_text)
        
    def setup_ui(self, label_text):
        layout = QVBoxLayout(self)
        layout.setSpacing(int(8 * self.scale_factor))
        
        # Label
        label = QLabel(label_text)
        label.setFont(QFont('Consolas', int(11 * self.scale_factor), QFont.Bold))
        label.setStyleSheet(f"color: {DarkMatrixTheme.COLORS['text_primary']}; margin-bottom: 5px;")
        layout.addWidget(label)
        
        # DateTime picker
        self.datetime_edit = QDateTimeEdit()
        self.datetime_edit.setCalendarPopup(True)
        self.datetime_edit.setDisplayFormat("yyyy-MM-dd HH:mm:ss")
        self.datetime_edit.setStyleSheet(f"""
            QDateTimeEdit {{
                padding: {int(10 * self.scale_factor)}px;
                border: 2px solid {DarkMatrixTheme.COLORS['border']};
                border-radius: {int(8 * self.scale_factor)}px;
                font-size: {int(13 * self.scale_factor)}px;
                background: {DarkMatrixTheme.COLORS['bg_tertiary']};
                color: {DarkMatrixTheme.COLORS['text_primary']};
                min-height: {int(20 * self.scale_factor)}px;
            }}
            QDateTimeEdit:focus {{
                border-color: {DarkMatrixTheme.COLORS['accent_primary']};
            }}
            QDateTimeEdit::drop-down {{
                border: none;
                width: 20px;
            }}
        """)
        layout.addWidget(self.datetime_edit)
        
        # Quick preset buttons
        preset_layout = QHBoxLayout()
        preset_layout.setSpacing(int(5 * self.scale_factor))
        
        presets = [
            ("Now", self.set_now),
            ("6AM", lambda: self.set_time(6, 0)),
            ("2PM", lambda: self.set_time(14, 0)),
            ("10PM", lambda: self.set_time(22, 0))
        ]
        
        for text, func in presets:
            btn = QPushButton(text)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: {DarkMatrixTheme.COLORS['bg_tertiary']};
                    border: 1px solid {DarkMatrixTheme.COLORS['border']};
                    border-radius: {int(5 * self.scale_factor)}px;
                    padding: {int(5 * self.scale_factor)}px {int(8 * self.scale_factor)}px;
                    font-size: {int(10 * self.scale_factor)}px;
                    min-height: {int(15 * self.scale_factor)}px;
                    color: {DarkMatrixTheme.COLORS['text_primary']};
                }}
                QPushButton:hover {{
                    background: {DarkMatrixTheme.COLORS['bg_secondary']};
                    border-color: {DarkMatrixTheme.COLORS['accent_primary']};
                }}
                QPushButton:pressed {{
                    background: {DarkMatrixTheme.COLORS['border']};
                }}
            """)
            btn.clicked.connect(func)
            preset_layout.addWidget(btn)
        
        layout.addLayout(preset_layout)
    
    def set_now(self):
        self.datetime_edit.setDateTime(QDateTime.currentDateTime())
    
    def set_time(self, hour, minute):
        current = QDateTime.currentDateTime()
        current.setTime(QTime(hour, minute, 0))
        self.datetime_edit.setDateTime(current)
    
    def get_datetime(self):
        return self.datetime_edit.dateTime()
    
    def set_datetime(self, dt):
        self.datetime_edit.setDateTime(dt)

class AdvancedModuleSelector(QWidget):
    """Advanced module selector with dark matrix styling"""
    def __init__(self, scale_factor=1.0):
        super().__init__()
        self.scale_factor = scale_factor
        self.setup_modules()
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(int(8 * self.scale_factor))
        layout.setContentsMargins(
            int(8 * self.scale_factor), 
            int(8 * self.scale_factor), 
            int(8 * self.scale_factor), 
            int(8 * self.scale_factor)
        )
        
        # Title
        title_layout = QHBoxLayout()
        title_icon = QLabel("◈")
        title_icon.setProperty("class", "icon")
        title_icon.setFont(QFont('Segoe UI Symbol', int(20 * self.scale_factor)))
        title_label = QLabel("Module Selection Hub")
        title_label.setProperty("class", "title")
        title_label.setFont(QFont('Segoe UI', int(18 * self.scale_factor), QFont.Bold))
        title_layout.addWidget(title_icon)
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        layout.addLayout(title_layout)
        
        # Search bar
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search modules...")
        self.search_bar.setStyleSheet(f"""
            QLineEdit {{
                padding: {int(10 * self.scale_factor)}px {int(15 * self.scale_factor)}px;
                border: 2px solid {DarkMatrixTheme.COLORS['border']};
                border-radius: {int(20 * self.scale_factor)}px;
                font-size: {int(14 * self.scale_factor)}px;
                background: {DarkMatrixTheme.COLORS['bg_tertiary']};
                color: {DarkMatrixTheme.COLORS['text_primary']};
            }}
            QLineEdit:focus {{
                border-color: {DarkMatrixTheme.COLORS['accent_primary']};
            }}
        """)
        self.search_bar.textChanged.connect(self.filter_modules)
        layout.addWidget(self.search_bar)
        
        # Module categories with tabs
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet(f"""
            QTabWidget::pane {{
                border: 2px solid {DarkMatrixTheme.COLORS['border']};
                border-radius: {int(10 * self.scale_factor)}px;
                background: {DarkMatrixTheme.COLORS['bg_secondary']};
                padding: {int(10 * self.scale_factor)}px;
            }}
            QTabBar::tab {{
                background: {DarkMatrixTheme.COLORS['bg_tertiary']};
                padding: {int(10 * self.scale_factor)}px {int(15 * self.scale_factor)}px;
                margin-right: 2px;
                border-top-left-radius: {int(8 * self.scale_factor)}px;
                border-top-right-radius: {int(8 * self.scale_factor)}px;
                font-weight: bold;
                min-width: {int(80 * self.scale_factor)}px;
                color: {DarkMatrixTheme.COLORS['text_secondary']};
            }}
            QTabBar::tab:selected {{
                background: {DarkMatrixTheme.COLORS['bg_secondary']};
                color: {DarkMatrixTheme.COLORS['accent_primary']};
                border-bottom: 2px solid {DarkMatrixTheme.COLORS['accent_primary']};
            }}
            QTabBar::tab:hover {{
                background: {DarkMatrixTheme.COLORS['bg_secondary']};
                color: {DarkMatrixTheme.COLORS['text_primary']};
            }}
        """)
        
        self.create_category_tabs()
        layout.addWidget(self.tab_widget)
        
        # Quick selection buttons
        quick_layout = QHBoxLayout()
        quick_layout.setSpacing(int(6 * self.scale_factor))
        
        all_btn = ModernButton("All Modules", "success", scale_factor=self.scale_factor)
        essential_btn = ModernButton("Essential", "primary", scale_factor=self.scale_factor)
        debug_btn = ModernButton("Debug Only", "info", scale_factor=self.scale_factor)
        clear_btn = ModernButton("Clear All", "danger", scale_factor=self.scale_factor)
        
        quick_layout.addWidget(all_btn)
        quick_layout.addWidget(essential_btn)
        quick_layout.addWidget(debug_btn)
        quick_layout.addWidget(clear_btn)
        layout.addLayout(quick_layout)
        
        # Connect quick buttons
        all_btn.clicked.connect(self.select_all)
        essential_btn.clicked.connect(self.select_essential)
        debug_btn.clicked.connect(self.select_debug)
        clear_btn.clicked.connect(self.clear_all)
        
    def setup_modules(self):
        """Setup all available modules with categories"""
        self.modules = {
            "Core Performance": [
                "Echo", "PHC", "HCTool", "BackLog", "PPR", "PPR_Q", "ALPS", "RODEO"
            ],
            "Data Analytics": [
                "Galaxy", "Galaxy_percentages", "Galaxy2", "Galaxy2_values", 
                "ICQA", "F2P", "kNekro", "SSP", "SSPOT"
            ],
            "Logistics & Transport": [
                "DockMaster", "DockMasterFiltered", "DockMaster2", "DockMaster2Filtered",
                "DockFlow", "YMS", "FMC", "CarrierMatrix", "SCACs"
            ],
            "Operations & Support": [
                "ALPS_RC_Sort", "ALPSRoster", "QuipCSV", "VIP", "IBBT"
            ]
        }
        
    def create_category_tabs(self):
        """Create tabs for each module category"""
        self.module_checkboxes = {}
        
        for category, modules in self.modules.items():
            tab = QScrollArea()
            tab_widget = QWidget()
            layout = QVBoxLayout(tab_widget)
            layout.setSpacing(int(8 * self.scale_factor))
            layout.setContentsMargins(
                int(10 * self.scale_factor), 
                int(10 * self.scale_factor), 
                int(10 * self.scale_factor), 
                int(10 * self.scale_factor)
            )
            
            # Category description
            descriptions = {
                "Core Performance": "Essential modules for performance monitoring and analysis",
                "Data Analytics": "Advanced analytics and reporting modules", 
                "Logistics & Transport": "Transportation and dock management systems",
                "Operations & Support": "Operational support and utility modules"
            }
            
            desc_label = QLabel(descriptions.get(category, "Module category"))
            desc_label.setStyleSheet(f"color: {DarkMatrixTheme.COLORS['text_muted']}; font-style: italic; margin-bottom: 10px;")
            desc_label.setWordWrap(True)
            layout.addWidget(desc_label)
            
            # Module checkboxes
            for module in modules:
                checkbox = QCheckBox(module)
                
                # Special highlighting for PPR_Q
                if module == "PPR_Q":
                    checkbox.setProperty("class", "ppr_q")
                    checkbox.setStyleSheet(f"""
                        QCheckBox[class="ppr_q"] {{
                            background: {DarkMatrixTheme.COLORS['ppr_q_highlight']};
                            color: {DarkMatrixTheme.COLORS['bg_primary']};
                            border-radius: {int(8 * self.scale_factor)}px;
                            padding: {int(12 * self.scale_factor)}px;
                            font-weight: bold;
                            font-size: {int(14 * self.scale_factor)}px;
                            margin: 5px 0px;
                            border: 2px solid #e6c200;
                        }}
                        QCheckBox[class="ppr_q"]::indicator {{
                            width: {int(20 * self.scale_factor)}px;
                            height: {int(20 * self.scale_factor)}px;
                            border-radius: {int(10 * self.scale_factor)}px;
                            border: 3px solid #e6c200;
                            background: white;
                        }}
                        QCheckBox[class="ppr_q"]::indicator:checked {{
                            background: {DarkMatrixTheme.COLORS['ppr_q_highlight']};
                            border-color: #e6c200;
                        }}
                    """)
                    checkbox.setToolTip("NEW! PPR Quarterly - Minute-level precision analysis")
                else:
                    checkbox.setStyleSheet(f"""
                        QCheckBox {{
                            font-size: {int(13 * self.scale_factor)}px;
                            padding: {int(8 * self.scale_factor)}px;
                            spacing: {int(10 * self.scale_factor)}px;
                            color: {DarkMatrixTheme.COLORS['text_primary']};
                        }}
                        QCheckBox::indicator {{
                            width: {int(18 * self.scale_factor)}px;
                            height: {int(18 * self.scale_factor)}px;
                            border-radius: {int(9 * self.scale_factor)}px;
                            border: 2px solid {DarkMatrixTheme.COLORS['border']};
                            background: {DarkMatrixTheme.COLORS['bg_tertiary']};
                        }}
                        QCheckBox::indicator:checked {{
                            background: {DarkMatrixTheme.COLORS['accent_primary']};
                            border-color: {DarkMatrixTheme.COLORS['accent_primary']};
                        }}
                    """)
                
                layout.addWidget(checkbox)
                self.module_checkboxes[module] = checkbox
            
            layout.addStretch()
            tab.setWidget(tab_widget)
            tab.setWidgetResizable(True)
            
            # Clean tab title (remove emoji)
            clean_title = category.split(' ', 1)[1] if ' ' in category else category
            self.tab_widget.addTab(tab, clean_title)
    
    def filter_modules(self, text):
        """Filter modules based on search text"""
        for module, checkbox in self.module_checkboxes.items():
            visible = text.lower() in module.lower()
            checkbox.setVisible(visible)
    
    def select_all(self):
        for checkbox in self.module_checkboxes.values():
            checkbox.setChecked(True)
    
    def select_essential(self):
        essential = ["Echo", "PPR_Q", "ALPS", "Galaxy", "DockMaster"]
        self.clear_all()
        for module, checkbox in self.module_checkboxes.items():
            if module in essential:
                checkbox.setChecked(True)
    
    def select_debug(self):
        self.clear_all()
        self.module_checkboxes["Echo"].setChecked(True)
    
    def clear_all(self):
        for checkbox in self.module_checkboxes.values():
            checkbox.setChecked(False)
    
    def get_selected_modules(self):
        return [module for module, checkbox in self.module_checkboxes.items() 
                if checkbox.isChecked()]

class ConfigurationPanel(QWidget):
    """Configuration panel with site and time settings"""
    def __init__(self, scale_factor=1.0):
        super().__init__()
        self.scale_factor = scale_factor
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(int(8 * self.scale_factor))
        
        # Title
        title = QLabel("Configuration Hub")
        title.setProperty("class", "title")
        title.setFont(QFont('Segoe UI', int(18 * self.scale_factor), QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Site configuration group
        site_group = QGroupBox("Site Configuration")
        site_group.setStyleSheet(f"""
            QGroupBox {{
                font-weight: bold;
                border: 2px solid {DarkMatrixTheme.COLORS['border']};
                border-radius: {int(10 * self.scale_factor)}px;
                margin-top: 10px;
                padding-top: 15px;
                color: {DarkMatrixTheme.COLORS['text_primary']};
                background: {DarkMatrixTheme.COLORS['bg_secondary']};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px 0 10px;
                background: {DarkMatrixTheme.COLORS['bg_secondary']};
                color: {DarkMatrixTheme.COLORS['accent_primary']};
            }}
        """)
        site_layout = QGridLayout(site_group)
        site_layout.setSpacing(int(10 * self.scale_factor))
        
        # Site combo
        site_label = QLabel("Site:")
        site_label.setStyleSheet(f"color: {DarkMatrixTheme.COLORS['text_primary']}; font-weight: bold;")
        self.site_combo = QComboBox()
        sites = ["ZAZ1", "LBA4", "BHX4", "CDG7", "DTM1", "DTM2", "HAJ1", "WRO5", "TRN3", "BCN1", "MXP5"]
        self.site_combo.addItems(sites)
        self.site_combo.setEditable(True)
        self.site_combo.setStyleSheet(f"""
            QComboBox {{
                padding: {int(8 * self.scale_factor)}px;
                border: 2px solid {DarkMatrixTheme.COLORS['border']};
                border-radius: {int(8 * self.scale_factor)}px;
                background: {DarkMatrixTheme.COLORS['bg_tertiary']};
                color: {DarkMatrixTheme.COLORS['text_primary']};
                font-size: {int(13 * self.scale_factor)}px;
                min-height: {int(20 * self.scale_factor)}px;
            }}
            QComboBox:focus {{
                border-color: {DarkMatrixTheme.COLORS['accent_primary']};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}
        """)
        
        # Plan type
        plan_label = QLabel("Plan Type:")
        plan_label.setStyleSheet(f"color: {DarkMatrixTheme.COLORS['text_primary']}; font-weight: bold;")
        self.plan_combo = QComboBox()
        self.plan_combo.addItems(["Prior-Day", "Next-Shift", "SOS", "Real-Time"])
        self.plan_combo.setStyleSheet(self.site_combo.styleSheet())
        
        # Shift
        shift_label = QLabel("Shift:")
        shift_label.setStyleSheet(f"color: {DarkMatrixTheme.COLORS['text_primary']}; font-weight: bold;")
        self.shift_combo = QComboBox()
        self.shift_combo.addItems(["ES", "LS", "NS", "CS", "All-Shifts"])
        self.shift_combo.setStyleSheet(self.site_combo.styleSheet())
        
        site_layout.addWidget(site_label, 0, 0)
        site_layout.addWidget(self.site_combo, 0, 1)
        site_layout.addWidget(plan_label, 1, 0)
        site_layout.addWidget(self.plan_combo, 1, 1)
        site_layout.addWidget(shift_label, 2, 0)
        site_layout.addWidget(self.shift_combo, 2, 1)
        
        layout.addWidget(site_group)
        
        # DateTime configuration
        datetime_group = QGroupBox("Time Configuration")
        datetime_group.setStyleSheet(site_group.styleSheet())
        datetime_layout = QVBoxLayout(datetime_group)
        datetime_layout.setSpacing(int(10 * self.scale_factor))
        
        self.sos_widget = SmartDateTimeWidget("Start of Shift (SOS)", self.scale_factor)
        self.eos_widget = SmartDateTimeWidget("End of Shift (EOS)", self.scale_factor)
        
        datetime_layout.addWidget(self.sos_widget)
        datetime_layout.addWidget(self.eos_widget)
        
        # Smart shift buttons
        shift_buttons = QHBoxLayout()
        shift_buttons.setSpacing(int(5 * self.scale_factor))
        
        morning_btn = ModernButton("Morning", "info", scale_factor=self.scale_factor)
        evening_btn = ModernButton("Evening", "warning", scale_factor=self.scale_factor) 
        night_btn = ModernButton("Night", "primary", scale_factor=self.scale_factor)
        
        morning_btn.clicked.connect(lambda: self.set_shift(6, 14))
        evening_btn.clicked.connect(lambda: self.set_shift(14, 22))
        night_btn.clicked.connect(lambda: self.set_shift(22, 6, True))
        
        shift_buttons.addWidget(morning_btn)
        shift_buttons.addWidget(evening_btn)
        shift_buttons.addWidget(night_btn)
        
        datetime_layout.addLayout(shift_buttons)
        layout.addWidget(datetime_group)
        
        # PPR_Q Special Configuration
        ppr_q_group = QGroupBox("PPR_Q Advanced Settings")
        ppr_q_group.setProperty("class", "ppr_q")
        ppr_q_group.setStyleSheet(f"""
            QGroupBox[class="ppr_q"] {{
                font-weight: bold;
                border: 3px solid {DarkMatrixTheme.COLORS['ppr_q_highlight']};
                border-radius: {int(10 * self.scale_factor)}px;
                margin-top: 10px;
                padding-top: 15px;
                color: {DarkMatrixTheme.COLORS['ppr_q_highlight']};
                background: #1a1a00;
            }}
            QGroupBox[class="ppr_q"]::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px 0 10px;
                background: {DarkMatrixTheme.COLORS['bg_secondary']};
                color: {DarkMatrixTheme.COLORS['ppr_q_highlight']};
            }}
        """)
        ppr_q_layout = QVBoxLayout(ppr_q_group)
        
        self.ppr_q_enabled = QCheckBox("Enable PPR_Q Minute-Level Analysis")
        self.ppr_q_enabled.setProperty("class", "ppr_q")
        self.ppr_q_enabled.setStyleSheet(f"""
            QCheckBox[class="ppr_q"] {{
                color: {DarkMatrixTheme.COLORS['text_primary']}; 
                font-weight: bold;
                font-size: {int(13 * self.scale_factor)}px;
            }}
            QCheckBox[class="ppr_q"]::indicator {{
                width: {int(18 * self.scale_factor)}px;
                height: {int(18 * self.scale_factor)}px;
                border-radius: {int(9 * self.scale_factor)}px;
                border: 2px solid {DarkMatrixTheme.COLORS['ppr_q_highlight']};
                background: {DarkMatrixTheme.COLORS['bg_tertiary']};
            }}
            QCheckBox[class="ppr_q"]::indicator:checked {{
                background: {DarkMatrixTheme.COLORS['ppr_q_highlight']};
                border-color: {DarkMatrixTheme.COLORS['ppr_q_highlight']};
            }}
        """)
        self.ppr_q_enabled.setChecked(True)
        
        ppr_q_info = QLabel("NEW: Get PPR data with minute-level precision!\nPerfect for detailed shift analysis and real-time monitoring.")
        ppr_q_info.setStyleSheet(f"color: {DarkMatrixTheme.COLORS['ppr_q_highlight']}; font-style: italic; margin: 10px; font-size: {int(12 * self.scale_factor)}px;")
        ppr_q_info.setWordWrap(True)
        
        ppr_q_layout.addWidget(self.ppr_q_enabled)
        ppr_q_layout.addWidget(ppr_q_info)
        layout.addWidget(ppr_q_group)
        
        layout.addStretch()
    
    def set_shift(self, start_hour, end_hour, next_day=False):
        """Set shift times intelligently"""
        current_date = QDateTime.currentDateTime().date()
        
        sos = QDateTime(current_date, QTime(start_hour, 0))
        self.sos_widget.set_datetime(sos)
        
        if next_day:
            eos = QDateTime(current_date.addDays(1), QTime(end_hour, 0))
        else:
            eos = QDateTime(current_date, QTime(end_hour, 0))
        self.eos_widget.set_datetime(eos)
    
    def get_config_data(self):
        """Get configuration data"""
        return {
            "site": self.site_combo.currentText(),
            "plan_type": self.plan_combo.currentText(),
            "shift": self.shift_combo.currentText(),
            "sos_datetime": self.sos_widget.get_datetime().toString("yyyy-MM-dd HH:mm:ss"),
            "eos_datetime": self.eos_widget.get_datetime().toString("yyyy-MM-dd HH:mm:ss"),
            "ppr_q_enabled": self.ppr_q_enabled.isChecked()
        }
    
    def set_defaults(self):
        """Set intelligent defaults"""
        self.site_combo.setCurrentText("DTM2")
        self.plan_combo.setCurrentText("Prior-Day")
        self.shift_combo.setCurrentText("LS")
        
        # Set default times
        current = QDateTime.currentDateTime()
        self.sos_widget.set_datetime(current.addSecs(-3600))  # 1 hour ago
        self.eos_widget.set_datetime(current)

class ActionPanel(QWidget):
    """Action panel with output configuration and action buttons"""
    def __init__(self, scale_factor=1.0):
        super().__init__()
        self.scale_factor = scale_factor
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(int(8 * self.scale_factor))
        
        # Output configuration
        output_group = QGroupBox("Output Configuration")
        output_group.setStyleSheet(f"""
            QGroupBox {{
                font-weight: bold;
                border: 2px solid {DarkMatrixTheme.COLORS['border']};
                border-radius: {int(10 * self.scale_factor)}px;
                margin-top: 10px;
                padding-top: 15px;
                color: {DarkMatrixTheme.COLORS['text_primary']};
                background: {DarkMatrixTheme.COLORS['bg_secondary']};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px 0 10px;
                background: {DarkMatrixTheme.COLORS['bg_secondary']};
                color: {DarkMatrixTheme.COLORS['accent_primary']};
            }}
        """)
        output_layout = QHBoxLayout(output_group)
        
        self.output_path = QLineEdit()
        self.output_path.setPlaceholderText("Select output directory...")
        self.output_path.setStyleSheet(f"""
            QLineEdit {{
                padding: {int(10 * self.scale_factor)}px;
                border: 2px solid {DarkMatrixTheme.COLORS['border']};
                border-radius: {int(8 * self.scale_factor)}px;
                background: {DarkMatrixTheme.COLORS['bg_tertiary']};
                color: {DarkMatrixTheme.COLORS['text_primary']};
                font-size: {int(13 * self.scale_factor)}px;
            }}
            QLineEdit:focus {{
                border-color: {DarkMatrixTheme.COLORS['accent_primary']};
            }}
        """)
        
        browse_btn = ModernButton("Browse", "info", scale_factor=self.scale_factor)
        browse_btn.clicked.connect(self.browse_output)
        
        output_layout.addWidget(self.output_path, 1)
        output_layout.addWidget(browse_btn, 0)
        layout.addWidget(output_group)
        
        # Action buttons
        action_layout = QHBoxLayout()
        action_layout.setSpacing(int(6 * self.scale_factor))
        
        preview_btn = ModernButton("Preview JSON", "info", scale_factor=self.scale_factor)
        save_btn = ModernButton("Save Only", "primary", scale_factor=self.scale_factor)
        generate_btn = ModernButton("Generate & Run", "success", scale_factor=self.scale_factor)
        
        action_layout.addWidget(preview_btn)
        action_layout.addWidget(save_btn)
        action_layout.addWidget(generate_btn)
        
        layout.addLayout(action_layout)
        
        # Store button references for external connections
        self.preview_btn = preview_btn
        self.save_btn = save_btn
        self.generate_btn = generate_btn
    
    def browse_output(self):
        """Browse for output directory"""
        path = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if path:
            self.output_path.setText(path)
    
    def get_output_path(self):
        """Get the output path"""
        return self.output_path.text()
    
    def set_default_output_path(self, path):
        """Set default output path"""
        self.output_path.setText(path) 