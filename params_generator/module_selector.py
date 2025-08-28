"""
Module selection widget with search and categorization
"""

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from .theme import Theme

class ModuleSelector(QWidget):
    """Modern module selector with search and categories"""
    
    def __init__(self):
        super().__init__()
        self.setup_modules()
        self.setup_ui()
        
    def setup_modules(self):
        """Setup module categories and definitions"""
        self.modules = {
            "Performance": {
                "modules": ["Echo", "PHC", "HCTool", "BackLog", "PPR", "PPR_Q", "ALPS", "RODEO"],
                "description": "Core performance monitoring and analysis"
            },
            "Analytics": {
                "modules": ["Galaxy", "Galaxy_percentages", "Galaxy2", "Galaxy2_values", "ICQA", "F2P", "kNekro", "SSP", "SSPOT"],
                "description": "Data analytics and reporting modules"
            },
            "Transport": {
                "modules": ["DockMaster", "DockMasterFiltered", "DockMaster2", "DockMaster2Filtered", "DockFlow", "YMS", "FMC", "CarrierMatrix", "SCACs", "SPARK"],
                "description": "Logistics and transportation data"
            },
            "Support": {
                "modules": ["ALPS_RC_Sort", "ALPSRoster", "QuipCSV", "VIP", "IBBT"],
                "description": "Operations and support modules"
            }
        }
        
        # Essential modules for quick selection
        self.essential_modules = ["Echo", "PPR_Q", "ALPS", "Galaxy", "DockMaster", "SPARK"]
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(Theme.SPACING['md'])
        
        # Search bar
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("🔍 Search modules...")
        self.search_bar.setStyleSheet(Theme.STYLES['input_field'])
        self.search_bar.textChanged.connect(self.filter_modules)
        layout.addWidget(self.search_bar)
        
        # Module tabs
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet(f"""
            QTabWidget::pane {{
                border: 1px solid {Theme.COLORS['border']};
                border-radius: 8px;
                background: {Theme.COLORS['bg_secondary']};
                padding: 12px;
            }}
            QTabBar::tab {{
                background: {Theme.COLORS['bg_tertiary']};
                padding: 12px 20px;
                margin-right: 2px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                color: {Theme.COLORS['text_secondary']};
                font-weight: bold;
                font-size: {Theme.FONTS['small']}px;
            }}
            QTabBar::tab:selected {{
                background: {Theme.COLORS['bg_secondary']};
                color: {Theme.COLORS['accent']};
            }}
            QTabBar::tab:hover {{
                background: {Theme.COLORS['bg_secondary']};
                color: {Theme.COLORS['text_primary']};
            }}
        """)
        
        self.module_checkboxes = {}
        self.create_module_tabs()
        layout.addWidget(self.tab_widget)
        
        # Quick selection buttons
        quick_layout = QHBoxLayout()
        quick_layout.setSpacing(Theme.SPACING['sm'])
        
        buttons = [
            ("All", self.select_all, Theme.COLORS['success']),
            ("Essential", self.select_essential, Theme.COLORS['accent']),
            ("Clear", self.clear_all, Theme.COLORS['error'])
        ]
        
        for btn_text, btn_func, btn_color in buttons:
            btn = QPushButton(btn_text)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: {btn_color};
                    color: {Theme.COLORS['bg_primary']};
                    border: none;
                    border-radius: 6px;
                    padding: 8px 16px;
                    font-weight: bold;
                    font-size: {Theme.FONTS['small']}px;
                    min-height: 30px;
                }}
                QPushButton:hover {{
                    background: {Theme.COLORS['accent_hover']};
                }}
            """)
            btn.clicked.connect(btn_func)
            quick_layout.addWidget(btn)
            
        layout.addLayout(quick_layout)
        
    def create_module_tabs(self):
        """Create module category tabs"""
        for category, config in self.modules.items():
            scroll_area = QScrollArea()
            scroll_area.setStyleSheet(Theme.STYLES['scroll_area'])
            
            scroll_widget = QWidget()
            scroll_layout = QVBoxLayout(scroll_widget)
            scroll_layout.setSpacing(Theme.SPACING['sm'])
            
            # Category description
            desc_label = QLabel(config['description'])
            desc_label.setStyleSheet(f"""
                color: {Theme.COLORS['text_muted']};
                font-size: {Theme.FONTS['small']}px;
                font-style: italic;
                margin-bottom: 8px;
            """)
            scroll_layout.addWidget(desc_label)
            
            for module in config['modules']:
                checkbox = QCheckBox(module)
                checkbox.setStyleSheet(Theme.STYLES['checkbox'])
                
                # Special styling for PPR_Q
                if module == "PPR_Q":
                    checkbox.setStyleSheet(Theme.STYLES['checkbox'] + f"""
                        QCheckBox {{
                            background: {Theme.COLORS['warning']};
                            color: {Theme.COLORS['bg_primary']};
                            border-radius: 8px;
                            padding: 12px;
                            font-weight: bold;
                            margin: 4px;
                        }}
                    """)
                    
                scroll_layout.addWidget(checkbox)
                self.module_checkboxes[module] = checkbox
                
            scroll_layout.addStretch()
            scroll_area.setWidget(scroll_widget)
            scroll_area.setWidgetResizable(True)
            self.tab_widget.addTab(scroll_area, category)
            
    def filter_modules(self, text):
        """Filter modules based on search text"""
        search_text = text.lower()
        for module, checkbox in self.module_checkboxes.items():
            checkbox.setVisible(search_text in module.lower())
            
    def select_all(self):
        """Select all modules"""
        for checkbox in self.module_checkboxes.values():
            checkbox.setChecked(True)
            
    def select_essential(self):
        """Select essential modules only"""
        self.clear_all()
        for module, checkbox in self.module_checkboxes.items():
            if module in self.essential_modules:
                checkbox.setChecked(True)
                
    def clear_all(self):
        """Clear all module selections"""
        for checkbox in self.module_checkboxes.values():
            checkbox.setChecked(False)
            
    def get_selected_modules(self):
        """Get list of selected modules"""
        return [module for module, checkbox in self.module_checkboxes.items() if checkbox.isChecked()]
    
    def set_selected_modules(self, modules):
        """Set selected modules from list"""
        self.clear_all()
        for module in modules:
            if module in self.module_checkboxes:
                self.module_checkboxes[module].setChecked(True)
