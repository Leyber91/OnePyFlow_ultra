"""
🚀 Revolutionary OnePyFlow Params Generator
Complete redesign with modern UI and full functionality
"""

import sys
import os
import json
import subprocess
from datetime import datetime
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class RevolutionaryParamsGenerator(QMainWindow):
    """Revolutionary params generator with proper functionality"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🚀 OnePyFlow V3.0 - Revolutionary Edition")
        self.setMinimumSize(1600, 1000)
        self.setup_ui()
        
    def setup_ui(self):
        """Setup revolutionary UI"""
        self.setStyleSheet("""
            QMainWindow { background: #0a0a0a; color: white; }
            QWidget { background: #0a0a0a; color: white; }
            QGroupBox { 
                border: 2px solid #00ff88; 
                border-radius: 12px; 
                margin: 8px; 
                padding: 16px;
                font-weight: bold;
                font-size: 14px;
            }
            QComboBox, QLineEdit, QDateTimeEdit {
                background: #2a2a2a;
                border: 2px solid #333;
                border-radius: 8px;
                padding: 12px;
                font-size: 14px;
                min-height: 20px;
            }
            QComboBox:focus, QLineEdit:focus, QDateTimeEdit:focus {
                border-color: #00ff88;
            }
            QPushButton {
                background: #00ff88;
                color: black;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-weight: bold;
                font-size: 14px;
                min-height: 40px;
            }
            QPushButton:hover { background: #00cc66; }
            QPushButton:pressed { background: #009944; }
        """)
        
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Left panel
        left_panel = self.create_left_panel()
        left_panel.setMaximumWidth(600)
        
        # Right panel  
        right_panel = self.create_right_panel()
        
        layout.addWidget(left_panel, 2)
        layout.addWidget(right_panel, 3)
        
    def create_left_panel(self):
        """Create configuration panel"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(16)
        
        # Site config
        site_group = QGroupBox("🏢 Site Configuration")
        site_layout = QGridLayout(site_group)
        
        self.site_combo = QComboBox()
        sites = ["ZAZ1", "LBA4", "BHX4", "CDG7", "DTM1", "DTM2", "HAJ1", "WRO5", "TRN3"]
        self.site_combo.addItems(sites)
        self.site_combo.setCurrentText("DTM2")
        self.site_combo.currentTextChanged.connect(self.update_shifts)
        
        self.plan_combo = QComboBox()
        self.plan_combo.addItems(["Prior-Day", "Next-Shift", "SOS", "Real-Time"])
        
        site_layout.addWidget(QLabel("Site:"), 0, 0)
        site_layout.addWidget(self.site_combo, 0, 1)
        site_layout.addWidget(QLabel("Plan:"), 1, 0)
        site_layout.addWidget(self.plan_combo, 1, 1)
        
        layout.addWidget(site_group)
        
        # Schedule config
        schedule_group = QGroupBox("⏰ Schedule Configuration")
        schedule_layout = QVBoxLayout(schedule_group)
        
        # Shift buttons
        self.shift_buttons_widget = QWidget()
        self.shift_buttons_layout = QGridLayout(self.shift_buttons_widget)
        schedule_layout.addWidget(self.shift_buttons_widget)
        
        # DateTime inputs
        dt_layout = QGridLayout()
        self.start_dt = QDateTimeEdit(QDateTime.currentDateTime().addSecs(-3600))
        self.start_dt.setDisplayFormat("yyyy-MM-dd HH:mm")
        self.end_dt = QDateTimeEdit(QDateTime.currentDateTime())
        self.end_dt.setDisplayFormat("yyyy-MM-dd HH:mm")
        
        dt_layout.addWidget(QLabel("Start:"), 0, 0)
        dt_layout.addWidget(self.start_dt, 0, 1)
        dt_layout.addWidget(QLabel("End:"), 1, 0)
        dt_layout.addWidget(self.end_dt, 1, 1)
        schedule_layout.addLayout(dt_layout)
        
        layout.addWidget(schedule_group)
        
        # Actions
        actions_group = QGroupBox("🎯 Actions")
        actions_layout = QVBoxLayout(actions_group)
        
        # Output path
        output_layout = QHBoxLayout()
        self.output_path = QLineEdit(os.getcwd())
        browse_btn = QPushButton("Browse")
        browse_btn.clicked.connect(self.browse_output)
        output_layout.addWidget(self.output_path)
        output_layout.addWidget(browse_btn)
        actions_layout.addLayout(output_layout)
        
        # Action buttons
        self.preview_btn = QPushButton("👁️ Preview JSON")
        self.save_btn = QPushButton("💾 Save Only")
        self.run_btn = QPushButton("🚀 Generate & Run OnePyFlow")
        
        self.preview_btn.clicked.connect(self.preview_params)
        self.save_btn.clicked.connect(self.save_params)
        self.run_btn.clicked.connect(self.generate_and_run)
        
        actions_layout.addWidget(self.preview_btn)
        actions_layout.addWidget(self.save_btn)
        actions_layout.addWidget(self.run_btn)
        
        layout.addWidget(actions_group)
        
        self.update_shifts("DTM2")
        return widget
        
    def create_right_panel(self):
        """Create module selection panel"""
        group = QGroupBox("🧩 Module Selection")
        layout = QVBoxLayout(group)
        
        # Search
        self.search = QLineEdit()
        self.search.setPlaceholderText("🔍 Search modules...")
        self.search.textChanged.connect(self.filter_modules)
        layout.addWidget(self.search)
        
        # Module checkboxes
        scroll = QScrollArea()
        scroll_widget = QWidget()
        self.modules_layout = QVBoxLayout(scroll_widget)
        
        modules = [
            "Echo", "PHC", "HCTool", "BackLog", "PPR", "PPR_Q", "ALPS", "RODEO",
            "Galaxy", "Galaxy2", "ICQA", "F2P", "kNekro", "SSP", "SSPOT",
            "DockMaster", "DockMaster2", "DockFlow", "YMS", "FMC", 
            "CarrierMatrix", "SCACs", "SPARK", "VIP", "IBBT"
        ]
        
        self.module_checkboxes = {}
        for module in modules:
            cb = QCheckBox(module)
            cb.setStyleSheet("""
                QCheckBox { 
                    font-size: 14px; 
                    padding: 8px; 
                    spacing: 12px; 
                }
                QCheckBox::indicator {
                    width: 20px; height: 20px;
                    border: 2px solid #333;
                    border-radius: 4px;
                    background: #2a2a2a;
                }
                QCheckBox::indicator:checked {
                    background: #00ff88;
                    border-color: #00ff88;
                }
            """)
            
            if module == "PPR_Q":
                cb.setStyleSheet(cb.styleSheet() + """
                    QCheckBox { 
                        background: #ffaa00; 
                        color: black; 
                        border-radius: 8px; 
                        padding: 12px;
                        font-weight: bold;
                    }
                """)
                
            self.modules_layout.addWidget(cb)
            self.module_checkboxes[module] = cb
            
        scroll.setWidget(scroll_widget)
        scroll.setWidgetResizable(True)
        layout.addWidget(scroll)
        
        # Quick buttons
        quick_layout = QHBoxLayout()
        all_btn = QPushButton("All")
        essential_btn = QPushButton("Essential")
        clear_btn = QPushButton("Clear")
        
        all_btn.clicked.connect(lambda: [cb.setChecked(True) for cb in self.module_checkboxes.values()])
        essential_btn.clicked.connect(self.select_essential)
        clear_btn.clicked.connect(lambda: [cb.setChecked(False) for cb in self.module_checkboxes.values()])
        
        quick_layout.addWidget(all_btn)
        quick_layout.addWidget(essential_btn)
        quick_layout.addWidget(clear_btn)
        layout.addLayout(quick_layout)
        
        return group
        
    def update_shifts(self, fc):
        """Update shift buttons for FC"""
        # Clear existing buttons
        while self.shift_buttons_layout.count():
            child = self.shift_buttons_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
                
        shifts = self.get_fc_shifts(fc)
        colors = ["#00ff88", "#ffaa00", "#0088ff", "#ff4444", "#aa44ff"]
        
        row, col = 0, 0
        for i, (shift, times) in enumerate(shifts.items()):
            btn = QPushButton(shift.upper())
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: {colors[i % len(colors)]};
                    color: black;
                    font-weight: bold;
                    border-radius: 8px;
                    padding: 12px;
                    min-height: 40px;
                }}
            """)
            btn.setToolTip(f"{shift}: {times[0]:.2f}h - {times[1]:.2f}h")
            btn.clicked.connect(lambda checked, s=times: self.set_shift_times(s))
            
            self.shift_buttons_layout.addWidget(btn, row, col)
            col += 1
            if col > 2:
                col = 0
                row += 1
                
    def get_fc_shifts(self, fc):
        """Get shifts for FC"""
        configs = {
            'BHX4': {'es': (7.5, 18), 'ns': (18.75, 29.25)},
            'CDG7': {'es': (5.5, 13), 'ls': (13.5, 21), 'ns': (21.5, 29)},
            'DTM1': {'es': (6.25, 15), 'ls': (15, 23.75), 'ns': (23.75, 30.25)},
            'DTM2': {'es': (6.25, 15), 'ls': (15, 23.75), 'ns': (23.75, 30.25)},
            'HAJ1': {'es': (6, 14), 'ls': (14, 22), 'ns': (22, 30)},
            'LBA4': {'es': (7.75, 18.25), 'ns': (18.75, 29.5)},
            'TRN3': {'es': (6, 14), 'ls': (14.75, 22.5), 'ns': (22.5, 30)},
            'WRO5': {'es': (6.5, 17), 'ns': (18, 28.5)},
            'ZAZ1': {'es': (6, 14.5), 'ls': (14.5, 23), 'ns': (23, 30)}
        }
        return configs.get(fc, {'es': (6, 14), 'ls': (14, 22), 'ns': (22, 30)})
        
    def set_shift_times(self, times):
        """Set shift times"""
        start_h, end_h = times
        current_date = QDateTime.currentDateTime().date()
        
        start_hour = int(start_h)
        start_min = int((start_h % 1) * 60)
        end_hour = int(end_h % 24)
        end_min = int((end_h % 1) * 60)
        
        start_dt = QDateTime(current_date, QTime(start_hour, start_min))
        
        if end_h >= 24:
            end_dt = QDateTime(current_date.addDays(1), QTime(end_hour, end_min))
        else:
            end_dt = QDateTime(current_date, QTime(end_hour, end_min))
            
        self.start_dt.setDateTime(start_dt)
        self.end_dt.setDateTime(end_dt)
        
    def filter_modules(self, text):
        """Filter modules"""
        for module, cb in self.module_checkboxes.items():
            cb.setVisible(text.lower() in module.lower())
            
    def select_essential(self):
        """Select essential modules"""
        essential = ["Echo", "PPR_Q", "ALPS", "Galaxy", "DockMaster", "SPARK"]
        for module, cb in self.module_checkboxes.items():
            cb.setChecked(module in essential)
            
    def browse_output(self):
        """Browse output directory"""
        path = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if path:
            self.output_path.setText(path)
            
    def get_params(self):
        """Get parameters"""
        return {
            "Site": self.site_combo.currentText(),
            "plan_type": self.plan_combo.currentText(),
            "shift": "Custom",
            "SOSdatetime": self.start_dt.dateTime().toString("yyyy-MM-dd HH:mm:ss"),
            "EOSdatetime": self.end_dt.dateTime().toString("yyyy-MM-dd HH:mm:ss"),
            "Modules": [m for m, cb in self.module_checkboxes.items() if cb.isChecked()],
            "GeneratedBy": "OnePyFlow V3.0 Revolutionary",
            "GeneratedAt": datetime.now().isoformat()
        }
        
    def preview_params(self):
        """Preview parameters"""
        params = self.get_params()
        dialog = QDialog(self)
        dialog.setWindowTitle("Preview Parameters")
        dialog.setMinimumSize(600, 500)
        
        layout = QVBoxLayout(dialog)
        text = QTextEdit()
        text.setPlainText(json.dumps(params, indent=4))
        text.setReadOnly(True)
        layout.addWidget(text)
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)
        
        dialog.exec_()
        
    def save_params(self):
        """Save parameters"""
        params = self.get_params()
        if not params["Modules"]:
            QMessageBox.warning(self, "Warning", "Select at least one module!")
            return
            
        file_path = os.path.join(self.output_path.text(), "OnePyFlowParams.json")
        
        try:
            with open(file_path, 'w') as f:
                json.dump(params, f, indent=4)
            QMessageBox.information(self, "Success", f"Saved to {file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save: {e}")
            
    def generate_and_run(self):
        """Generate parameters and run OnePyFlow"""
        self.save_params()
        
        # Run main.py
        try:
            main_py = os.path.join(os.path.dirname(self.output_path.text()), "main.py")
            if os.path.exists(main_py):
                subprocess.Popen([sys.executable, main_py], cwd=os.path.dirname(main_py))
                QMessageBox.information(self, "Success", "OnePyFlow launched!")
                self.close()
            else:
                QMessageBox.warning(self, "Warning", "main.py not found!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to run: {e}")

def main():
    """Launch revolutionary params generator"""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    window = RevolutionaryParamsGenerator()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
