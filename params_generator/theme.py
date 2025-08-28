"""
Theme and styling constants for OnePyFlow Params Generator
"""

class Theme:
    """Modern dark theme with proper colors and spacing"""
    
    # Color palette
    COLORS = {
        'bg_primary': '#0a0a0a',
        'bg_secondary': '#1a1a1a', 
        'bg_tertiary': '#2a2a2a',
        'accent': '#00ff88',
        'accent_hover': '#00cc66',
        'text_primary': '#ffffff',
        'text_secondary': '#cccccc',
        'text_muted': '#888888',
        'border': '#333333',
        'success': '#00ff88',
        'warning': '#ffaa00',
        'error': '#ff4444',
        'info': '#0088ff'
    }
    
    # Font sizes
    FONTS = {
        'small': 12,
        'medium': 14,
        'large': 16,
        'xlarge': 18
    }
    
    # Spacing
    SPACING = {
        'xs': 4,
        'sm': 8,
        'md': 12,
        'lg': 16,
        'xl': 20,
        'xxl': 24
    }
    
    # Component styles
    STYLES = {
        'main_window': f"""
            QMainWindow {{ 
                background: {COLORS['bg_primary']}; 
                color: {COLORS['text_primary']}; 
            }}
        """,
        
        'group_box': f"""
            QGroupBox {{ 
                border: 2px solid {COLORS['accent']}; 
                border-radius: 12px; 
                margin: 8px; 
                padding: 16px;
                font-weight: bold;
                font-size: {FONTS['medium']}px;
                color: {COLORS['text_primary']};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }}
        """,
        
        'input_field': f"""
            QComboBox, QLineEdit, QDateTimeEdit {{
                background: {COLORS['bg_tertiary']};
                border: 2px solid {COLORS['border']};
                border-radius: 8px;
                padding: 12px;
                font-size: {FONTS['medium']}px;
                color: {COLORS['text_primary']};
                min-height: 20px;
            }}
            QComboBox:focus, QLineEdit:focus, QDateTimeEdit:focus {{
                border-color: {COLORS['accent']};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid {COLORS['text_secondary']};
                margin-right: 5px;
            }}
        """,
        
        'button_primary': f"""
            QPushButton {{
                background: {COLORS['accent']};
                color: {COLORS['bg_primary']};
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-weight: bold;
                font-size: {FONTS['medium']}px;
                min-height: 40px;
            }}
            QPushButton:hover {{ 
                background: {COLORS['accent_hover']}; 
            }}
            QPushButton:pressed {{ 
                background: {COLORS['success']}; 
            }}
        """,
        
        'button_secondary': f"""
            QPushButton {{
                background: {COLORS['bg_tertiary']};
                color: {COLORS['text_primary']};
                border: 2px solid {COLORS['border']};
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: {FONTS['small']}px;
                min-height: 30px;
            }}
            QPushButton:hover {{ 
                background: {COLORS['bg_secondary']};
                border-color: {COLORS['accent']};
            }}
            QPushButton:pressed {{ 
                background: {COLORS['border']}; 
            }}
        """,
        
        'checkbox': f"""
            QCheckBox {{ 
                font-size: {FONTS['medium']}px; 
                padding: 8px; 
                spacing: 12px;
                color: {COLORS['text_primary']};
            }}
            QCheckBox::indicator {{
                width: 20px; 
                height: 20px;
                border: 2px solid {COLORS['border']};
                border-radius: 4px;
                background: {COLORS['bg_tertiary']};
            }}
            QCheckBox::indicator:checked {{
                background: {COLORS['accent']};
                border-color: {COLORS['accent']};
            }}
            QCheckBox::indicator:hover {{
                border-color: {COLORS['accent_hover']};
            }}
        """,
        
        'scroll_area': f"""
            QScrollArea {{
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                background: {COLORS['bg_secondary']};
            }}
            QScrollBar:vertical {{
                background: {COLORS['bg_tertiary']};
                width: 12px;
                border-radius: 6px;
            }}
            QScrollBar::handle:vertical {{
                background: {COLORS['accent']};
                border-radius: 6px;
                min-height: 20px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {COLORS['accent_hover']};
            }}
        """
    }
    
    @classmethod
    def get_shift_color(cls, shift_type):
        """Get color for shift type"""
        shift_colors = {
            'es': cls.COLORS['success'],
            'ls': cls.COLORS['warning'], 
            'ns': cls.COLORS['info'],
            'cs-sat': cls.COLORS['accent'],
            'cs-sun': cls.COLORS['error']
        }
        return shift_colors.get(shift_type.lower(), cls.COLORS['accent'])
