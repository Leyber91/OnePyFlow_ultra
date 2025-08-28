"""
OnePyFlow Params Generator - Proper Layout Edition
Completely redesigned with vertical layout and proper module selection area
"""

import sys
import os
import json
import subprocess
from datetime import datetime
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from .fc_configs import FCConfigs

class ProperTheme:
    """Theme optimized for proper layout"""
    
    COLORS = {
        'bg_primary': '#0f172a',
        'bg_secondary': '#1e293b', 
        'bg_tertiary': '#334155',
        'bg_card': '#475569',
        'accent': '#06b6d4',
        'accent_hover': '#0891b2',
        'success': '#10b981',
        'warning': '#f59e0b',
        'error': '#ef4444',
        'text_primary': '#f8fafc',
        'text_secondary': '#cbd5e1',
        'text_muted': '#64748b',
        'border': '#475569'
    }
    
    @classmethod
    def get_card_style(cls):
        return f"""
            QGroupBox {{
                background-color: rgba(30, 41, 59, 0.9);
                border: 2px solid rgba(71, 85, 105, 0.9);
                border-radius: 12px;
                padding: 20px;
                margin: 8px;
                font-size: 16px;
                font-weight: 600;
                color: {cls.COLORS['text_primary']};
                font-family: 'Segoe UI', Arial, sans-serif;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 16px;
                padding: 0 8px;
                color: {cls.COLORS['accent']};
                font-size: 14px;
                font-weight: bold;
            }}
        """
    
    @classmethod
    def get_input_style(cls):
        return f"""
            QComboBox, QLineEdit, QDateTimeEdit {{
                background-color: rgba(51, 65, 85, 0.95);
                border: 2px solid rgba(71, 85, 105, 0.9);
                border-radius: 8px;
                padding: 12px 16px;
                font-size: 14px;
                color: {cls.COLORS['text_primary']};
                min-height: 28px;
                font-family: 'Segoe UI', Arial, sans-serif;
            }}
            QComboBox:focus, QLineEdit:focus, QDateTimeEdit:focus {{
                border-color: {cls.COLORS['accent']};
            }}
        """
    
    @classmethod
    def get_button_style(cls, variant='primary'):
        colors = {
            'primary': cls.COLORS['accent'],
            'success': cls.COLORS['success'],
            'warning': cls.COLORS['warning'],
            'error': cls.COLORS['error']
        }
        color = colors.get(variant, cls.COLORS['accent'])
        
        return f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 20px;
                font-size: 14px;
                font-weight: 600;
                min-height: 20px;
                font-family: 'Segoe UI', Arial, sans-serif;
            }}
            QPushButton:hover {{
                background-color: {cls.COLORS['accent_hover']};
            }}
        """

class ProperSchedulePicker(QWidget):
    """Compact schedule picker"""
    
    schedule_changed = pyqtSignal(float, float)
    
    def __init__(self, fc="DTM2"):
        super().__init__()
        self.fc = fc
        self.start_hour = 6.0
        self.end_hour = 14.0
        self.setFixedHeight(80)
        
    def set_fc(self, fc):
        self.fc = fc
        self.update()
        
    def set_shift(self, shift_name):
        start, end = FCConfigs.get_shift_times(self.fc, shift_name)
        self.start_hour = start
        self.end_hour = end % 24 if end >= 24 else end
        self.schedule_changed.emit(self.start_hour, self.end_hour)
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        rect = self.rect()
        margin = 10
        timeline_rect = QRect(margin, 15, rect.width() - 2*margin, 35)
        
        # Background
        painter.fillRect(timeline_rect, QColor(51, 65, 85))
        painter.setPen(QPen(QColor(71, 85, 105), 2))
        painter.drawRoundedRect(timeline_rect, 6, 6)
        
        # Hour markers
        painter.setPen(QPen(QColor(148, 163, 184), 1))
        for hour in range(0, 25, 6):
            x = int(timeline_rect.left() + (hour / 24) * timeline_rect.width())
            painter.drawLine(x, timeline_rect.top(), x, timeline_rect.bottom())
            
            painter.setPen(QColor(203, 213, 225))
            painter.setFont(QFont('Segoe UI', 8))
            painter.drawText(x - 8, timeline_rect.bottom() + 12, f"{hour:02d}")
            
        # Shift block
        start_x = int(timeline_rect.left() + (self.start_hour / 24) * timeline_rect.width())
        end_x = int(timeline_rect.left() + (self.end_hour / 24) * timeline_rect.width())
        
        painter.fillRect(QRect(start_x, timeline_rect.top() + 6,
                              end_x - start_x, timeline_rect.height() - 12),
                        QColor(6, 182, 212))
        
        # Time labels
        painter.setPen(QColor(248, 250, 252))
        painter.setFont(QFont('Segoe UI', 9, QFont.Bold))
        start_text = FCConfigs.format_time(self.start_hour)
        end_text = FCConfigs.format_time(self.end_hour)
        painter.drawText(timeline_rect.left(), timeline_rect.top() - 3, f"{start_text} - {end_text}")

class ProperShiftPresets(QWidget):
    """Compact shift presets"""
    
    shift_selected = pyqtSignal(str)
    
    def __init__(self, fc="DTM2"):
        super().__init__()
        self.fc = fc
        self.setup_ui()
        
    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.update_shifts()
        
    def set_fc(self, fc):
        self.fc = fc
        self.update_shifts()
        
    def update_shifts(self):
        # Clear existing buttons
        while self.layout().count():
            child = self.layout().takeAt(0)
            if child.widget():
                child.widget().deleteLater()
                
        shifts = FCConfigs.get_shifts_for_fc(self.fc)
        colors = ['#10b981', '#f59e0b', '#3b82f6', '#8b5cf6']
        
        for i, (shift_name, (start, end)) in enumerate(shifts.items()):
            btn = QPushButton(shift_name.upper())
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {colors[i % len(colors)]};
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 8px 12px;
                    font-weight: 600;
                    font-size: 11px;
                    min-height: 16px;
                }}
                QPushButton:hover {{
                    background-color: #06b6d4;
                }}
            """)
            
            start_str = FCConfigs.format_time(start)
            end_str = FCConfigs.format_time(end % 24)
            btn.setToolTip(f"{shift_name.upper()}: {start_str} - {end_str}")
            btn.clicked.connect(lambda checked, s=shift_name: self.shift_selected.emit(s))
            
            self.layout().addWidget(btn)

