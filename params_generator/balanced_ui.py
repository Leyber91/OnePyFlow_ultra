"""
🚀 Balanced OnePyFlow Params Generator - Perfect Proportions
Professional layout with proper spacing and visual hierarchy
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

class BalancedTheme:
    """Balanced theme with perfect proportions"""
    
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
                background-color: rgba(30, 41, 59, 0.8);
                border: 2px solid rgba(71, 85, 105, 0.8);
                border-radius: 12px;
                padding: 24px;
                margin: 12px;
                font-size: 18px;
                font-weight: 600;
                color: {cls.COLORS['text_primary']};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 20px;
                padding: 0 12px;
                color: {cls.COLORS['accent']};
                font-size: 16px;
                font-weight: bold;
            }}
        """
    
    @classmethod
    def get_input_style(cls):
        return f"""
            QComboBox, QLineEdit, QDateTimeEdit {{
                background-color: rgba(51, 65, 85, 0.9);
                border: 2px solid rgba(71, 85, 105, 0.8);
                border-radius: 8px;
                padding: 16px 20px;
                font-size: 16px;
                color: {cls.COLORS['text_primary']};
                min-height: 32px;
                font-family: 'Segoe UI', Arial, sans-serif;
            }}
            QComboBox:focus, QLineEdit:focus, QDateTimeEdit:focus {{
                border-color: {cls.COLORS['accent']};
                background-color: rgba(51, 65, 85, 1.0);
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
                padding: 18px 28px;
                font-size: 16px;
                font-weight: 600;
                min-height: 24px;
                font-family: 'Segoe UI', Arial, sans-serif;
            }}
            QPushButton:hover {{
                background-color: {cls.COLORS['accent_hover']};
                transform: translateY(-1px);
            }}
        """

class CompactSchedulePicker(QWidget):
    """Compact schedule picker with proper proportions"""
    
    schedule_changed = pyqtSignal(float, float)
    
    def __init__(self, fc="DTM2"):
        super().__init__()
        self.fc = fc
        self.start_hour = 6.0
        self.end_hour = 14.0
        self.setFixedHeight(100)
        
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
        timeline_rect = QRect(margin, 20, rect.width() - 2*margin, 40)
        
        # Background
        painter.fillRect(timeline_rect, QColor(51, 65, 85))
        painter.setPen(QPen(QColor(71, 85, 105), 2))
        painter.drawRoundedRect(timeline_rect, 8, 8)
        
        # Hour markers
        painter.setPen(QPen(QColor(148, 163, 184), 1))
        for hour in range(0, 25, 6):
            x = int(timeline_rect.left() + (hour / 24) * timeline_rect.width())
            painter.drawLine(x, timeline_rect.top(), x, timeline_rect.bottom())
            
            painter.setPen(QColor(203, 213, 225))
            painter.setFont(QFont('Segoe UI', 9))
            painter.drawText(x - 12, timeline_rect.bottom() + 15, f"{hour:02d}")
            
        # Shift block
        start_x = int(timeline_rect.left() + (self.start_hour / 24) * timeline_rect.width())
        end_x = int(timeline_rect.left() + (self.end_hour / 24) * timeline_rect.width())
        
        painter.fillRect(QRect(start_x, timeline_rect.top() + 8,
                              end_x - start_x, timeline_rect.height() - 16),
                        QColor(6, 182, 212))
        
        # Time labels
        painter.setPen(QColor(248, 250, 252))
        painter.setFont(QFont('Segoe UI', 10, QFont.Bold))
        start_text = FCConfigs.format_time(self.start_hour)
        end_text = FCConfigs.format_time(self.end_hour)
        painter.drawText(timeline_rect.left(), timeline_rect.top() - 5, f"{start_text} - {end_text}")
        
    def mousePressEvent(self, event):
        rect = self.rect()
        margin = 10
        timeline_rect = QRect(margin, 20, rect.width() - 2*margin, 40)
        
        if timeline_rect.contains(event.pos()):
            relative_x = event.pos().x() - timeline_rect.left()
            hour = (relative_x / timeline_rect.width()) * 24
            
            if event.button() == Qt.LeftButton:
                self.start_hour = hour
            elif event.button() == Qt.RightButton:
                self.end_hour = hour
                
            self.schedule_changed.emit(self.start_hour, self.end_hour)
            self.update()

class CompactShiftPresets(QWidget):
    """Compact shift presets with proper sizing"""
    
    shift_selected = pyqtSignal(str)
    
    def __init__(self, fc="DTM2"):
        super().__init__()
        self.fc = fc
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.buttons_container = QWidget()
        self.buttons_layout = QGridLayout(self.buttons_container)
        self.buttons_layout.setSpacing(8)
        layout.addWidget(self.buttons_container)
        
        self.update_shifts()
        
    def set_fc(self, fc):
        self.fc = fc
        self.update_shifts()
        
    def update_shifts(self):
        while self.buttons_layout.count():
            child = self.buttons_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
                
        shifts = FCConfigs.get_shifts_for_fc(self.fc)
        colors = ['#10b981', '#f59e0b', '#3b82f6', '#8b5cf6']
        
        row, col = 0, 0
        for i, (shift_name, (start, end)) in enumerate(shifts.items()):
            btn = QPushButton(shift_name.upper())
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {colors[i % len(colors)]};
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 12px;
                    font-weight: bold;
                    font-size: 12px;
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
            
            self.buttons_layout.addWidget(btn, row, col)
            col += 1
            if col > 2:
                col = 0
                row += 1

