"""
🎨 Dark Matrix Theme for OnePyFlow Params Generator
Evolved, professional styling with custom elements and sophisticated design
"""

from PyQt5.QtCore import QSize
from PyQt5.QtGui import QFont, QPalette, QColor

class DarkMatrixTheme:
    """Dark Matrix theme with evolved, professional styling"""
    
    # Sophisticated color palette
    COLORS = {
        'bg_primary': '#0a0a0a',      # Deep black
        'bg_secondary': '#1a1a1a',    # Dark gray
        'bg_tertiary': '#2a2a2a',     # Medium gray
        'bg_elevated': '#333333',     # Elevated panels
        'accent_primary': '#00ff41',   # Matrix green
        'accent_secondary': '#00cc33', # Darker green
        'accent_tertiary': '#009926',  # Even darker green
        'accent_glow': '#00ff4120',    # Subtle green glow
        'text_primary': '#ffffff',     # Pure white
        'text_secondary': '#e0e0e0',   # Light gray
        'text_muted': '#a0a0a0',       # Muted gray
        'border': '#404040',           # Dark border
        'border_highlight': '#00ff41', # Green border
        'success': '#00ff41',          # Green
        'warning': '#ffaa00',          # Orange
        'error': '#ff4444',            # Red
        'info': '#00aaff',             # Blue
        'ppr_q_highlight': '#ffd700',  # Gold for PPR_Q
        'shadow': '#00000040',         # Subtle shadow
    }
    
    @classmethod
    def get_main_stylesheet(cls, scale_factor=1.0):
        """Get main application stylesheet with evolved design"""
        # Professional sizing
        base_size = max(12, int(13 * scale_factor))
        title_size = max(16, int(18 * scale_factor))
        subtitle_size = max(14, int(15 * scale_factor))
        button_height = max(40, int(44 * scale_factor))
        input_height = max(36, int(40 * scale_factor))
        padding = max(10, int(12 * scale_factor))
        margin = max(8, int(10 * scale_factor))
        border_radius = max(8, int(10 * scale_factor))
        
        return f"""
        QMainWindow {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 {cls.COLORS['bg_primary']}, 
                stop:0.5 {cls.COLORS['bg_secondary']},
                stop:1 {cls.COLORS['bg_primary']});
            color: {cls.COLORS['text_primary']};
            font-family: 'Segoe UI', 'Consolas', sans-serif;
            font-size: {base_size}px;
        }}
        
        QWidget {{
            background: transparent;
            color: {cls.COLORS['text_primary']};
        }}
        
        QFrame {{
            background: {cls.COLORS['bg_elevated']};
            border: 1px solid {cls.COLORS['border']};
            border-radius: {border_radius}px;
            padding: {padding}px;
        }}
        
        QFrame:hover {{
            border-color: {cls.COLORS['border_highlight']};
        }}
        
        QLabel {{
            color: {cls.COLORS['text_primary']};
            font-size: {base_size}px;
            padding: {padding//2}px;
        }}
        
        QLabel[class="title"] {{
            font-size: {title_size}px;
            font-weight: bold;
            color: {cls.COLORS['accent_primary']};
            padding: {padding}px;
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 {cls.COLORS['accent_glow']}, 
                stop:1 transparent);
            border-radius: {border_radius//2}px;
        }}
        
        QLabel[class="subtitle"] {{
            font-size: {subtitle_size}px;
            font-weight: bold;
            color: {cls.COLORS['text_secondary']};
            padding: {padding//2}px;
        }}
        
        QLabel[class="icon"] {{
            font-family: 'Segoe UI Symbol', 'Arial Unicode MS', sans-serif;
            font-size: {title_size}px;
            color: {cls.COLORS['accent_primary']};
        }}
        
        QLineEdit {{
            background: {cls.COLORS['bg_tertiary']};
            border: 1px solid {cls.COLORS['border']};
            border-radius: {border_radius//2}px;
            padding: {padding}px;
            color: {cls.COLORS['text_primary']};
            font-size: {base_size}px;
            min-height: {input_height}px;
        }}
        
        QLineEdit:focus {{
            border-color: {cls.COLORS['accent_primary']};
            background: {cls.COLORS['bg_tertiary']};
        }}
        
        QComboBox {{
            background: {cls.COLORS['bg_tertiary']};
            border: 1px solid {cls.COLORS['border']};
            border-radius: {border_radius//2}px;
            padding: {padding}px;
            color: {cls.COLORS['text_primary']};
            font-size: {base_size}px;
            min-height: {input_height}px;
        }}
        
        QComboBox:focus {{
            border-color: {cls.COLORS['accent_primary']};
        }}
        
        QComboBox::drop-down {{
            border: none;
            width: 25px;
            background: {cls.COLORS['accent_primary']};
            border-radius: {border_radius//4}px;
        }}
        
        QComboBox::down-arrow {{
            image: none;
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 5px solid {cls.COLORS['bg_primary']};
            margin-right: 5px;
        }}
        
        QComboBox QAbstractItemView {{
            background: {cls.COLORS['bg_tertiary']};
            border: 1px solid {cls.COLORS['border']};
            border-radius: {border_radius//2}px;
            selection-background-color: {cls.COLORS['accent_primary']};
            color: {cls.COLORS['text_primary']};
            padding: {padding//2}px;
        }}
        
        QPushButton {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {cls.COLORS['accent_primary']}, 
                stop:1 {cls.COLORS['accent_secondary']});
            border: 1px solid {cls.COLORS['accent_primary']};
            border-radius: {border_radius}px;
            color: {cls.COLORS['bg_primary']};
            font-weight: bold;
            font-size: {base_size}px;
            padding: {padding}px {padding*2}px;
            min-height: {button_height}px;
        }}
        
        QPushButton:hover {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {cls.COLORS['accent_secondary']}, 
                stop:1 {cls.COLORS['accent_tertiary']});
            border-color: {cls.COLORS['accent_secondary']};
        }}
        
        QPushButton:pressed {{
            background: {cls.COLORS['accent_tertiary']};
            border-color: {cls.COLORS['accent_tertiary']};
        }}
        
        QPushButton[class="danger"] {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {cls.COLORS['error']}, 
                stop:1 #cc3333);
            border-color: {cls.COLORS['error']};
        }}
        
        QPushButton[class="warning"] {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {cls.COLORS['warning']}, 
                stop:1 #cc8800);
            border-color: {cls.COLORS['warning']};
        }}
        
        QPushButton[class="info"] {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {cls.COLORS['info']}, 
                stop:1 #0088cc);
            border-color: {cls.COLORS['info']};
        }}
        
        QPushButton[class="compact"] {{
            min-height: {input_height}px;
            padding: {padding//2}px {padding}px;
            font-size: {base_size-1}px;
        }}
        
        QCheckBox {{
            color: {cls.COLORS['text_primary']};
            font-size: {base_size}px;
            spacing: {padding}px;
        }}
        
        QCheckBox::indicator {{
            width: 18px;
            height: 18px;
            border-radius: 9px;
            border: 2px solid {cls.COLORS['border']};
            background: {cls.COLORS['bg_tertiary']};
        }}
        
        QCheckBox::indicator:checked {{
            background: {cls.COLORS['accent_primary']};
            border-color: {cls.COLORS['accent_primary']};
        }}
        
        QGroupBox {{
            font-weight: bold;
            border: 2px solid {cls.COLORS['border']};
            border-radius: {border_radius}px;
            margin-top: {margin*2}px;
            padding-top: {margin*2}px;
            color: {cls.COLORS['text_primary']};
            background: {cls.COLORS['bg_secondary']};
            padding: {padding}px;
        }}
        
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: {margin}px;
            padding: 0 {padding}px 0 {padding}px;
            background: {cls.COLORS['bg_secondary']};
            color: {cls.COLORS['accent_primary']};
            font-size: {subtitle_size}px;
        }}
        
        QTabWidget::pane {{
            border: 2px solid {cls.COLORS['border']};
            border-radius: {border_radius}px;
            background: {cls.COLORS['bg_secondary']};
            padding: {padding}px;
        }}
        
        QTabBar::tab {{
            background: {cls.COLORS['bg_tertiary']};
            padding: {padding}px {padding*1.5}px;
            margin-right: 3px;
            border-top-left-radius: {border_radius//2}px;
            border-top-right-radius: {border_radius//2}px;
            font-weight: bold;
            min-width: 100px;
            color: {cls.COLORS['text_secondary']};
            font-size: {base_size}px;
        }}
        
        QTabBar::tab:selected {{
            background: {cls.COLORS['bg_secondary']};
            color: {cls.COLORS['accent_primary']};
            border-bottom: 3px solid {cls.COLORS['accent_primary']};
        }}
        
        QTabBar::tab:hover {{
            background: {cls.COLORS['bg_secondary']};
            color: {cls.COLORS['text_primary']};
        }}
        
        QScrollArea {{
            border: none;
            background: transparent;
        }}
        
        QScrollBar:vertical {{
            background: {cls.COLORS['bg_tertiary']};
            width: 14px;
            border-radius: 7px;
        }}
        
        QScrollBar::handle:vertical {{
            background: {cls.COLORS['accent_primary']};
            border-radius: 7px;
            min-height: 30px;
        }}
        
        QScrollBar::handle:vertical:hover {{
            background: {cls.COLORS['accent_secondary']};
        }}
        
        QTextEdit {{
            background: {cls.COLORS['bg_primary']};
            color: {cls.COLORS['text_primary']};
            border: 1px solid {cls.COLORS['border']};
            border-radius: {border_radius}px;
            padding: {padding}px;
            font-family: 'Consolas', 'Courier New', monospace;
            font-size: {base_size}px;
            line-height: 1.4;
        }}
        
        QMessageBox {{
            background: {cls.COLORS['bg_secondary']};
            color: {cls.COLORS['text_primary']};
            border-radius: {border_radius}px;
            padding: {padding}px;
        }}
        
        QMessageBox QPushButton {{
            background: {cls.COLORS['accent_primary']};
            color: {cls.COLORS['bg_primary']};
            border: none;
            border-radius: {border_radius//2}px;
            padding: {padding}px {padding*1.5}px;
            font-weight: bold;
            min-height: {button_height}px;
        }}
        
        QDialog {{
            background: {cls.COLORS['bg_secondary']};
            border-radius: {border_radius}px;
            padding: {padding}px;
        }}
        
        QDateTimeEdit {{
            background: {cls.COLORS['bg_tertiary']};
            border: 1px solid {cls.COLORS['border']};
            border-radius: {border_radius//2}px;
            padding: {padding}px;
            color: {cls.COLORS['text_primary']};
            font-size: {base_size}px;
            min-height: {input_height}px;
        }}
        
        QDateTimeEdit:focus {{
            border-color: {cls.COLORS['accent_primary']};
        }}
        
        QDateTimeEdit::drop-down {{
            border: none;
            width: 25px;
            background: {cls.COLORS['accent_primary']};
            border-radius: {border_radius//4}px;
        }}
        
        QDateTimeEdit::down-arrow {{
            image: none;
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 5px solid {cls.COLORS['bg_primary']};
            margin-right: 5px;
        }}
        """
    
    @classmethod
    def get_ppr_q_stylesheet(cls, scale_factor=1.0):
        """Special styling for PPR_Q elements with evolved design"""
        base_size = max(14, int(15 * scale_factor))
        padding = max(12, int(14 * scale_factor))
        border_radius = max(8, int(10 * scale_factor))
        
        return f"""
        QCheckBox[class="ppr_q"] {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 {cls.COLORS['ppr_q_highlight']}, 
                stop:1 #1a1a00);
            color: {cls.COLORS['bg_primary']};
            border-radius: {border_radius}px;
            padding: {padding}px;
            font-weight: bold;
            font-size: {base_size}px;
            margin: 3px;
            border: 2px solid {cls.COLORS['ppr_q_highlight']};
        }}
        
        QCheckBox[class="ppr_q"]:hover {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #ffdf33, 
                stop:1 #2a2a00);
            border-color: #ffdf33;
        }}
        
        QCheckBox[class="ppr_q"]::indicator {{
            width: 20px;
            height: 20px;
            border-radius: 10px;
            border: 2px solid {cls.COLORS['ppr_q_highlight']};
            background: {cls.COLORS['bg_primary']};
        }}
        
        QCheckBox[class="ppr_q"]::indicator:checked {{
            background: {cls.COLORS['ppr_q_highlight']};
            border-color: {cls.COLORS['ppr_q_highlight']};
        }}
        
        QGroupBox[class="ppr_q"] {{
            border: 2px solid {cls.COLORS['ppr_q_highlight']};
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #1a1a00, 
                stop:1 {cls.COLORS['bg_secondary']});
            color: {cls.COLORS['ppr_q_highlight']};
        }}
        
        QGroupBox[class="ppr_q"]::title {{
            background: {cls.COLORS['bg_secondary']};
            color: {cls.COLORS['ppr_q_highlight']};
            font-weight: bold;
        }}
        """
    
    @classmethod
    def apply_theme(cls, app, scale_factor=1.0):
        """Apply the dark matrix theme to the application"""
        # Set application palette
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(cls.COLORS['bg_primary']))
        palette.setColor(QPalette.WindowText, QColor(cls.COLORS['text_primary']))
        palette.setColor(QPalette.Base, QColor(cls.COLORS['bg_tertiary']))
        palette.setColor(QPalette.AlternateBase, QColor(cls.COLORS['bg_secondary']))
        palette.setColor(QPalette.ToolTipBase, QColor(cls.COLORS['bg_secondary']))
        palette.setColor(QPalette.ToolTipText, QColor(cls.COLORS['text_primary']))
        palette.setColor(QPalette.Text, QColor(cls.COLORS['text_primary']))
        palette.setColor(QPalette.Button, QColor(cls.COLORS['accent_primary']))
        palette.setColor(QPalette.ButtonText, QColor(cls.COLORS['bg_primary']))
        palette.setColor(QPalette.BrightText, QColor(cls.COLORS['accent_primary']))
        palette.setColor(QPalette.Link, QColor(cls.COLORS['accent_primary']))
        palette.setColor(QPalette.Highlight, QColor(cls.COLORS['accent_primary']))
        palette.setColor(QPalette.HighlightedText, QColor(cls.COLORS['bg_primary']))
        
        app.setPalette(palette)
        app.setStyleSheet(cls.get_main_stylesheet(scale_factor))
        
        # Set application font
        font = QFont('Segoe UI', max(10, int(11 * scale_factor)))
        app.setFont(font) 