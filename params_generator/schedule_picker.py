"""
Visual schedule picker widget for shift selection
"""

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from .fc_configs import FCConfigs
from .theme import Theme

class VisualSchedulePicker(QWidget):
    """Visual 24-hour schedule picker with FC-specific presets"""
    
    schedule_changed = pyqtSignal(float, float)  # start_hour, end_hour
    
    def __init__(self, fc="DTM2"):
        super().__init__()
        self.fc = fc
        self.start_hour = 6.0
        self.end_hour = 14.0
        self.setMinimumHeight(120)
        self.setMaximumHeight(120)
        self.setToolTip("Left click: Set start time | Right click: Set end time")
        
    def set_fc(self, fc):
        """Update FC and refresh display"""
        self.fc = fc
        self.update()
        
    def set_shift(self, shift_name):
        """Set shift times based on FC and shift name"""
        start, end = FCConfigs.get_shift_times(self.fc, shift_name)
        self.start_hour = start
        self.end_hour = end % 24 if end >= 24 else end
        self.schedule_changed.emit(self.start_hour, self.end_hour)
        self.update()
        
    def paintEvent(self, event):
        """Draw the visual schedule picker"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        rect = self.rect()
        margin = 10
        timeline_rect = QRect(margin, margin + 20, rect.width() - 2*margin, 40)
        
        # Draw timeline background
        painter.fillRect(timeline_rect, QColor(Theme.COLORS['bg_tertiary']))
        painter.setPen(QPen(QColor(Theme.COLORS['border']), 1))
        painter.drawRect(timeline_rect)
        
        # Draw hour markers
        painter.setPen(QPen(QColor(Theme.COLORS['border']), 1))
        for hour in range(0, 25, 6):
            x = int(timeline_rect.left() + (hour / 24) * timeline_rect.width())
            painter.drawLine(x, timeline_rect.top(), x, timeline_rect.bottom())
            
            # Hour labels
            painter.setPen(QColor(Theme.COLORS['text_secondary']))
            painter.setFont(QFont('Segoe UI', 10))
            painter.drawText(x - 15, timeline_rect.bottom() + 15, f"{hour:02d}:00")
            
        # Draw shift block
        start_x = int(timeline_rect.left() + (self.start_hour / 24) * timeline_rect.width())
        end_x = int(timeline_rect.left() + (self.end_hour / 24) * timeline_rect.width())
        
        # Handle overnight shifts
        if self.end_hour < self.start_hour:
            # Draw two blocks for overnight shift
            painter.fillRect(QRect(start_x, timeline_rect.top() + 5, 
                                 timeline_rect.right() - start_x, timeline_rect.height() - 10),
                           QColor(Theme.COLORS['accent']))
            painter.fillRect(QRect(timeline_rect.left(), timeline_rect.top() + 5,
                                 end_x - timeline_rect.left(), timeline_rect.height() - 10),
                           QColor(Theme.COLORS['accent']))
        else:
            # Single block for same-day shift
            painter.fillRect(QRect(start_x, timeline_rect.top() + 5,
                                 end_x - start_x, timeline_rect.height() - 10),
                           QColor(Theme.COLORS['accent']))
            
        # Draw time labels
        painter.setPen(QColor(Theme.COLORS['text_primary']))
        painter.setFont(QFont('Segoe UI', 10, QFont.Bold))
        start_text = FCConfigs.format_time(self.start_hour)
        end_text = FCConfigs.format_time(self.end_hour)
        painter.drawText(timeline_rect.left(), timeline_rect.top() - 5, f"Start: {start_text}")
        painter.drawText(timeline_rect.right() - 80, timeline_rect.top() - 5, f"End: {end_text}")
        
    def mousePressEvent(self, event):
        """Handle mouse clicks to set times"""
        rect = self.rect()
        margin = 10
        timeline_rect = QRect(margin, margin + 20, rect.width() - 2*margin, 40)
        
        if timeline_rect.contains(event.pos()):
            relative_x = event.pos().x() - timeline_rect.left()
            hour = (relative_x / timeline_rect.width()) * 24
            
            if event.button() == Qt.LeftButton:
                self.start_hour = hour
            elif event.button() == Qt.RightButton:
                self.end_hour = hour
                
            self.schedule_changed.emit(self.start_hour, self.end_hour)
            self.update()

class ShiftPresetWidget(QWidget):
    """Modern shift preset selector"""
    
    shift_selected = pyqtSignal(str)
    
    def __init__(self, fc="DTM2"):
        super().__init__()
        self.fc = fc
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(Theme.SPACING['sm'])
        
        # Title
        title = QLabel("Quick Shift Presets")
        title.setStyleSheet(f"""
            color: {Theme.COLORS['text_primary']};
            font-size: {Theme.FONTS['medium']}px;
            font-weight: bold;
            margin-bottom: 8px;
        """)
        layout.addWidget(title)
        
        # Shift buttons container
        self.buttons_container = QWidget()
        self.buttons_layout = QGridLayout(self.buttons_container)
        self.buttons_layout.setSpacing(Theme.SPACING['sm'])
        layout.addWidget(self.buttons_container)
        
        self.update_shifts()
        
    def set_fc(self, fc):
        """Update FC and refresh shift buttons"""
        self.fc = fc
        self.update_shifts()
        
    def update_shifts(self):
        """Update shift buttons based on current FC"""
        # Clear existing buttons
        while self.buttons_layout.count():
            child = self.buttons_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
                
        shifts = FCConfigs.get_shifts_for_fc(self.fc)
        
        row, col = 0, 0
        for shift_name, (start, end) in shifts.items():
            btn = QPushButton(shift_name.upper())
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: {Theme.get_shift_color(shift_name)};
                    color: {Theme.COLORS['bg_primary']};
                    font-weight: bold;
                    border-radius: 8px;
                    padding: 12px;
                    min-height: 40px;
                    font-size: {Theme.FONTS['small']}px;
                }}
                QPushButton:hover {{
                    background: {Theme.COLORS['accent_hover']};
                }}
            """)
            
            start_str = FCConfigs.format_time(start)
            end_str = FCConfigs.format_time(end % 24)
            btn.setToolTip(f"{FCConfigs.get_shift_display_name(shift_name)}\n{start_str} - {end_str}")
            btn.clicked.connect(lambda checked, s=shift_name: self.shift_selected.emit(s))
            
            self.buttons_layout.addWidget(btn, row, col)
            col += 1
            if col > 2:
                col = 0
                row += 1