class ProperModuleSelector(QWidget):
    """Large module selector with proper visibility"""
    
    def __init__(self):
        super().__init__()
        self.setup_modules()
        self.setup_ui()
        
    def setup_modules(self):
        self.modules = {
            "Performance": ["Echo", "PHC", "HCTool", "BackLog", "PPR", "PPR_Q", "ALPS", "RODEO"],
            "Analytics": ["Galaxy", "Galaxy_percentages", "Galaxy2", "Galaxy2_values", "ICQA", "F2P", "kNekro", "SSP", "SSPOT"],
            "Transport": ["DockMaster", "DockMasterFiltered", "DockMaster2", "DockMaster2Filtered", "DockFlow", "YMS", "FMC", "CarrierMatrix", "SCACs", "SPARK"],
            "Support": ["ALPS_RC_Sort", "ALPSRoster", "QuipCSV", "VIP", "IBBT"]
        }
        self.essential_modules = ["Echo", "PPR_Q", "ALPS", "Galaxy", "DockMaster", "SPARK"]
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        
        # Search
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search modules...")
        self.search_bar.setStyleSheet(ProperTheme.get_input_style())
        self.search_bar.textChanged.connect(self.filter_modules)
        layout.addWidget(self.search_bar)
        
        # Tabs - make them much larger
        self.tab_widget = QTabWidget()
        self.tab_widget.setMinimumHeight(400)
        self.tab_widget.setStyleSheet(f"""
            QTabWidget::pane {{
                border: 2px solid {ProperTheme.COLORS['border']};
                border-radius: 8px;
                background: {ProperTheme.COLORS['bg_secondary']};
                padding: 12px;
            }}
            QTabBar::tab {{
                background: {ProperTheme.COLORS['bg_tertiary']};
                padding: 10px 16px;
                margin-right: 2px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                color: {ProperTheme.COLORS['text_secondary']};
                font-weight: 600;
                font-size: 13px;
                min-width: 80px;
            }}
            QTabBar::tab:selected {{
                background: {ProperTheme.COLORS['bg_secondary']};
                color: {ProperTheme.COLORS['accent']};
            }}
        """)
        
        self.module_checkboxes = {}
        self.create_module_tabs()
        layout.addWidget(self.tab_widget)
        
        # Quick buttons
        quick_layout = QHBoxLayout()
        quick_layout.setSpacing(8)
        
        all_btn = QPushButton("All")
        essential_btn = QPushButton("Essential")
        clear_btn = QPushButton("Clear")
        
        for btn, variant in [(all_btn, 'success'), (essential_btn, 'primary'), (clear_btn, 'error')]:
            btn.setStyleSheet(ProperTheme.get_button_style(variant))
            quick_layout.addWidget(btn)
            
        all_btn.clicked.connect(self.select_all)
        essential_btn.clicked.connect(self.select_essential)
        clear_btn.clicked.connect(self.clear_all)
        
        layout.addLayout(quick_layout)
        
    def create_module_tabs(self):
        for category, modules in self.modules.items():
            scroll_area = QScrollArea()
            scroll_widget = QWidget()
            scroll_layout = QGridLayout(scroll_widget)
            scroll_layout.setSpacing(6)
            
            row, col = 0, 0
            for module in modules:
                checkbox = QCheckBox(module)
                checkbox.setStyleSheet(f"""
                    QCheckBox {{
                        font-size: 13px;
                        color: {ProperTheme.COLORS['text_primary']};
                        padding: 6px;
                        spacing: 8px;
                    }}
                    QCheckBox::indicator {{
                        width: 16px;
                        height: 16px;
                        border: 2px solid {ProperTheme.COLORS['border']};
                        border-radius: 3px;
                        background: {ProperTheme.COLORS['bg_tertiary']};
                    }}
                    QCheckBox::indicator:checked {{
                        background: {ProperTheme.COLORS['accent']};
                        border-color: {ProperTheme.COLORS['accent']};
                    }}
                """)
                
                if module == "PPR_Q":
                    checkbox.setStyleSheet(checkbox.styleSheet() + f"""
                        QCheckBox {{
                            background: {ProperTheme.COLORS['warning']};
                            color: black;
                            border-radius: 4px;
                            padding: 8px;
                            font-weight: bold;
                        }}
                    """)
                    
                scroll_layout.addWidget(checkbox, row, col)
                self.module_checkboxes[module] = checkbox
                
                col += 1
                if col > 2:  # 3 columns
                    col = 0
                    row += 1
                
            scroll_layout.setRowStretch(row + 1, 1)
            scroll_area.setWidget(scroll_widget)
            scroll_area.setWidgetResizable(True)
            self.tab_widget.addTab(scroll_area, category)
            
    def filter_modules(self, text):
        for module, checkbox in self.module_checkboxes.items():
            checkbox.setVisible(text.lower() in module.lower())
            
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

