"""
🚀 Stunning OnePyFlow Params Generator - Complete Visual Makeover
Beautiful glassmorphism design with modern aesthetics
"""

import sys
import os
import json
import subprocess
from datetime import datetime
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from .modern_theme import ModernTheme
from .beautiful_schedule import BeautifulSchedulePicker, ModernShiftPresets
from .fc_configs import FCConfigs

class StunningCard(QFrame):
    """Beautiful glassmorphism card"""
    
    def __init__(self, title="", icon=""):
        super().__init__()
        self.setFrameStyle(QFrame.NoFrame)
        self.setup_ui(title, icon)
        
    def setup_ui(self, title, icon):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)
        
        if title:
            header_layout = QHBoxLayout()
            
            if icon:
                icon_label = QLabel(icon)
                icon_label.setStyleSheet(f"""
                    font-size: 28px;
                    color: {ModernTheme.COLORS['accent_primary']};
                    margin-right: 12px;
                """)
                header_layout.addWidget(icon_label)
                
            title_label = QLabel(title)
            title_label.setStyleSheet(f"""
                color: {ModernTheme.COLORS['text_primary']};
                font-family: {ModernTheme.FONTS['heading']['family']};
                font-size: {ModernTheme.FONTS['heading']['size']}px;
                font-weight: {ModernTheme.FONTS['heading']['weight']};
                margin: 0;
            """)
            header_layout.addWidget(title_label)
            header_layout.addStretch()
            layout.addLayout(header_layout)
            
        self.setStyleSheet(ModernTheme.get_glass_card_style())

class ModernInput(QWidget):
    """Modern input field with label"""
    
    def __init__(self, label, widget_type="combo", items=None):
        super().__init__()
        self.setup_ui(label, widget_type, items)
        
    def setup_ui(self, label, widget_type, items):
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        
        # Label
        label_widget = QLabel(label)
        label_widget.setStyleSheet(f"""
            color: {ModernTheme.COLORS['text_secondary']};
            font-family: {ModernTheme.FONTS['body']['family']};
            font-size: {ModernTheme.FONTS['small']['size']}px;
            font-weight: bold;
            margin-bottom: 4px;
        """)
        layout.addWidget(label_widget)
        
        # Input widget
        if widget_type == "combo":
            self.widget = QComboBox()
            if items:
                self.widget.addItems(items)
        elif widget_type == "line":
            self.widget = QLineEdit()
        elif widget_type == "datetime":
            self.widget = QDateTimeEdit()
            self.widget.setDisplayFormat("yyyy-MM-dd HH:mm")
            
        self.widget.setStyleSheet(ModernTheme.get_modern_input_style())
        layout.addWidget(self.widget)

class ModernButton(QPushButton):
    """Modern button with beautiful styling"""
    
    def __init__(self, text, variant="primary", icon=""):
        super().__init__()
        self.variant = variant
        if icon:
            self.setText(f"{icon} {text}")
        else:
            self.setText(text)
        self.setStyleSheet(ModernTheme.get_modern_button_style(variant))
        self.setCursor(Qt.PointingHandCursor)

