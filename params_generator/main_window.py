"""
🚀 Main Window for OnePyFlow Params Generator
Dark Matrix Theme with Adaptive UI
"""

import sys
import os
import json
from datetime import datetime
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from .components import ConfigurationPanel, AdvancedModuleSelector, ActionPanel, ModernButton
from .themes import DarkMatrixTheme

class OnePyFlowParamsGenerator(QMainWindow):
    """🚀 OnePyFlow Parameters Generator V2.0 - Dark Matrix Edition"""
    
    def __init__(self):
        super().__init__()
        self.scale_factor = self.calculate_scale_factor()
        self.setWindowTitle("🚀 OnePyFlow Params Generator V2.0 - Dark Matrix Edition")
        self.setMinimumSize(int(1600 * self.scale_factor), int(1000 * self.scale_factor))
        self.setup_ui()
        self.set_defaults()
        
    def calculate_scale_factor(self):
        """Calculate scale factor based on screen size with better proportions"""
        screen = QApplication.primaryScreen()
        size = screen.size()
        # Base scale on screen width, with better bounds for readability
        base_width = 1920
        scale = size.width() / base_width
        # Use a more generous scale range for better visibility
        return max(1.0, min(1.8, scale))  # Clamp between 1.0 and 1.8
        
    def setup_ui(self):
        """Setup the main UI with adaptive sizing"""
        # Set main window style
        self.setStyleSheet(f"""
            QMainWindow {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {DarkMatrixTheme.COLORS['bg_primary']}, 
                    stop:1 {DarkMatrixTheme.COLORS['bg_secondary']});
            }}
        """)
        
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        
        # Main layout - horizontal split with adaptive sizing
        main_layout = QHBoxLayout(central)
        main_layout.setSpacing(int(12 * self.scale_factor))
        main_layout.setContentsMargins(
            int(12 * self.scale_factor), 
            int(12 * self.scale_factor), 
            int(12 * self.scale_factor), 
            int(12 * self.scale_factor)
        )
        
        # Left container - Configuration + Actions
        left_container = QWidget()
        left_layout = QVBoxLayout(left_container)
        left_layout.setSpacing(int(8 * self.scale_factor))
        
        # Create panels with scale factor
        self.config_panel = ConfigurationPanel(self.scale_factor)
        self.action_panel = ActionPanel(self.scale_factor)
        
        left_layout.addWidget(self.config_panel, 1)
        left_layout.addWidget(self.action_panel, 0)
        
        # Right panel - Module selection  
        self.module_panel = self.create_module_panel()
        
        # Add to main layout with proportional sizing
        main_layout.addWidget(left_container, 1)
        main_layout.addWidget(self.module_panel, 2)
        
        # Connect action buttons
        self.action_panel.preview_btn.clicked.connect(self.preview_json)
        self.action_panel.save_btn.clicked.connect(self.save_only)
        self.action_panel.generate_btn.clicked.connect(self.generate_and_run)
        
    def create_module_panel(self):
        """Create the module selection panel"""
        panel = QFrame()
        panel.setStyleSheet(f"""
            QFrame {{
                background: {DarkMatrixTheme.COLORS['bg_secondary']};
                border: 2px solid {DarkMatrixTheme.COLORS['border']};
                border-radius: {int(15 * self.scale_factor)}px;
                padding: {int(10 * self.scale_factor)}px;
            }}
        """)
        
        layout = QVBoxLayout(panel)
        layout.setSpacing(int(10 * self.scale_factor))
        
        # Title
        title = QLabel("Module Selection Hub")
        title.setProperty("class", "title")
        title.setFont(QFont('Segoe UI', int(18 * self.scale_factor), QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Module selector
        self.module_selector = AdvancedModuleSelector(self.scale_factor)
        layout.addWidget(self.module_selector)
        
        return panel
    
    def set_defaults(self):
        """Set intelligent defaults"""
        self.config_panel.set_defaults()
        self.action_panel.set_default_output_path(os.getcwd())
        
        # Select essential modules including PPR_Q
        self.module_selector.select_essential()
    
    def get_params_dict(self):
        """Generate parameters dictionary"""
        config_data = self.config_panel.get_config_data()
        modules = self.module_selector.get_selected_modules()
        
        # Add PPR_Q if enabled and not already selected
        if config_data["ppr_q_enabled"] and "PPR_Q" not in modules:
            modules.append("PPR_Q")
        
        params = {
            "Site": config_data["site"],
            "plan_type": config_data["plan_type"],
            "shift": config_data["shift"],
            "SOSdatetime": config_data["sos_datetime"],
            "EOSdatetime": config_data["eos_datetime"],
            "Modules": modules,
            "GeneratedBy": "OnePyFlow Params Generator V2.0 - Dark Matrix Edition",
            "GeneratedAt": datetime.now().isoformat(),
            "PPR_Q_Enabled": config_data["ppr_q_enabled"]
        }
        
        return params
    
    def preview_json(self):
        """Preview the JSON with syntax highlighting"""
        params = self.get_params_dict()
        json_str = json.dumps(params, indent=4)
        
        dialog = QDialog(self)
        dialog.setWindowTitle("🔍 JSON Preview")
        dialog.setMinimumSize(int(600 * self.scale_factor), int(500 * self.scale_factor))
        dialog.setStyleSheet(f"""
            QDialog {{
                background: {DarkMatrixTheme.COLORS['bg_secondary']};
                border-radius: {int(10 * self.scale_factor)}px;
            }}
        """)
        
        layout = QVBoxLayout(dialog)
        
        text_edit = QTextEdit()
        text_edit.setPlainText(json_str)
        text_edit.setStyleSheet(f"""
            QTextEdit {{
                background: {DarkMatrixTheme.COLORS['bg_primary']};
                color: {DarkMatrixTheme.COLORS['text_primary']};
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: {int(12 * self.scale_factor)}px;
                border-radius: {int(8 * self.scale_factor)}px;
                padding: {int(15 * self.scale_factor)}px;
                border: 2px solid {DarkMatrixTheme.COLORS['border']};
            }}
        """)
        text_edit.setReadOnly(True)
        layout.addWidget(text_edit)
        
        close_btn = ModernButton("Looks Good!", "success", scale_factor=self.scale_factor)
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
        
        output_dir = self.action_panel.get_output_path()
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
            msg.setStyleSheet(f"""
                QMessageBox {{
                    background: {DarkMatrixTheme.COLORS['bg_secondary']};
                    border-radius: {int(10 * self.scale_factor)}px;
                }}
                QMessageBox QPushButton {{
                    background: {DarkMatrixTheme.COLORS['accent_primary']};
                    color: {DarkMatrixTheme.COLORS['bg_primary']};
                    border: none;
                    border-radius: {int(5 * self.scale_factor)}px;
                    padding: {int(8 * self.scale_factor)}px {int(16 * self.scale_factor)}px;
                    font-weight: bold;
                }}
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
    app.setApplicationName("OnePyFlow Params Generator V2.0 - Dark Matrix Edition")
    app.setApplicationVersion("2.0.0")
    
    # Apply dark matrix theme
    DarkMatrixTheme.apply_theme(app)
    
    window = OnePyFlowParamsGenerator()
    window.show()

    result = app.exec_()
    sys.exit(result)

if __name__ == "__main__":
    main() 