class ProperParamsGenerator(QMainWindow):
    """Proper params generator with vertical layout"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OnePyFlow Params Generator V5.0 — Proper Layout")
        self.setMinimumSize(1400, 800)
        self.setup_ui()
        self.setup_connections()
        
    def setup_ui(self):
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {ProperTheme.COLORS['bg_primary']};
                color: {ProperTheme.COLORS['text_primary']};
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 13px;
            }}
        """)
        
        central = QWidget()
        self.setCentralWidget(central)
        
        # VERTICAL layout - this is key!
        main_layout = QVBoxLayout(central)
        main_layout.setSpacing(16)
        main_layout.setContentsMargins(16, 16, 16, 16)
        
        # Top row - Site and Schedule in horizontal layout
        top_row = QHBoxLayout()
        top_row.setSpacing(16)
        
        # Site Configuration - compact
        site_group = QGroupBox("Site Configuration")
        site_group.setStyleSheet(ProperTheme.get_card_style())
        site_group.setMaximumHeight(120)
        site_layout = QGridLayout(site_group)
        site_layout.setSpacing(8)
        
        self.site_combo = QComboBox()
        self.site_combo.addItems(FCConfigs.AVAILABLE_FCS)
        self.site_combo.setCurrentText("DTM2")
        self.site_combo.setStyleSheet(ProperTheme.get_input_style())
        
        self.plan_combo = QComboBox()
        self.plan_combo.addItems(FCConfigs.PLAN_TYPES)
        self.plan_combo.setStyleSheet(ProperTheme.get_input_style())
        
        site_layout.addWidget(QLabel("Site:"), 0, 0)
        site_layout.addWidget(self.site_combo, 0, 1)
        site_layout.addWidget(QLabel("Plan:"), 1, 0)
        site_layout.addWidget(self.plan_combo, 1, 1)
        
        # Schedule Configuration - compact
        schedule_group = QGroupBox("Schedule Configuration")
        schedule_group.setStyleSheet(ProperTheme.get_card_style())
        schedule_group.setMaximumHeight(120)
        schedule_layout = QVBoxLayout(schedule_group)
        schedule_layout.setSpacing(6)
        
        self.schedule_picker = ProperSchedulePicker("DTM2")
        schedule_layout.addWidget(self.schedule_picker)
        
        self.shift_presets = ProperShiftPresets("DTM2")
        schedule_layout.addWidget(self.shift_presets)
        
        top_row.addWidget(site_group)
        top_row.addWidget(schedule_group)
        
        # DateTime row - separate row for better space usage
        dt_group = QGroupBox("Time Range")
        dt_group.setStyleSheet(ProperTheme.get_card_style())
        dt_group.setMaximumHeight(80)
        dt_layout = QHBoxLayout(dt_group)
        dt_layout.setSpacing(12)
        
        self.start_dt = QDateTimeEdit(QDateTime.currentDateTime().addSecs(-3600))
        self.start_dt.setDisplayFormat("MM-dd HH:mm")
        self.start_dt.setStyleSheet(ProperTheme.get_input_style())
        
        self.end_dt = QDateTimeEdit(QDateTime.currentDateTime())
        self.end_dt.setDisplayFormat("MM-dd HH:mm")
        self.end_dt.setStyleSheet(ProperTheme.get_input_style())
        
        dt_layout.addWidget(QLabel("Start:"))
        dt_layout.addWidget(self.start_dt)
        dt_layout.addWidget(QLabel("End:"))
        dt_layout.addWidget(self.end_dt)
        dt_layout.addStretch()
        
        # Actions row - compact
        actions_group = QGroupBox("Actions")
        actions_group.setStyleSheet(ProperTheme.get_card_style())
        actions_group.setMaximumHeight(120)
        actions_layout = QVBoxLayout(actions_group)
        actions_layout.setSpacing(8)
        
        # Output path
        path_layout = QHBoxLayout()
        self.output_path = QLineEdit(os.getcwd())
        self.output_path.setStyleSheet(ProperTheme.get_input_style())
        
        browse_btn = QPushButton("Browse")
        browse_btn.setStyleSheet(ProperTheme.get_button_style('primary'))
        browse_btn.clicked.connect(self.browse_output)
        
        path_layout.addWidget(QLabel("Output:"))
        path_layout.addWidget(self.output_path)
        path_layout.addWidget(browse_btn)
        actions_layout.addLayout(path_layout)
        
        # Action buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(8)
        
        self.preview_btn = QPushButton("Preview")
        self.save_btn = QPushButton("Save")
        self.run_btn = QPushButton("Generate & Run")
        
        for btn, variant in [(self.preview_btn, 'primary'), (self.save_btn, 'success'), (self.run_btn, 'success')]:
            btn.setStyleSheet(ProperTheme.get_button_style(variant))
            buttons_layout.addWidget(btn)
            
        # Add icons
        try:
            base = os.path.join(os.path.dirname(__file__), 'icons')
            self.preview_btn.setIcon(QIcon(os.path.join(base, 'preview.svg')))
            self.preview_btn.setIconSize(QSize(16, 16))
            self.save_btn.setIcon(QIcon(os.path.join(base, 'save.svg')))
            self.save_btn.setIconSize(QSize(16, 16))
            self.run_btn.setIcon(QIcon(os.path.join(base, 'run.svg')))
            self.run_btn.setIconSize(QSize(16, 16))
        except Exception:
            pass
            
        actions_layout.addLayout(buttons_layout)
        
        # Add all top sections
        main_layout.addLayout(top_row)
        main_layout.addWidget(dt_group)
        main_layout.addWidget(actions_group)
        
        # Module Selection - LARGE area at bottom
        module_group = QGroupBox("Module Selection")
        module_group.setStyleSheet(ProperTheme.get_card_style())
        module_layout = QVBoxLayout(module_group)
        
        self.module_selector = ProperModuleSelector()
        module_layout.addWidget(self.module_selector)
        
        # This gets the remaining space!
        main_layout.addWidget(module_group, 1)  # stretch factor 1
        
    def setup_connections(self):
        self.site_combo.currentTextChanged.connect(self.on_site_changed)
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
            
        self.start_dt.setDateTime(start_dt)
        self.end_dt.setDateTime(end_dt)
        
    def browse_output(self):
        path = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if path:
            self.output_path.setText(path)
            
    def get_parameters(self):
        return {
            "Site": self.site_combo.currentText(),
            "plan_type": self.plan_combo.currentText(),
            "shift": "Custom",
            "SOSdatetime": self.start_dt.dateTime().toString("yyyy-MM-dd HH:mm:ss"),
            "EOSdatetime": self.end_dt.dateTime().toString("yyyy-MM-dd HH:mm:ss"),
            "Modules": self.module_selector.get_selected_modules(),
            "GeneratedBy": "OnePyFlow Params Generator V5.0 - Proper Layout",
            "GeneratedAt": datetime.now().isoformat()
        }
        
    def preview_parameters(self):
        params = self.get_parameters()
        if not params["Modules"]:
            QMessageBox.warning(self, "Warning", "Please select at least one module!")
            return
            
        dialog = QDialog(self)
        dialog.setWindowTitle("Preview Parameters")
        dialog.setMinimumSize(600, 500)
        dialog.setStyleSheet(f"background-color: {ProperTheme.COLORS['bg_primary']}; color: {ProperTheme.COLORS['text_primary']};")
        
        layout = QVBoxLayout(dialog)
        text = QTextEdit()
        text.setPlainText(json.dumps(params, indent=4))
        text.setReadOnly(True)
        text.setStyleSheet(f"""
            background-color: {ProperTheme.COLORS['bg_secondary']};
            border: 2px solid {ProperTheme.COLORS['border']};
            border-radius: 8px;
            padding: 12px;
            font-family: 'Consolas', monospace;
            font-size: 12px;
            color: {ProperTheme.COLORS['text_primary']};
        """)
        layout.addWidget(text)
        
        close_btn = QPushButton("Close")
        close_btn.setStyleSheet(ProperTheme.get_button_style('primary'))
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)
        
        dialog.exec_()
        
    def save_parameters(self):
        params = self.get_parameters()
        if not params["Modules"]:
            QMessageBox.warning(self, "Warning", "Please select at least one module!")
            return
            
        file_path = os.path.join(self.output_path.text(), "OnePyFlowParams.json")
        
        try:
            with open(file_path, 'w') as f:
                json.dump(params, f, indent=4)
            QMessageBox.information(self, "Success", f"Parameters saved to:\n{file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save: {e}")
            
    def generate_and_run(self):
        self.save_parameters()
        
        try:
            output_path = self.output_path.text()
            main_py = os.path.join(output_path, "main.py")
            
            if not os.path.exists(main_py):
                main_py = os.path.join(os.path.dirname(output_path), "main.py")
                
            if os.path.exists(main_py):
                subprocess.Popen([sys.executable, main_py], cwd=os.path.dirname(main_py))
                QMessageBox.information(self, "Success", "OnePyFlow launched!")
                self.close()
            else:
                QMessageBox.warning(self, "Warning", "main.py not found!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to launch: {e}")

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    window = ProperParamsGenerator()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
