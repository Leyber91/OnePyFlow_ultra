"""
Beautiful visual schedule picker with modern design
"""

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from .fc_configs import FCConfigs
from .modern_theme import ModernTheme

class BeautifulSchedulePicker(QWidget):
    """Beautiful visual schedule picker with glassmorphism design"""
    
    schedule_changed = pyqtSignal(float, float)
    
    def __init__(self, fc="DTM2"):
        super().__init__()
        self.fc = fc
        self.start_hour = 6.0
        self.end_hour = 14.0
        self.setMinimumHeight(180)
        self.setMaximumHeight(180)
        self.setToolTip("Left click: Set start time | Right click: Set end time")
        
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
        margin = 20
        timeline_rect = QRect(margin, margin + 40, rect.width() - 2*margin, 60)
        
        # Draw glassmorphism background
        painter.setBrush(QBrush(QColor(30, 41, 59, 200)))
        painter.setPen(QPen(QColor(255, 255, 255, 50), 2))
        painter.drawRoundedRect(rect.adjusted(10, 10, -10, -10), 20, 20)
        
        # Draw timeline background with gradient
        gradient = QLinearGradient(timeline_rect.topLeft(), timeline_rect.bottomRight())
        gradient.setColorAt(0, QColor(30, 58, 138, 100))
        gradient.setColorAt(1, QColor(59, 130, 246, 100))
        painter.setBrush(QBrush(gradient))
        painter.setPen(QPen(QColor(255, 255, 255, 100), 1))
        painter.drawRoundedRect(timeline_rect, 12, 12)
        
        # Draw hour markers with glow effect
        painter.setPen(QPen(QColor(203, 213, 225), 2))
        for hour in range(0, 25, 6):
            x = int(timeline_rect.left() + (hour / 24) * timeline_rect.width())
            painter.drawLine(x, timeline_rect.top() + 10, x, timeline_rect.bottom() - 10)
            
            # Hour labels with modern font
            painter.setPen(QColor(203, 213, 225))
            painter.setFont(QFont('Segoe UI', 11, QFont.Bold))
            painter.drawText(x - 20, timeline_rect.bottom() + 25, f"{hour:02d}:00")
            
        # Draw beautiful shift block with gradient
        start_x = int(timeline_rect.left() + (self.start_hour / 24) * timeline_rect.width())
        end_x = int(timeline_rect.left() + (self.end_hour / 24) * timeline_rect.width())
        
        # Create shift gradient
        shift_gradient = QLinearGradient(start_x, timeline_rect.top(), end_x, timeline_rect.bottom())
        shift_gradient.setColorAt(0, QColor(0, 212, 255, 200))
        shift_gradient.setColorAt(1, QColor(14, 165, 233, 200))
        
        if self.end_hour < self.start_hour:
            # Overnight shift - two blocks
            painter.setBrush(QBrush(shift_gradient))
            painter.setPen(QPen(QColor(0, 212, 255), 2))
            painter.drawRoundedRect(QRect(start_x, timeline_rect.top() + 15, 
                                        timeline_rect.right() - start_x, timeline_rect.height() - 30), 8, 8)
            painter.drawRoundedRect(QRect(timeline_rect.left(), timeline_rect.top() + 15,
                                        end_x - timeline_rect.left(), timeline_rect.height() - 30), 8, 8)
        else:
            # Single block
            painter.setBrush(QBrush(shift_gradient))
            painter.setPen(QPen(QColor(0, 212, 255), 2))
            painter.drawRoundedRect(QRect(start_x, timeline_rect.top() + 15,
                                        end_x - start_x, timeline_rect.height() - 30), 8, 8)
            
        # Draw time labels with modern styling
        painter.setPen(QColor(255, 255, 255))
        painter.setFont(QFont('Segoe UI', 14, QFont.Bold))
        start_text = FCConfigs.format_time(self.start_hour)
        end_text = FCConfigs.format_time(self.end_hour)
        
        # Add glow effect to text
        painter.setPen(QPen(QColor(0, 212, 255), 3))
        painter.drawText(timeline_rect.left(), timeline_rect.top() - 10, f"🕐 Start: {start_text}")
        painter.drawText(timeline_rect.right() - 120, timeline_rect.top() - 10, f"🕐 End: {end_text}")
        
        painter.setPen(QColor(255, 255, 255))
        painter.drawText(timeline_rect.left(), timeline_rect.top() - 10, f"🕐 Start: {start_text}")
        painter.drawText(timeline_rect.right() - 120, timeline_rect.top() - 10, f"🕐 End: {end_text}")
        
    def mousePressEvent(self, event):
        rect = self.rect()
        margin = 20
        timeline_rect = QRect(margin, margin + 40, rect.width() - 2*margin, 60)
        
        if timeline_rect.contains(event.pos()):
            relative_x = event.pos().x() - timeline_rect.left()
            hour = (relative_x / timeline_rect.width()) * 24
            
            if event.button() == Qt.LeftButton:
                self.start_hour = hour
            elif event.button() == Qt.RightButton:
                self.end_hour = hour
                
            self.schedule_changed.emit(self.start_hour, self.end_hour)
            self.update()