class BeautifulModuleSelector(QWidget):
    """Beautiful module selector with modern design"""
    
    def __init__(self):
        super().__init__()
        self.setup_modules()
        self.setup_ui()
        
    def setup_modules(self):
        self.modules = {
            "Performance": {
                "modules": ["Echo", "PHC", "HCTool", "BackLog", "PPR", "PPR_Q", "ALPS", "RODEO"],
                "icon": "⚡",
                "description": "Core performance monitoring and analysis"
            },
            "Analytics": {
                "modules": ["Galaxy", "Galaxy_percentages", "Galaxy2", "Galaxy2_values", "ICQA", "F2P", "kNekro", "SSP", "SSPOT"],
                "icon": "📊",
                "description": "Data analytics and reporting modules"
            },
            "Transport": {
                "modules": ["DockMaster", "DockMasterFiltered", "DockMaster2", "DockMaster2Filtered", "DockFlow", "YMS", "FMC", "CarrierMatrix", "SCACs", "SPARK"],
                "icon": "🚛",
                "description": "Logistics and transportation data"
            },
            "Support": {
                "modules": ["ALPS_RC_Sort", "ALPSRoster", "QuipCSV", "VIP", "IBBT"],
                "icon": "🛠️",
                "description": "Operations and support modules"
            }
        }
        
        self.essential_modules = ["Echo", "PPR_Q", "ALPS", "Galaxy", "DockMaster", "SPARK"]
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        # Search bar
        search_container = QWidget()
        search_layout = QHBoxLayout(search_container)
        search_layout.setContentsMargins(0, 0, 0, 0)
        
        search_icon = QLabel("🔍")
        search_icon.setStyleSheet(f"font-size: 18px; color: {ModernTheme.COLORS['text_muted']};")
        
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search modules...")
        self.search_bar.setStyleSheet(ModernTheme.get_modern_input_style())
        self.search_bar.textChanged.connect(self.filter_modules)
        
        search_layout.addWidget(search_icon)
        search_layout.addWidget(self.search_bar)
        layout.addWidget(search_container)
        
        # Module tabs
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet(ModernTheme.get_modern_tab_style())
        
        self.module_checkboxes = {}
        self.create_module_tabs()
        layout.addWidget(self.tab_widget)
        
        # Quick selection buttons
        quick_layout = QHBoxLayout()
        quick_layout.setSpacing(12)
        
        all_btn = ModernButton("All Modules", "success", "✅")
        essential_btn = ModernButton("Essential", "primary", "⭐")
        clear_btn = ModernButton("Clear All", "error", "🗑️")
        
        all_btn.clicked.connect(self.select_all)
        essential_btn.clicked.connect(self.select_essential)
        clear_btn.clicked.connect(self.clear_all)
        
        quick_layout.addWidget(all_btn)
        quick_layout.addWidget(essential_btn)
        quick_layout.addWidget(clear_btn)
        layout.addLayout(quick_layout)
        
    def create_module_tabs(self):
        for category, config in self.modules.items():
            scroll_area = QScrollArea()
            scroll_area.setStyleSheet(ModernTheme.get_scroll_area_style())
            
            scroll_widget = QWidget()
            scroll_layout = QVBoxLayout(scroll_widget)
            scroll_layout.setSpacing(12)
            
            # Category header
            header_layout = QHBoxLayout()
            icon_label = QLabel(config['icon'])
            icon_label.setStyleSheet(f"font-size: 24px; margin-right: 8px;")
            
            desc_label = QLabel(config['description'])
            desc_label.setStyleSheet(f"""
                color: {ModernTheme.COLORS['text_muted']};
                font-style: italic;
                font-size: {ModernTheme.FONTS['small']['size']}px;
            """)
            
            header_layout.addWidget(icon_label)
            header_layout.addWidget(desc_label)
            header_layout.addStretch()
            scroll_layout.addLayout(header_layout)
            
            # Module checkboxes
            for module in config['modules']:
                checkbox = QCheckBox(module)
                checkbox.setStyleSheet(ModernTheme.get_modern_checkbox_style())
                
                # Special styling for PPR_Q
                if module == "PPR_Q":
                    checkbox.setStyleSheet(ModernTheme.get_modern_checkbox_style() + f"""
                        QCheckBox {{
                            background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                                stop:0 {ModernTheme.COLORS['accent_warning']}, 
                                stop:1 rgba(255, 230, 109, 0.3));
                            border-radius: 12px;
                            padding: 16px;
                            margin: 4px;
                            font-weight: bold;
                        }}
                    """)
                    
                scroll_layout.addWidget(checkbox)
                self.module_checkboxes[module] = checkbox
                
            scroll_layout.addStretch()
            scroll_area.setWidget(scroll_widget)
            scroll_area.setWidgetResizable(True)
            self.tab_widget.addTab(scroll_area, f"{config['icon']} {category}")
            
    def filter_modules(self, text):
        search_text = text.lower()
        for module, checkbox in self.module_checkboxes.items():
            checkbox.setVisible(search_text in module.lower())
            
    def select_all(self):
        for checkbox in self.module_checkboxes.values():
            checkbox.setChecked(True)
            
    def select_essential(self):
        self.clear_all()
        for module, checkbox in self.module_checkboxes.items():
            if module in self.essential_modules:
                checkbox.setChecked(True)
                
    def clear_all(self):
        for checkbox in self.module_checkboxes.values():
            checkbox.setChecked(False)
            
    def get_selected_modules(self):
        return [module for module, checkbox in self.module_checkboxes.items() if checkbox.isChecked()]