class CompactModuleSelector(QWidget):
    """Compact module selector with proper proportions"""
    
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
        self.search_bar.setStyleSheet(BalancedTheme.get_input_style())
        self.search_bar.textChanged.connect(self.filter_modules)
        layout.addWidget(self.search_bar)
        
        # Tabs
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet(f"""
            QTabWidget::pane {{
                border: 2px solid {BalancedTheme.COLORS['border']};
                border-radius: 12px;
                background: {BalancedTheme.COLORS['bg_secondary']};
                padding: 12px;
            }}
            QTabBar::tab {{
                background: {BalancedTheme.COLORS['bg_tertiary']};
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                color: {BalancedTheme.COLORS['text_secondary']};
                font-weight: bold;
                min-width: 80px;
            }}
            QTabBar::tab:selected {{
                background: {BalancedTheme.COLORS['bg_secondary']};
                color: {BalancedTheme.COLORS['accent']};
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
            btn.setStyleSheet(BalancedTheme.get_button_style(variant))
            quick_layout.addWidget(btn)
            
        all_btn.clicked.connect(self.select_all)
        essential_btn.clicked.connect(self.select_essential)
        clear_btn.clicked.connect(self.clear_all)
        
        layout.addLayout(quick_layout)
        
    def create_module_tabs(self):
        for category, modules in self.modules.items():
            scroll_area = QScrollArea()
            scroll_widget = QWidget()
            scroll_layout = QVBoxLayout(scroll_widget)
            scroll_layout.setSpacing(6)
            
            for module in modules:
                checkbox = QCheckBox(module)
                checkbox.setStyleSheet(f"""
                    QCheckBox {{
                        font-size: 13px;
                        color: {BalancedTheme.COLORS['text_primary']};
                        padding: 6px;
                        spacing: 8px;
                    }}
                    QCheckBox::indicator {{
                        width: 16px;
                        height: 16px;
                        border: 2px solid {BalancedTheme.COLORS['border']};
                        border-radius: 4px;
                        background: {BalancedTheme.COLORS['bg_tertiary']};
                    }}
                    QCheckBox::indicator:checked {{
                        background: {BalancedTheme.COLORS['accent']};
                        border-color: {BalancedTheme.COLORS['accent']};
                    }}
                """)
                
                if module == "PPR_Q":
                    checkbox.setStyleSheet(checkbox.styleSheet() + f"""
                        QCheckBox {{
                            background: {BalancedTheme.COLORS['warning']};
                            color: black;
                            border-radius: 6px;
                            padding: 8px;
                            font-weight: bold;
                        }}
                    """)
                    
                scroll_layout.addWidget(checkbox)
                self.module_checkboxes[module] = checkbox
                
            scroll_layout.addStretch()
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

class BalancedParamsGenerator(QMainWindow):
    """Balanced params generator with perfect proportions"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OnePyFlow Params Generator V5.0 — Balanced Edition")
        self.setMinimumSize(1600, 900)
        self.setup_ui()
        self.setup_connections()
        
    def setup_ui(self):
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {BalancedTheme.COLORS['bg_primary']};
                color: {BalancedTheme.COLORS['text_primary']};
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 15px;
            }}
        """)
        
        central = QWidget()
        self.setCentralWidget(central)
        
        # Main layout with proper proportions
        main_layout = QHBoxLayout(central)
        main_layout.setSpacing(16)
        main_layout.setContentsMargins(16, 16, 16, 16)
        
        # Left panel - 35% width
        left_panel = QWidget()
        left_panel.setMaximumWidth(500)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setSpacing(12)
        
        # Site config - compact
        site_group = QGroupBox("Site Configuration")
        site_group.setStyleSheet(BalancedTheme.get_card_style())
        site_layout = QGridLayout(site_group)
        site_layout.setSpacing(8)
        
        self.site_combo = QComboBox()
        self.site_combo.addItems(FCConfigs.AVAILABLE_FCS)
        self.site_combo.setCurrentText("DTM2")
        self.site_combo.setStyleSheet(BalancedTheme.get_input_style())
        
        self.plan_combo = QComboBox()
        self.plan_combo.addItems(FCConfigs.PLAN_TYPES)
        self.plan_combo.setStyleSheet(BalancedTheme.get_input_style())
        
        site_layout.addWidget(QLabel("Site:"), 0, 0)
        site_layout.addWidget(self.site_combo, 0, 1)
        site_layout.addWidget(QLabel("Plan:"), 1, 0)
        site_layout.addWidget(self.plan_combo, 1, 1)
        
        left_layout.addWidget(site_group)
        
        # Schedule config - compact
        schedule_group = QGroupBox("Schedule Configuration")
        schedule_group.setStyleSheet(BalancedTheme.get_card_style())
        schedule_layout = QVBoxLayout(schedule_group)
        schedule_layout.setSpacing(8)
        
        self.schedule_picker = CompactSchedulePicker("DTM2")
        schedule_layout.addWidget(self.schedule_picker)
        
        self.shift_presets = CompactShiftPresets("DTM2")
        schedule_layout.addWidget(self.shift_presets)
        
        # DateTime inputs - compact
        dt_layout = QHBoxLayout()
        dt_layout.setSpacing(8)
        
        self.start_dt = QDateTimeEdit(QDateTime.currentDateTime().addSecs(-3600))
        self.start_dt.setDisplayFormat("MM-dd HH:mm")
        self.start_dt.setStyleSheet(BalancedTheme.get_input_style())
        
        self.end_dt = QDateTimeEdit(QDateTime.currentDateTime())
        self.end_dt.setDisplayFormat("MM-dd HH:mm")
        self.end_dt.setStyleSheet(BalancedTheme.get_input_style())
        
        dt_layout.addWidget(self.start_dt)
        dt_layout.addWidget(self.end_dt)
        schedule_layout.addLayout(dt_layout)
        
        left_layout.addWidget(schedule_group)
        
        # Actions - compact
        actions_group = QGroupBox("Actions")
        actions_group.setStyleSheet(BalancedTheme.get_card_style())
        actions_layout = QVBoxLayout(actions_group)
        actions_layout.setSpacing(8)
        
        # Output path - compact
        path_layout = QHBoxLayout()
        self.output_path = QLineEdit(os.getcwd())
        self.output_path.setStyleSheet(BalancedTheme.get_input_style())
        
        browse_btn = QPushButton("Browse")
        browse_btn.setStyleSheet(BalancedTheme.get_button_style('primary'))
        browse_btn.clicked.connect(self.browse_output)
        try:
            icon_path = os.path.join(os.path.dirname(__file__), 'icons', 'browse.svg')
            browse_btn.setIcon(QIcon(icon_path))
            browse_btn.setIconSize(QSize(18, 18))
        except Exception:
            pass
        
        path_layout.addWidget(self.output_path)
        path_layout.addWidget(browse_btn)
        actions_layout.addLayout(path_layout)
        
        # Action buttons - compact
        self.preview_btn = QPushButton("Preview")
        self.save_btn = QPushButton("Save")
        self.run_btn = QPushButton("Generate & Run")

        for btn, variant in [(self.preview_btn, 'primary'), (self.save_btn, 'success'), (self.run_btn, 'success')]:
            btn.setStyleSheet(BalancedTheme.get_button_style(variant))
            actions_layout.addWidget(btn)
        # Attach icons to buttons
        try:
            base = os.path.join(os.path.dirname(__file__), 'icons')
            self.preview_btn.setIcon(QIcon(os.path.join(base, 'preview.svg')))
            self.preview_btn.setIconSize(QSize(18, 18))
            self.save_btn.setIcon(QIcon(os.path.join(base, 'save.svg')))
            self.save_btn.setIconSize(QSize(18, 18))
            self.run_btn.setIcon(QIcon(os.path.join(base, 'run.svg')))
            self.run_btn.setIconSize(QSize(18, 18))
        except Exception:
            pass
            
        left_layout.addWidget(actions_group)
        left_layout.addStretch()
        
        # Right panel - 65% width
        right_panel = QGroupBox("Module Selection")
        right_panel.setStyleSheet(BalancedTheme.get_card_style())
        right_layout = QVBoxLayout(right_panel)
        
        self.module_selector = CompactModuleSelector()
        right_layout.addWidget(self.module_selector)
        
        # Add panels with proper proportions
        main_layout.addWidget(left_panel, 35)
        main_layout.addWidget(right_panel, 65)
        
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
            "GeneratedBy": "OnePyFlow Params Generator V5.0 - Balanced Edition",
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
        dialog.setStyleSheet(f"background-color: {BalancedTheme.COLORS['bg_primary']}; color: {BalancedTheme.COLORS['text_primary']};")
        
        layout = QVBoxLayout(dialog)
        text = QTextEdit()
        text.setPlainText(json.dumps(params, indent=4))
        text.setReadOnly(True)
        text.setStyleSheet(f"""
            background-color: {BalancedTheme.COLORS['bg_secondary']};
            border: 2px solid {BalancedTheme.COLORS['border']};
            border-radius: 8px;
            padding: 12px;
            font-family: 'Consolas', monospace;
            font-size: 12px;
            color: {BalancedTheme.COLORS['text_primary']};
        """)
        layout.addWidget(text)
        
        close_btn = QPushButton("Close")
        close_btn.setStyleSheet(BalancedTheme.get_button_style('primary'))
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
    
    window = BalancedParamsGenerator()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