class ModernShiftPresets(QWidget):
    """Modern shift preset buttons with beautiful styling"""
    
    shift_selected = pyqtSignal(str)
    
    def __init__(self, fc="DTM2"):
        super().__init__()
        self.fc = fc
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        
        # Title with icon
        title_layout = QHBoxLayout()
        icon_label = QLabel("⚡")
        icon_label.setStyleSheet(f"font-size: 24px; color: {ModernTheme.COLORS['accent_primary']};")
        
        title = QLabel("Quick Shift Presets")
        title.setStyleSheet(f"""
            color: {ModernTheme.COLORS['text_primary']};
            font-family: {ModernTheme.FONTS['heading']['family']};
            font-size: {ModernTheme.FONTS['heading']['size']}px;
            font-weight: {ModernTheme.FONTS['heading']['weight']};
            margin-left: 8px;
        """)
        
        title_layout.addWidget(icon_label)
        title_layout.addWidget(title)
        title_layout.addStretch()
        layout.addLayout(title_layout)
        
        # Shift buttons container
        self.buttons_container = QWidget()
        self.buttons_layout = QGridLayout(self.buttons_container)
        self.buttons_layout.setSpacing(12)
        layout.addWidget(self.buttons_container)
        
        self.update_shifts()
        
    def set_fc(self, fc):
        self.fc = fc
        self.update_shifts()
        
    def update_shifts(self):
        # Clear existing buttons
        while self.buttons_layout.count():
            child = self.buttons_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
                
        shifts = FCConfigs.get_shifts_for_fc(self.fc)
        shift_colors = {
            'es': ModernTheme.COLORS['shift_es'],
            'ls': ModernTheme.COLORS['shift_ls'], 
            'ns': ModernTheme.COLORS['shift_ns'],
            'cs-sat': ModernTheme.COLORS['shift_cs'],
            'cs-sun': ModernTheme.COLORS['shift_cs']
        }
        
        row, col = 0, 0
        for shift_name, (start, end) in shifts.items():
            btn = QPushButton(shift_name.upper())
            color = shift_colors.get(shift_name, ModernTheme.COLORS['accent_primary'])
            
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                        stop:0 {color}, stop:1 rgba(255,255,255,0.1));
                    color: #1e293b;
                    font-weight: bold;
                    border: none;
                    border-radius: 12px;
                    padding: 16px;
                    min-height: 50px;
                    font-size: 14px;
                }}
                QPushButton:hover {{
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                        stop:0 rgba(255,255,255,0.2), stop:1 {color});
                    transform: translateY(-3px);
                }}
                QPushButton:pressed {{
                    transform: translateY(0px);
                }}
            """)
            
            start_str = FCConfigs.format_time(start)
            end_str = FCConfigs.format_time(end % 24)
            btn.setToolTip(f"{FCConfigs.get_shift_display_name(shift_name)}\n🕐 {start_str} - {end_str}")
            btn.clicked.connect(lambda checked, s=shift_name: self.shift_selected.emit(s))
            
            self.buttons_layout.addWidget(btn, row, col)
            col += 1
            if col > 2:
                col = 0
                row += 1
