"""
🚀 OnePyFlow Params Generator V3.0 - Central Orchestrator
Modular architecture with clean separation of concerns
"""

import sys
import os
import json
import subprocess
from datetime import datetime
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

# Import modular components
from .theme import Theme
from .config_panel import ConfigPanel
from .module_selector import ModuleSelector
from .actions_panel import ActionsPanel, PreviewDialog

class ParamsGenerator(QMainWindow):
    """Central orchestrator for OnePyFlow parameters generation"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🚀 OnePyFlow Params Generator V3.0 - Modular Edition")
        self.setMinimumSize(1600, 1000)
        self.setup_ui()
        self.setup_connections()
        self.apply_theme()
        
    def setup_ui(self):
        """Setup the main UI layout"""
        central = QWidget()
        self.setCentralWidget(central)
        
        # Main horizontal layout
        main_layout = QHBoxLayout(central)
        main_layout.setSpacing(Theme.SPACING['xl'])
        main_layout.setContentsMargins(
            Theme.SPACING['xl'], 
            Theme.SPACING['xl'], 
            Theme.SPACING['xl'], 
            Theme.SPACING['xl']
        )
        
        # Left panel - Configuration (40% width)
        left_panel = QWidget()
        left_panel.setMaximumWidth(640)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setSpacing(Theme.SPACING['lg'])
        
        # Configuration panel
        self.config_panel = ConfigPanel()
        left_layout.addWidget(self.config_panel)
        
        # Actions panel
        self.actions_panel = ActionsPanel()
        left_layout.addWidget(self.actions_panel)
        
        # Right panel - Module selection (60% width)
        right_panel = QGroupBox("🧩 Module Selection Hub")
        right_panel.setStyleSheet(Theme.STYLES['group_box'])
        right_layout = QVBoxLayout(right_panel)
        
        self.module_selector = ModuleSelector()
        right_layout.addWidget(self.module_selector)
        
        # Add panels to main layout
        main_layout.addWidget(left_panel, 2)
        main_layout.addWidget(right_panel, 3)
        
    def setup_connections(self):
        """Setup signal connections between components"""
        # Actions panel connections
        self.actions_panel.preview_btn.clicked.connect(self.preview_parameters)
        self.actions_panel.save_btn.clicked.connect(self.save_parameters)
        self.actions_panel.run_btn.clicked.connect(self.generate_and_run)
        
        # Config panel connections
        self.config_panel.fc_changed.connect(self.on_fc_changed)
        self.config_panel.schedule_changed.connect(self.on_schedule_changed)
        
    def apply_theme(self):
        """Apply the dark theme to the main window"""
        self.setStyleSheet(Theme.STYLES['main_window'])
        
    def on_fc_changed(self, fc):
        """Handle FC change events"""
        # Could add FC-specific module recommendations here
        pass
        
    def on_schedule_changed(self, start_dt, end_dt):
        """Handle schedule change events"""
        # Could add schedule validation here
        pass
        
    def get_parameters_dict(self):
        """Generate complete parameters dictionary"""
        config = self.config_panel.get_config()
        modules = self.module_selector.get_selected_modules()
        
        return {
            "Site": config['site'],
            "plan_type": config['plan_type'],
            "shift": "Custom",
            "SOSdatetime": config['start_datetime'].toString("yyyy-MM-dd HH:mm:ss"),
            "EOSdatetime": config['end_datetime'].toString("yyyy-MM-dd HH:mm:ss"),
            "Modules": modules,
            "GeneratedBy": "OnePyFlow Params Generator V3.0 - Modular Edition",
            "GeneratedAt": datetime.now().isoformat(),
            "OutputPath": self.actions_panel.get_output_path()
        }
        
    def validate_parameters(self):
        """Validate parameters before saving/running"""
        modules = self.module_selector.get_selected_modules()
        
        if not modules:
            QMessageBox.warning(
                self, 
                "Validation Error", 
                "Please select at least one module before proceeding."
            )
            return False
            
        output_path = self.actions_panel.get_output_path()
        if not os.path.exists(output_path):
            reply = QMessageBox.question(
                self,
                "Directory Not Found",
                f"Output directory does not exist:\n{output_path}\n\nCreate it?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                try:
                    os.makedirs(output_path, exist_ok=True)
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to create directory:\n{e}")
                    return False
            else:
                return False
                
        return True
        
    def preview_parameters(self):
        """Preview parameters in a dialog"""
        if not self.validate_parameters():
            return
            
        params = self.get_parameters_dict()
        dialog = PreviewDialog(params, self)
        dialog.exec_()
        
    def save_parameters(self):
        """Save parameters to JSON file"""
        if not self.validate_parameters():
            return
            
        params = self.get_parameters_dict()
        output_path = self.actions_panel.get_output_path()
        file_path = os.path.join(output_path, "OnePyFlowParams.json")
        
        try:
            with open(file_path, 'w') as f:
                json.dump(params, f, indent=4)
                
            QMessageBox.information(
                self, 
                "Success", 
                f"Parameters saved successfully to:\n{file_path}"
            )
            
        except Exception as e:
            QMessageBox.critical(
                self, 
                "Save Error", 
                f"Failed to save parameters:\n{e}"
            )
            
    def generate_and_run(self):
        """Generate parameters and run OnePyFlow"""
        if not self.validate_parameters():
            return
            
        # Save parameters first
        self.save_parameters()
        
        # Find and run main.py
        try:
            output_path = self.actions_panel.get_output_path()
            main_py_path = os.path.join(output_path, "main.py")
            
            if not os.path.exists(main_py_path):
                # Try parent directory
                parent_dir = os.path.dirname(output_path)
                main_py_path = os.path.join(parent_dir, "main.py")
                
            if os.path.exists(main_py_path):
                # Launch OnePyFlow
                subprocess.Popen(
                    [sys.executable, main_py_path], 
                    cwd=os.path.dirname(main_py_path)
                )
                
                QMessageBox.information(
                    self, 
                    "OnePyFlow Launched", 
                    f"OnePyFlow has been launched successfully!\n\nRunning: {main_py_path}"
                )
                
                # Close the params generator
                self.close()
                
            else:
                QMessageBox.warning(
                    self, 
                    "main.py Not Found", 
                    f"Could not find main.py in:\n{output_path}\nor its parent directory.\n\nPlease ensure OnePyFlow is properly installed."
                )
                
        except Exception as e:
            QMessageBox.critical(
                self, 
                "Launch Error", 
                f"Failed to launch OnePyFlow:\n{e}"
            )
            
    def load_existing_params(self, file_path):
        """Load existing parameters from JSON file"""
        try:
            with open(file_path, 'r') as f:
                params = json.load(f)
                
            # Update UI with loaded parameters
            config = {
                'site': params.get('Site', 'DTM2'),
                'plan_type': params.get('plan_type', 'Prior-Day'),
                'start_datetime': QDateTime.fromString(params.get('SOSdatetime', ''), "yyyy-MM-dd HH:mm:ss"),
                'end_datetime': QDateTime.fromString(params.get('EOSdatetime', ''), "yyyy-MM-dd HH:mm:ss")
            }
            
            self.config_panel.set_config(config)
            self.module_selector.set_selected_modules(params.get('Modules', []))
            
            if 'OutputPath' in params:
                self.actions_panel.set_output_path(params['OutputPath'])
                
        except Exception as e:
            QMessageBox.critical(
                self, 
                "Load Error", 
                f"Failed to load parameters:\n{e}"
            )

def main():
    """Launch the modular params generator"""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # Set application properties
    app.setApplicationName("OnePyFlow Params Generator")
    app.setApplicationVersion("3.0")
    app.setOrganizationName("OnePyFlow")
    
    window = ParamsGenerator()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
