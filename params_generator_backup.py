#!/usr/bin/env python3
"""
🚀 OnePyFlow Params Generator V2.0 - PyQt5 Compatible Edition 🚀
Modern UI with PyQt5-compatible styling and advanced features
Supports PPR_Q and all latest modules with intelligent presets
"""

import sys
import os
import json
from datetime import datetime, timedelta
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class ModernButton(QPushButton):
    """Modern button with PyQt5-compatible styling"""
    def __init__(self, text, color="primary", parent=None):
        super().__init__(text, parent)
        self.color = color
        self.setMinimumHeight(40)
        self.setFont(QFont('Segoe UI', 10, QFont.Bold))
        self.setCursor(Qt.PointingHandCursor)
        self.setup_style()
        
    def setup_style(self):
        colors = {
            "primary": "#667eea",
            "success": "#4facfe", 
            "warning": "#fa709a",
            "danger": "#ff6b6b",
            "info": "#a8edea",
            "gold": "#ffd700"
        }
        
        bg_color = colors.get(self.color, colors["primary"])
        
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg_color};
                border: none;
                border-radius: 20px;
                color: white;
                font-weight: bold;
                padding: 10px 20px;
            }}
            QPushButton:hover {{
                background-color: {self.lighten_color(bg_color)};
            }}
            QPushButton:pressed {{
                background-color: {self.darken_color(bg_color)};
            }}
        """)
    
    def lighten_color(self, color):
        """Lighten a hex color"""
        if color == "#667eea": return "#7c8ef0"
        if color == "#4facfe": return "#6bb8fe"
        if color == "#fa709a": return "#fb85ab"
        if color == "#ff6b6b": return "#ff8585"
        if color == "#a8edea": return "#baf1ee"
        if color == "#ffd700": return "#ffdf33"
        return color
    
    def darken_color(self, color):
        """Darken a hex color"""
        if color == "#667eea": return "#5a6fd4"
        if color == "#4facfe": return "#3d9bfe"
        if color == "#fa709a": return "#f95b89"
        if color == "#ff6b6b": return "#ff5151"
        if color == "#a8edea": return "#97e9e6"
        if color == "#ffd700": return "#e6c200"
        return color

class AdvancedModuleSelector(QWidget):
    """Advanced module selector with proper PyQt5 styling"""
    def __init__(self):
        super().__init__()
        self.setup_modules()
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Title
        title_layout = QHBoxLayout()
        title_icon = QLabel("🧩")
        title_icon.setFont(QFont('Segoe UI Emoji', 16))
        title_label = QLabel("Module Selection Hub")
        title_label.setFont(QFont('Segoe UI', 14, QFont.Bold))
        title_label.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        title_layout.addWidget(title_icon)
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        layout.addLayout(title_layout)
        
        # Search bar
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("🔍 Search modules...")
        self.search_bar.setStyleSheet("""
            QLineEdit {
                padding: 10px 15px;
                border: 2px solid #e0e6ed;
                border-radius: 20px;
                font-size: 14px;
                background: white;
            }
            QLineEdit:focus {
                border-color: #667eea;
            }
        """)
        self.search_bar.textChanged.connect(self.filter_modules)
        layout.addWidget(self.search_bar)
        
        # Module categories with tabs
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 2px solid #e0e6ed;
                border-radius: 10px;
                background: white;
                padding: 10px;
            }
            QTabBar::tab {
                background: #f8f9fa;
                padding: 10px 15px;
                margin-right: 2px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-weight: bold;
                min-width: 80px;
            }
            QTabBar::tab:selected {
                background: white;
                color: #667eea;
                border-bottom: 2px solid #667eea;
            }
            QTabBar::tab:hover {
                background: #e9ecef;
            }
        """)
        
        self.create_category_tabs()
        layout.addWidget(self.tab_widget)
        
        # Quick selection buttons
        quick_layout = QHBoxLayout()
        quick_layout.addWidget(ModernButton("🚀 All Modules", "success"))
        quick_layout.addWidget(ModernButton("⚡ Essential", "primary"))
        quick_layout.addWidget(ModernButton("🧪 Debug Only", "info"))
        quick_layout.addWidget(ModernButton("🔄 Clear All", "danger"))
        layout.addLayout(quick_layout)
        
        # Connect quick buttons
        quick_layout.itemAt(0).widget().clicked.connect(self.select_all)
        quick_layout.itemAt(1).widget().clicked.connect(self.select_essential)
        quick_layout.itemAt(2).widget().clicked.connect(self.select_debug)
        quick_layout.itemAt(3).widget().clicked.connect(self.clear_all)
        
    def setup_modules(self):
        """Setup all available modules with categories"""
        self.modules = {
            "🚀 Core Performance": [
                "Echo", "PHC", "HCTool", "BackLog", "PPR", "PPR_Q", "ALPS", "RODEO"
            ],
            "📊 Data Analytics": [
                "Galaxy", "Galaxy_percentages", "Galaxy2", "Galaxy2_values", 
                "ICQA", "F2P", "kNekro", "SSP", "SSPOT"
            ],
            "🚛 Logistics & Transport": [
                "DockMaster", "DockMasterFiltered", "DockMaster2", "DockMaster2Filtered",
                "DockFlow", "YMS", "FMC", "CarrierMatrix", "SCACs"
            ],
            "🔧 Operations & Support": [
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
            layout.setSpacing(8)
            layout.setContentsMargins(10, 10, 10, 10)
            
            # Category description
            descriptions = {
                "🚀 Core Performance": "Essential modules for performance monitoring and analysis",
                "📊 Data Analytics": "Advanced analytics and reporting modules", 
                "🚛 Logistics & Transport": "Transportation and dock management systems",
                "🔧 Operations & Support": "Operational support and utility modules"
            }
            
            desc_label = QLabel(descriptions.get(category, "Module category"))
            desc_label.setStyleSheet("color: #6c757d; font-style: italic; margin-bottom: 10px;")
            desc_label.setWordWrap(True)
            layout.addWidget(desc_label)
            
            # Module checkboxes
            for module in modules:
                checkbox = QCheckBox(module)
                checkbox.setStyleSheet("""
                    QCheckBox {
                        font-size: 13px;
                        padding: 8px;
                        spacing: 10px;
                    }
                    QCheckBox::indicator {
                        width: 18px;
                        height: 18px;
                        border-radius: 9px;
                        border: 2px solid #dee2e6;
                        background: white;
                    }
                    QCheckBox::indicator:checked {
                        background: #667eea;
                        border-color: #667eea;
                    }
                """)
                
                # Special highlighting for PPR_Q
                if module == "PPR_Q":
                    checkbox.setStyleSheet("""
                        QCheckBox {
                            background: #ffd700;
                            color: #2c3e50;
                            border-radius: 8px;
                            padding: 12px;
                            font-weight: bold;
                            font-size: 14px;
                            margin: 5px 0px;
                            border: 2px solid #e6c200;
                        }
                        QCheckBox::indicator {
                            width: 20px;
                            height: 20px;
                            border-radius: 10px;
                            border: 3px solid #e6c200;
                            background: white;
                        }
                        QCheckBox::indicator:checked {
                            background: #ffd700;
                            border-color: #e6c200;
                        }
                    """)
                    checkbox.setToolTip("🆕 NEW! PPR Quarterly - Minute-level precision analysis")
                
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

class SmartDateTimeWidget(QWidget):
    """Smart datetime widget with presets"""
    def __init__(self, label_text):
        super().__init__()
        self.setup_ui(label_text)
        
    def setup_ui(self, label_text):
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        
        # Label
        label = QLabel(label_text)
        label.setFont(QFont('Segoe UI', 11, QFont.Bold))
        label.setStyleSheet("color: #2c3e50; margin-bottom: 5px;")
        layout.addWidget(label)
        
        # DateTime picker
        self.datetime_edit = QDateTimeEdit()
        self.datetime_edit.setCalendarPopup(True)
        self.datetime_edit.setDisplayFormat("yyyy-MM-dd HH:mm:ss")
        self.datetime_edit.setStyleSheet("""
            QDateTimeEdit {
                padding: 10px;
                border: 2px solid #e0e6ed;
                border-radius: 8px;
                font-size: 13px;
                background: white;
                min-height: 20px;
            }
            QDateTimeEdit:focus {
                border-color: #667eea;
            }
            QDateTimeEdit::drop-down {
                border: none;
                width: 20px;
            }
        """)
        layout.addWidget(self.datetime_edit)
        
        # Quick preset buttons
        preset_layout = QHBoxLayout()
        preset_layout.setSpacing(5)
        
        presets = [
            ("Now", self.set_now),
            ("6AM", lambda: self.set_time(6, 0)),
            ("2PM", lambda: self.set_time(14, 0)),
            ("10PM", lambda: self.set_time(22, 0))
        ]
        
        for text, func in presets:
            btn = QPushButton(text)
            btn.setStyleSheet("""
                QPushButton {
                    background: #f8f9fa;
                    border: 1px solid #dee2e6;
                    border-radius: 5px;
                    padding: 5px 8px;
                    font-size: 10px;
                    min-height: 15px;
                }
                QPushButton:hover {
                    background: #e9ecef;
                }
                QPushButton:pressed {
                    background: #dee2e6;
                }
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

class OnePyFlowParamsGenerator(QMainWindow):
    """🚀 OnePyFlow Parameters Generator V2.0"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🚀 OnePyFlow Params Generator V2.0 - Revolutionary Edition")
        self.setMinimumSize(1400, 900)
        self.setup_ui()
        self.set_defaults()
        
    def setup_ui(self):
        """Setup the main UI"""
        # Set main window style
        self.setStyleSheet("""
            QMainWindow {
                background: #667eea;
            }
        """)
        
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        
        # Main layout - horizontal split
        main_layout = QHBoxLayout(central)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        # Left container - Configuration + Actions
        left_container = QWidget()
        left_layout = QVBoxLayout(left_container)
        left_layout.setSpacing(15)
        
        # Create panels
        config_panel = self.create_config_panel()
        action_panel = self.create_action_panel()
        
        left_layout.addWidget(config_panel, 1)
        left_layout.addWidget(action_panel, 0)
        
        # Right panel - Module selection  
        module_panel = self.create_module_panel()
        
        # Add to main layout
        main_layout.addWidget(left_container, 1)
        main_layout.addWidget(module_panel, 2)
        
    def create_config_panel(self):
        """Create the configuration panel"""
        panel = QFrame()
        panel.setStyleSheet("""
            QFrame {
                background: rgba(255, 255, 255, 0.95);
                border: 2px solid rgba(255, 255, 255, 0.3);
                border-radius: 15px;
                padding: 10px;
            }
        """)
        
        layout = QVBoxLayout(panel)
        layout.setSpacing(15)
        
        # Title
        title = QLabel("⚙️ Configuration Hub")
        title.setFont(QFont('Segoe UI', 16, QFont.Bold))
        title.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Site configuration group
        site_group = QGroupBox("🏢 Site Configuration")
        site_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #e0e6ed;
                border-radius: 10px;
                margin-top: 10px;
                padding-top: 15px;
                color: #2c3e50;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px 0 10px;
                background: white;
            }
        """)
        site_layout = QGridLayout(site_group)
        site_layout.setSpacing(10)
        
        # Site combo
        site_label = QLabel("Site:")
        site_label.setStyleSheet("color: #2c3e50; font-weight: bold;")
        self.site_combo = QComboBox()
        sites = ["ZAZ1", "LBA4", "BHX4", "CDG7", "DTM1", "DTM2", "HAJ1", "WRO5", "TRN3", "BCN1", "MXP5"]
        self.site_combo.addItems(sites)
        self.site_combo.setEditable(True)
        self.site_combo.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 2px solid #e0e6ed;
                border-radius: 8px;
                background: white;
                color: #2c3e50;
                font-size: 13px;
                min-height: 20px;
            }
            QComboBox:focus {
                border-color: #667eea;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
        """)
        
        # Plan type
        plan_label = QLabel("Plan Type:")
        plan_label.setStyleSheet("color: #2c3e50; font-weight: bold;")
        self.plan_combo = QComboBox()
        self.plan_combo.addItems(["Prior-Day", "Next-Shift", "SOS", "Real-Time"])
        self.plan_combo.setStyleSheet(self.site_combo.styleSheet())
        
        # Shift
        shift_label = QLabel("Shift:")
        shift_label.setStyleSheet("color: #2c3e50; font-weight: bold;")
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
        datetime_group = QGroupBox("⏰ Time Configuration")
        datetime_group.setStyleSheet(site_group.styleSheet())
        datetime_layout = QVBoxLayout(datetime_group)
        datetime_layout.setSpacing(10)
        
        self.sos_widget = SmartDateTimeWidget("🌅 Start of Shift (SOS)")
        self.eos_widget = SmartDateTimeWidget("🌆 End of Shift (EOS)")
        
        datetime_layout.addWidget(self.sos_widget)
        datetime_layout.addWidget(self.eos_widget)
        
        # Smart shift buttons
        shift_buttons = QHBoxLayout()
        shift_buttons.setSpacing(5)
        
        morning_btn = ModernButton("🌅 Morning", "info")
        evening_btn = ModernButton("🌆 Evening", "warning") 
        night_btn = ModernButton("🌙 Night", "primary")
        
        morning_btn.clicked.connect(lambda: self.set_shift(6, 14))
        evening_btn.clicked.connect(lambda: self.set_shift(14, 22))
        night_btn.clicked.connect(lambda: self.set_shift(22, 6, True))
        
        shift_buttons.addWidget(morning_btn)
        shift_buttons.addWidget(evening_btn)
        shift_buttons.addWidget(night_btn)
        
        datetime_layout.addLayout(shift_buttons)
        layout.addWidget(datetime_group)
        
        # PPR_Q Special Configuration
        ppr_q_group = QGroupBox("🆕 PPR_Q Advanced Settings")
        ppr_q_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 3px solid #ffd700;
                border-radius: 10px;
                margin-top: 10px;
                padding-top: 15px;
                color: #e6c200;
                background: #fffacd;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px 0 10px;
                background: white;
                color: #e6c200;
            }
        """)
        ppr_q_layout = QVBoxLayout(ppr_q_group)
        
        self.ppr_q_enabled = QCheckBox("Enable PPR_Q Minute-Level Analysis")
        self.ppr_q_enabled.setStyleSheet("""
            QCheckBox {
                color: #2c3e50; 
                font-weight: bold;
                font-size: 13px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border-radius: 9px;
                border: 2px solid #ffd700;
                background: white;
            }
            QCheckBox::indicator:checked {
                background: #ffd700;
                border-color: #e6c200;
            }
        """)
        self.ppr_q_enabled.setChecked(True)
        
        ppr_q_info = QLabel("🔥 NEW: Get PPR data with minute-level precision!\nPerfect for detailed shift analysis and real-time monitoring.")
        ppr_q_info.setStyleSheet("color: #e6c200; font-style: italic; margin: 10px; font-size: 12px;")
        ppr_q_info.setWordWrap(True)
        
        ppr_q_layout.addWidget(self.ppr_q_enabled)
        ppr_q_layout.addWidget(ppr_q_info)
        layout.addWidget(ppr_q_group)
        
        layout.addStretch()
        return panel
    
    def create_module_panel(self):
        """Create the module selection panel"""
        panel = QFrame()
        panel.setStyleSheet("""
            QFrame {
                background: rgba(255, 255, 255, 0.95);
                border: 2px solid rgba(255, 255, 255, 0.3);
                border-radius: 15px;
                padding: 10px;
            }
        """)
        
        layout = QVBoxLayout(panel)
        layout.setSpacing(10)
        
        # Title
        title = QLabel("🧩 Module Selection Hub")
        title.setFont(QFont('Segoe UI', 16, QFont.Bold))
        title.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Module selector
        self.module_selector = AdvancedModuleSelector()
        layout.addWidget(self.module_selector)
        
        return panel
    
    def create_action_panel(self):
        """Create the action panel"""
        panel = QFrame()
        panel.setStyleSheet("""
            QFrame {
                background: rgba(255, 255, 255, 0.95);
                border: 2px solid rgba(255, 255, 255, 0.3);
                border-radius: 15px;
                padding: 10px;
            }
        """)
        
        layout = QVBoxLayout(panel)
        layout.setSpacing(10)
        
        # Output configuration
        output_group = QGroupBox("📁 Output Configuration")
        output_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #e0e6ed;
                border-radius: 10px;
                margin-top: 10px;
                padding-top: 15px;
                color: #2c3e50;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px 0 10px;
                background: white;
            }
        """)
        output_layout = QHBoxLayout(output_group)
        
        self.output_path = QLineEdit()
        self.output_path.setPlaceholderText("Select output directory...")
        self.output_path.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 2px solid #e0e6ed;
                border-radius: 8px;
                background: white;
                color: #2c3e50;
                font-size: 13px;
            }
            QLineEdit:focus {
                border-color: #667eea;
            }
        """)
        
        browse_btn = ModernButton("📁 Browse", "info")
        browse_btn.clicked.connect(self.browse_output)
        
        output_layout.addWidget(self.output_path, 1)
        output_layout.addWidget(browse_btn, 0)
        layout.addWidget(output_group)
        
        # Action buttons
        action_layout = QHBoxLayout()
        action_layout.setSpacing(10)
        
        preview_btn = ModernButton("👁️ Preview JSON", "info")
        preview_btn.clicked.connect(self.preview_json)
        
        save_btn = ModernButton("💾 Save Only", "primary")
        save_btn.clicked.connect(self.save_only)
        
        generate_btn = ModernButton("🚀 Generate & Run", "success")
        generate_btn.clicked.connect(self.generate_and_run)
        
        action_layout.addWidget(preview_btn)
        action_layout.addWidget(save_btn)
        action_layout.addWidget(generate_btn)
        
        layout.addLayout(action_layout)
        
        return panel
    
    def set_defaults(self):
        """Set intelligent defaults"""
        self.site_combo.setCurrentText("DTM2")
        self.plan_combo.setCurrentText("Prior-Day")
        self.shift_combo.setCurrentText("LS")
        
        # Set default times
        current = QDateTime.currentDateTime()
        self.sos_widget.set_datetime(current.addSecs(-3600))  # 1 hour ago
        self.eos_widget.set_datetime(current)
        
        # Set default output path
        self.output_path.setText(os.getcwd())
        
        # Select essential modules including PPR_Q
        self.module_selector.select_essential()
    
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
    
    def browse_output(self):
        """Browse for output directory"""
        path = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if path:
            self.output_path.setText(path)
    
    def get_params_dict(self):
        """Generate parameters dictionary"""
        modules = self.module_selector.get_selected_modules()
        
        # Add PPR_Q if enabled and not already selected
        if self.ppr_q_enabled.isChecked() and "PPR_Q" not in modules:
            modules.append("PPR_Q")
        
        params = {
            "Site": self.site_combo.currentText(),
            "plan_type": self.plan_combo.currentText(),
            "shift": self.shift_combo.currentText(),
            "SOSdatetime": self.sos_widget.get_datetime().toString("yyyy-MM-dd HH:mm:ss"),
            "EOSdatetime": self.eos_widget.get_datetime().toString("yyyy-MM-dd HH:mm:ss"),
            "Modules": modules,
            "GeneratedBy": "OnePyFlow Params Generator V2.0",
            "GeneratedAt": datetime.now().isoformat(),
            "PPR_Q_Enabled": self.ppr_q_enabled.isChecked()
        }
        
        return params
    
    def preview_json(self):
        """Preview the JSON with syntax highlighting"""
        params = self.get_params_dict()
        json_str = json.dumps(params, indent=4)
        
        dialog = QDialog(self)
        dialog.setWindowTitle("🔍 JSON Preview")
        dialog.setMinimumSize(600, 500)
        dialog.setStyleSheet("""
            QDialog {
                background: white;
                border-radius: 10px;
            }
        """)
        
        layout = QVBoxLayout(dialog)
        
        text_edit = QTextEdit()
        text_edit.setPlainText(json_str)
        text_edit.setStyleSheet("""
            QTextEdit {
                background: #2d3748;
                color: #e2e8f0;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 12px;
                border-radius: 8px;
                padding: 15px;
                border: 2px solid #4a5568;
            }
        """)
        text_edit.setReadOnly(True)
        layout.addWidget(text_edit)
        
        close_btn = ModernButton("✅ Looks Good!", "success")
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)
        
        dialog.exec_()
    
    def save_only(self):
        """Save parameters without running"""
        self.save_params(run_after=False)
    
    def generate_and_run(self):
        """Generate parameters and run OneFlow"""
        self.save_params(run_after=True)
    
    def save_params(self, run_after=False):
        """Save parameters to file"""
        params = self.get_params_dict()
        
        if not params["Modules"]:
            QMessageBox.warning(self, "⚠️ Warning", "Please select at least one module!")
            return
        
        output_dir = self.output_path.text()
        if not os.path.isdir(output_dir):
            QMessageBox.warning(self, "⚠️ Warning", "Invalid output directory!")
            return
        
        file_path = os.path.join(output_dir, "OnePyFlowParams.json")
        
        try:
            with open(file_path, 'w') as f:
                json.dump(params, f, indent=4)
            
            # Success message
            msg = QMessageBox(self)
            msg.setWindowTitle("🎉 Success!")
            msg.setText(f"Parameters saved successfully!\n\n📁 {file_path}")
            msg.setStyleSheet("""
                QMessageBox {
                    background: white;
                    border-radius: 10px;
                }
                QMessageBox QPushButton {
                    background: #667eea;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    padding: 8px 16px;
                    font-weight: bold;
                }
            """)
            
            if run_after:
                msg.setInformativeText("🚀 OneFlow will now launch with these parameters!")
                msg.exec_()
                self.close()  # Close the generator
                return True  # Signal to run OneFlow
            else:
                msg.exec_()
                
        except Exception as e:
            QMessageBox.critical(self, "❌ Error", f"Failed to save parameters:\n{str(e)}")

        return False

def main():
    """Launch the params generator"""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # Set application properties
    app.setApplicationName("OnePyFlow Params Generator V2.0")
    app.setApplicationVersion("2.0.0")
    
    window = OnePyFlowParamsGenerator()
    window.show()

    result = app.exec_()
    sys.exit(result)

if __name__ == "__main__":
    main()