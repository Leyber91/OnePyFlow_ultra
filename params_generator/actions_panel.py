"""
Actions panel for output configuration and execution
"""

import os
import json
import subprocess
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from datetime import datetime
from .theme import Theme

class ActionsPanel(QWidget):
    """Actions panel for output configuration and execution"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the actions panel UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(Theme.SPACING['lg'])
        
        # Output configuration group
        output_group = QGroupBox("📁 Output Configuration")
        output_group.setStyleSheet(Theme.STYLES['group_box'])
        output_layout = QVBoxLayout(output_group)
        output_layout.setSpacing(Theme.SPACING['md'])
        
        # Output path
        path_layout = QHBoxLayout()
        path_label = QLabel("Output Directory:")
        path_label.setStyleSheet(f"color: {Theme.COLORS['text_primary']}; font-weight: bold;")
        
        self.output_path = QLineEdit(os.getcwd())
        self.output_path.setStyleSheet(Theme.STYLES['input_field'])
        
        browse_btn = QPushButton("Browse")
        browse_btn.setStyleSheet(Theme.STYLES['button_secondary'])
        browse_btn.clicked.connect(self.browse_output)
        
        path_layout.addWidget(self.output_path)
        path_layout.addWidget(browse_btn)
        
        output_layout.addWidget(path_label)
        output_layout.addLayout(path_layout)
        layout.addWidget(output_group)
        
        # Actions group
        actions_group = QGroupBox("🎯 Actions")
        actions_group.setStyleSheet(Theme.STYLES['group_box'])
        actions_layout = QVBoxLayout(actions_group)
        actions_layout.setSpacing(Theme.SPACING['md'])
        
        # Preview button
        self.preview_btn = QPushButton("👁️ Preview JSON")
        self.preview_btn.setStyleSheet(Theme.STYLES['button_secondary'])
        self.preview_btn.setToolTip("Preview the parameters JSON before saving")
        
        # Save button
        self.save_btn = QPushButton("💾 Save Parameters")
        self.save_btn.setStyleSheet(Theme.STYLES['button_primary'])
        self.save_btn.setToolTip("Save parameters to JSON file")
        
        # Generate & Run button
        self.run_btn = QPushButton("🚀 Generate & Run OnePyFlow")
        self.run_btn.setStyleSheet(f"""
            QPushButton {{
                background: {Theme.COLORS['success']};
                color: {Theme.COLORS['bg_primary']};
                border: none;
                border-radius: 8px;
                padding: 16px 24px;
                font-weight: bold;
                font-size: {Theme.FONTS['large']}px;
                min-height: 50px;
            }}
            QPushButton:hover {{
                background: {Theme.COLORS['accent_hover']};
            }}
            QPushButton:pressed {{
                background: {Theme.COLORS['accent']};
            }}
        """)
        self.run_btn.setToolTip("Save parameters and launch OnePyFlow main.py")
        
        actions_layout.addWidget(self.preview_btn)
        actions_layout.addWidget(self.save_btn)
        actions_layout.addWidget(self.run_btn)
        layout.addWidget(actions_group)
        
        layout.addStretch()
        
    def browse_output(self):
        """Browse for output directory"""
        path = QFileDialog.getExistingDirectory(self, "Select Output Directory", self.output_path.text())
        if path:
            self.output_path.setText(path)
            
    def get_output_path(self):
        """Get current output path"""
        return self.output_path.text()
        
    def set_output_path(self, path):
        """Set output path"""
        self.output_path.setText(path)

class PreviewDialog(QDialog):
    """Dialog for previewing parameters JSON"""
    
    def __init__(self, params_dict, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Preview Parameters JSON")
        self.setMinimumSize(700, 600)
        self.setup_ui(params_dict)
        
    def setup_ui(self, params_dict):
        """Setup preview dialog UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(Theme.SPACING['md'])
        
        # Title
        title = QLabel("Parameters Preview")
        title.setStyleSheet(f"""
            color: {Theme.COLORS['text_primary']};
            font-size: {Theme.FONTS['xlarge']}px;
            font-weight: bold;
            margin-bottom: 10px;
        """)
        layout.addWidget(title)
        
        # JSON text area
        self.text_area = QTextEdit()
        self.text_area.setPlainText(json.dumps(params_dict, indent=4))
        self.text_area.setReadOnly(True)
        self.text_area.setStyleSheet(f"""
            QTextEdit {{
                background: {Theme.COLORS['bg_tertiary']};
                border: 2px solid {Theme.COLORS['border']};
                border-radius: 8px;
                padding: 12px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: {Theme.FONTS['small']}px;
                color: {Theme.COLORS['text_primary']};
            }}
        """)
        layout.addWidget(self.text_area)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        copy_btn = QPushButton("📋 Copy to Clipboard")
        copy_btn.setStyleSheet(Theme.STYLES['button_secondary'])
        copy_btn.clicked.connect(self.copy_to_clipboard)
        
        close_btn = QPushButton("Close")
        close_btn.setStyleSheet(Theme.STYLES['button_primary'])
        close_btn.clicked.connect(self.accept)
        
        button_layout.addWidget(copy_btn)
        button_layout.addStretch()
        button_layout.addWidget(close_btn)
        layout.addLayout(button_layout)
        
        # Apply dark theme to dialog
        self.setStyleSheet(f"""
            QDialog {{
                background: {Theme.COLORS['bg_primary']};
                color: {Theme.COLORS['text_primary']};
            }}
        """)
        
    def copy_to_clipboard(self):
        """Copy JSON to clipboard"""
        clipboard = QApplication.clipboard()
        clipboard.setText(self.text_area.toPlainText())
        
        # Show temporary tooltip
        QToolTip.showText(self.mapToGlobal(self.rect().center()), "Copied to clipboard!", self)