class StunningParamsGenerator(QMainWindow):
    """Stunning OnePyFlow Params Generator with beautiful design"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🚀 OnePyFlow Params Generator V4.0 - Stunning Edition")
        self.setMinimumSize(1800, 1100)
        self.setup_ui()
        self.setup_connections()
        
    def setup_ui(self):
        # Apply main window styling
        self.setStyleSheet(ModernTheme.get_main_window_style())
        
        central = QWidget()
        self.setCentralWidget(central)
        
        # Main layout with proper spacing
        main_layout = QHBoxLayout(central)
        main_layout.setSpacing(32)
        main_layout.setContentsMargins(32, 32, 32, 32)
        
        # Left panel - Configuration
        left_panel = QWidget()
        left_panel.setMaximumWidth(700)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setSpacing(24)
        
        # Site configuration card
        site_card = StunningCard("Site Configuration", "🏢")
        site_content = QWidget()
        site_layout = QGridLayout(site_content)
        site_layout.setSpacing(16)
        
        self.site_input = ModernInput("Fulfillment Center", "combo", FCConfigs.AVAILABLE_FCS)
        self.site_input.widget.setCurrentText("DTM2")
        
        self.plan_input = ModernInput("Plan Type", "combo", FCConfigs.PLAN_TYPES)
        
        site_layout.addWidget(self.site_input, 0, 0)
        site_layout.addWidget(self.plan_input, 0, 1)
        site_card.layout().addWidget(site_content)
        left_layout.addWidget(site_card)
        
        # Schedule configuration card
        schedule_card = StunningCard("Schedule Configuration", "⏰")
        schedule_content = QWidget()
        schedule_layout = QVBoxLayout(schedule_content)
        schedule_layout.setSpacing(20)
        
        # Beautiful schedule picker
        self.schedule_picker = BeautifulSchedulePicker("DTM2")
        schedule_layout.addWidget(self.schedule_picker)
        
        # Modern shift presets
        self.shift_presets = ModernShiftPresets("DTM2")
        schedule_layout.addWidget(self.shift_presets)
        
        # DateTime inputs
        datetime_layout = QHBoxLayout()
        datetime_layout.setSpacing(16)
        
        self.start_input = ModernInput("Start Time", "datetime")
        self.start_input.widget.setDateTime(QDateTime.currentDateTime().addSecs(-3600))
        
        self.end_input = ModernInput("End Time", "datetime")
        self.end_input.widget.setDateTime(QDateTime.currentDateTime())
        
        datetime_layout.addWidget(self.start_input)
        datetime_layout.addWidget(self.end_input)
        schedule_layout.addLayout(datetime_layout)
        
        schedule_card.layout().addWidget(schedule_content)
        left_layout.addWidget(schedule_card)
        
        # Actions card
        actions_card = StunningCard("Actions", "🎯")
        actions_content = QWidget()
        actions_layout = QVBoxLayout(actions_content)
        actions_layout.setSpacing(16)
        
        # Output path
        self.output_input = ModernInput("Output Directory", "line")
        self.output_input.widget.setText(os.getcwd())
        
        path_layout = QHBoxLayout()
        path_layout.addWidget(self.output_input)
        browse_btn = ModernButton("Browse", "secondary", "📁")
        browse_btn.clicked.connect(self.browse_output)
        path_layout.addWidget(browse_btn)
        actions_layout.addLayout(path_layout)
        
        # Action buttons
        self.preview_btn = ModernButton("Preview JSON", "secondary", "👁️")
        self.save_btn = ModernButton("Save Parameters", "primary", "💾")
        self.run_btn = ModernButton("Generate & Run OnePyFlow", "success", "🚀")
        
        actions_layout.addWidget(self.preview_btn)
        actions_layout.addWidget(self.save_btn)
        actions_layout.addWidget(self.run_btn)
        
        actions_card.layout().addWidget(actions_content)
        left_layout.addWidget(actions_card)
        
        # Right panel - Module selection
        right_panel = StunningCard("Module Selection Hub", "🧩")
        self.module_selector = BeautifulModuleSelector()
        right_panel.layout().addWidget(self.module_selector)
        
        # Add panels to main layout
        main_layout.addWidget(left_panel, 2)
        main_layout.addWidget(right_panel, 3)
        
    def setup_connections(self):
        self.site_input.widget.currentTextChanged.connect(self.on_site_changed)
        self.shift_presets.shift_selected.connect(self.on_shift_selected)
        self.schedule_picker.schedule_changed.connect(self.on_schedule_changed)
        
        self.preview_btn.clicked.connect(self.preview_parameters)
        self.save_btn.clicked.connect(self.save_parameters)
        self.run_btn.clicked.connect(self.generate_and_run)
        
    def on_site_changed(self, site):
        self.schedule_picker.set_fc(site)
        self.shift_presets.set_fc(site)
        
    def on_shift_selected(self, shift):
        self.schedule_picker.set_shift(shift)
        
    def on_schedule_changed(self, start_hour, end_hour):
        current_date = QDateTime.currentDateTime().date()
        
        start_h = int(start_hour)
        start_m = int((start_hour % 1) * 60)
        end_h = int(end_hour)
        end_m = int((end_hour % 1) * 60)
        
        start_dt = QDateTime(current_date, QTime(start_h, start_m))
        
        if end_hour < start_hour:
            end_dt = QDateTime(current_date.addDays(1), QTime(end_h, end_m))
        else:
            end_dt = QDateTime(current_date, QTime(end_h, end_m))
            
        self.start_input.widget.setDateTime(start_dt)
        self.end_input.widget.setDateTime(end_dt)
        
    def browse_output(self):
        path = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if path:
            self.output_input.widget.setText(path)
            
    def get_parameters(self):
        return {
            "Site": self.site_input.widget.currentText(),
            "plan_type": self.plan_input.widget.currentText(),
            "shift": "Custom",
            "SOSdatetime": self.start_input.widget.dateTime().toString("yyyy-MM-dd HH:mm:ss"),
            "EOSdatetime": self.end_input.widget.dateTime().toString("yyyy-MM-dd HH:mm:ss"),
            "Modules": self.module_selector.get_selected_modules(),
            "GeneratedBy": "OnePyFlow Params Generator V4.0 - Stunning Edition",
            "GeneratedAt": datetime.now().isoformat()
        }
        
    def preview_parameters(self):
        params = self.get_parameters()
        if not params["Modules"]:
            QMessageBox.warning(self, "Warning", "Please select at least one module!")
            return
            
        dialog = QDialog(self)
        dialog.setWindowTitle("Preview Parameters")
        dialog.setMinimumSize(800, 600)
        dialog.setStyleSheet(ModernTheme.get_main_window_style())
        
        layout = QVBoxLayout(dialog)
        text = QTextEdit()
        text.setPlainText(json.dumps(params, indent=4))
        text.setReadOnly(True)
        text.setStyleSheet(f"""
            QTextEdit {{
                background: {ModernTheme.COLORS['bg_card']};
                border: 1px solid {ModernTheme.COLORS['border_light']};
                border-radius: 12px;
                padding: 16px;
                font-family: {ModernTheme.FONTS['code']['family']};
                font-size: {ModernTheme.FONTS['code']['size']}px;
                color: {ModernTheme.COLORS['text_primary']};
            }}
        """)
        layout.addWidget(text)
        
        close_btn = ModernButton("Close", "primary")
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)
        
        dialog.exec_()
        
    def save_parameters(self):
        params = self.get_parameters()
        if not params["Modules"]:
            QMessageBox.warning(self, "Warning", "Please select at least one module!")
            return
            
        file_path = os.path.join(self.output_input.widget.text(), "OnePyFlowParams.json")
        
        try:
            with open(file_path, 'w') as f:
                json.dump(params, f, indent=4)
            QMessageBox.information(self, "Success", f"Parameters saved to:\n{file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save: {e}")
            
    def generate_and_run(self):
        self.save_parameters()
        
        try:
            output_path = self.output_input.widget.text()
            main_py = os.path.join(output_path, "main.py")
            
            if not os.path.exists(main_py):
                main_py = os.path.join(os.path.dirname(output_path), "main.py")
                
            if os.path.exists(main_py):
                subprocess.Popen([sys.executable, main_py], cwd=os.path.dirname(main_py))
                QMessageBox.information(self, "Success", "OnePyFlow launched successfully!")
                self.close()
            else:
                QMessageBox.warning(self, "Warning", "main.py not found!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to launch: {e}")

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    window = StunningParamsGenerator()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
