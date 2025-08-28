"""
Modern glassmorphism theme with gradients and beautiful styling
"""

class ModernTheme:
    """Modern glassmorphism theme with beautiful gradients"""
    
    # Modern color palette
    COLORS = {
        # Background gradients
        'bg_primary': 'qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #0f0f23, stop:1 #1a1a2e)',
        'bg_secondary': 'qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #16213e, stop:1 #0f3460)',
        'bg_tertiary': 'qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #1e3a8a, stop:1 #3b82f6)',
        'bg_glass': 'rgba(255, 255, 255, 0.1)',
        'bg_card': 'rgba(30, 41, 59, 0.8)',
        
        # Accent colors
        'accent_primary': '#00d4ff',
        'accent_secondary': '#ff6b6b',
        'accent_success': '#4ecdc4',
        'accent_warning': '#ffe66d',
        'accent_error': '#ff5757',
        
        # Text colors
        'text_primary': '#ffffff',
        'text_secondary': '#cbd5e1',
        'text_muted': '#64748b',
        'text_accent': '#00d4ff',
        
        # Border and shadow
        'border_light': 'rgba(255, 255, 255, 0.2)',
        'border_accent': 'rgba(0, 212, 255, 0.5)',
        'shadow': 'rgba(0, 0, 0, 0.3)',
        
        # Shift colors
        'shift_es': '#4ade80',
        'shift_ls': '#fbbf24', 
        'shift_ns': '#60a5fa',
        'shift_cs': '#a78bfa'
    }
    
    # Typography
    FONTS = {
        'title': {'family': 'Segoe UI', 'size': 24, 'weight': 'bold'},
        'heading': {'family': 'Segoe UI', 'size': 18, 'weight': 'bold'},
        'subheading': {'family': 'Segoe UI', 'size': 16, 'weight': 'normal'},
        'body': {'family': 'Segoe UI', 'size': 14, 'weight': 'normal'},
        'small': {'family': 'Segoe UI', 'size': 12, 'weight': 'normal'},
        'code': {'family': 'JetBrains Mono', 'size': 13, 'weight': 'normal'}
    }
    
    # Spacing system
    SPACING = {
        'xs': 4, 'sm': 8, 'md': 16, 'lg': 24, 'xl': 32, 'xxl': 48
    }
    
    # Border radius
    RADIUS = {
        'sm': 6, 'md': 12, 'lg': 20, 'xl': 24, 'full': 9999
    }
    
    @classmethod
    def get_main_window_style(cls):
        """Get main window styling"""
        return f"""
            QMainWindow {{
                background: {cls.COLORS['bg_primary']};
                color: {cls.COLORS['text_primary']};
            }}
        """
    
    @classmethod
    def get_glass_card_style(cls):
        """Get glassmorphism card styling"""
        return f"""
            QGroupBox {{
                background: {cls.COLORS['bg_card']};
                border: 1px solid {cls.COLORS['border_light']};
                border-radius: {cls.RADIUS['lg']}px;
                padding: {cls.SPACING['lg']}px;
                margin: {cls.SPACING['sm']}px;
                font-family: {cls.FONTS['heading']['family']};
                font-size: {cls.FONTS['heading']['size']}px;
                font-weight: {cls.FONTS['heading']['weight']};
                color: {cls.COLORS['text_primary']};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: {cls.SPACING['md']}px;
                padding: 0 {cls.SPACING['sm']}px;
                color: {cls.COLORS['accent_primary']};
                background: transparent;
            }}
        """
    
    @classmethod
    def get_modern_input_style(cls):
        """Get modern input field styling"""
        return f"""
            QComboBox, QLineEdit, QDateTimeEdit {{
                background: {cls.COLORS['bg_glass']};
                border: 2px solid {cls.COLORS['border_light']};
                border-radius: {cls.RADIUS['md']}px;
                padding: {cls.SPACING['md']}px {cls.SPACING['lg']}px;
                font-family: {cls.FONTS['body']['family']};
                font-size: {cls.FONTS['body']['size']}px;
                color: {cls.COLORS['text_primary']};
                min-height: 24px;
                selection-background-color: {cls.COLORS['accent_primary']};
            }}
            QComboBox:focus, QLineEdit:focus, QDateTimeEdit:focus {{
                border-color: {cls.COLORS['accent_primary']};
                background: rgba(0, 212, 255, 0.1);
            }}
            QComboBox:hover, QLineEdit:hover, QDateTimeEdit:hover {{
                border-color: {cls.COLORS['border_accent']};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 30px;
                border-top-right-radius: {cls.RADIUS['md']}px;
                border-bottom-right-radius: {cls.RADIUS['md']}px;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 6px solid transparent;
                border-right: 6px solid transparent;
                border-top: 8px solid {cls.COLORS['text_secondary']};
                margin-right: 8px;
            }}
        """
    
    @classmethod
    def get_modern_button_style(cls, variant='primary'):
        """Get modern button styling"""
        if variant == 'primary':
            bg_color = f"qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 {cls.COLORS['accent_primary']}, stop:1 #0ea5e9)"
            hover_bg = f"qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #0ea5e9, stop:1 {cls.COLORS['accent_primary']})"
        elif variant == 'success':
            bg_color = f"qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 {cls.COLORS['accent_success']}, stop:1 #10b981)"
            hover_bg = f"qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #10b981, stop:1 {cls.COLORS['accent_success']})"
        elif variant == 'warning':
            bg_color = f"qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 {cls.COLORS['accent_warning']}, stop:1 #f59e0b)"
            hover_bg = f"qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #f59e0b, stop:1 {cls.COLORS['accent_warning']})"
        elif variant == 'error':
            bg_color = f"qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 {cls.COLORS['accent_error']}, stop:1 #ef4444)"
            hover_bg = f"qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #ef4444, stop:1 {cls.COLORS['accent_error']})"
        else:  # secondary
            bg_color = cls.COLORS['bg_glass']
            hover_bg = 'rgba(255, 255, 255, 0.2)'
            
        return f"""
            QPushButton {{
                background: {bg_color};
                color: {'#1e293b' if variant != 'secondary' else cls.COLORS['text_primary']};
                border: {'none' if variant != 'secondary' else f"2px solid {cls.COLORS['border_light']}"};
                border-radius: {cls.RADIUS['md']}px;
                padding: {cls.SPACING['md']}px {cls.SPACING['lg']}px;
                font-family: {cls.FONTS['body']['family']};
                font-size: {cls.FONTS['body']['size']}px;
                font-weight: bold;
                min-height: 40px;
            }}
            QPushButton:hover {{
                background: {hover_bg};
                transform: translateY(-2px);
            }}
            QPushButton:pressed {{
                transform: translateY(0px);
            }}
        """
    
    @classmethod
    def get_modern_checkbox_style(cls):
        """Get modern checkbox styling"""
        return f"""
            QCheckBox {{
                font-family: {cls.FONTS['body']['family']};
                font-size: {cls.FONTS['body']['size']}px;
                color: {cls.COLORS['text_primary']};
                padding: {cls.SPACING['sm']}px;
                spacing: {cls.SPACING['md']}px;
            }}
            QCheckBox::indicator {{
                width: 20px;
                height: 20px;
                border: 2px solid {cls.COLORS['border_light']};
                border-radius: 6px;
                background: {cls.COLORS['bg_glass']};
            }}
            QCheckBox::indicator:checked {{
                background: {cls.COLORS['accent_primary']};
                border-color: {cls.COLORS['accent_primary']};
                image: none;
            }}
            QCheckBox::indicator:checked::after {{
                content: "✓";
                color: white;
                font-weight: bold;
            }}
            QCheckBox::indicator:hover {{
                border-color: {cls.COLORS['accent_primary']};
                background: rgba(0, 212, 255, 0.1);
            }}
        """
    
    @classmethod
    def get_modern_tab_style(cls):
        """Get modern tab widget styling"""
        return f"""
            QTabWidget::pane {{
                border: 1px solid {cls.COLORS['border_light']};
                border-radius: {cls.RADIUS['lg']}px;
                background: {cls.COLORS['bg_card']};
                padding: {cls.SPACING['lg']}px;
            }}
            QTabBar::tab {{
                background: {cls.COLORS['bg_glass']};
                border: 1px solid {cls.COLORS['border_light']};
                border-bottom: none;
                border-top-left-radius: {cls.RADIUS['md']}px;
                border-top-right-radius: {cls.RADIUS['md']}px;
                padding: {cls.SPACING['md']}px {cls.SPACING['lg']}px;
                margin-right: 4px;
                color: {cls.COLORS['text_secondary']};
                font-family: {cls.FONTS['body']['family']};
                font-size: {cls.FONTS['body']['size']}px;
                font-weight: bold;
                min-width: 100px;
            }}
            QTabBar::tab:selected {{
                background: {cls.COLORS['bg_card']};
                color: {cls.COLORS['accent_primary']};
                border-bottom: 2px solid {cls.COLORS['accent_primary']};
            }}
            QTabBar::tab:hover {{
                background: rgba(0, 212, 255, 0.1);
                color: {cls.COLORS['text_primary']};
            }}
        """
    
    @classmethod
    def get_scroll_area_style(cls):
        """Get modern scroll area styling"""
        return f"""
            QScrollArea {{
                border: 1px solid {cls.COLORS['border_light']};
                border-radius: {cls.RADIUS['md']}px;
                background: transparent;
            }}
            QScrollBar:vertical {{
                background: {cls.COLORS['bg_glass']};
                width: 12px;
                border-radius: 6px;
                margin: 0;
            }}
            QScrollBar::handle:vertical {{
                background: {cls.COLORS['accent_primary']};
                border-radius: 6px;
                min-height: 20px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: #0ea5e9;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                border: none;
                background: none;
            }}
        """
