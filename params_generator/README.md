# 🚀 OnePyFlow Params Generator V2.0 - Dark Matrix Edition

## Overview
A completely redesigned, modular parameters generator with a dark matrix theme and adaptive UI sizing.

## Features
- 🌙 **Dark Matrix Theme**: Black background with green accents
- 📱 **Adaptive Sizing**: Automatically scales based on screen resolution
- 🧩 **Modular Architecture**: Clean separation of concerns
- 🎨 **Modern UI**: Smooth animations and professional styling
- ⚡ **Fast Performance**: Optimized for responsiveness

## File Structure
```
params_generator/
├── __init__.py          # Package initialization
├── main_window.py       # Main application window
├── components.py        # UI components (buttons, panels, selectors)
├── themes.py           # Dark matrix theme and styling
└── README.md           # This documentation
```

## Components

### Main Window (`main_window.py`)
- Main application class
- Adaptive sizing calculation
- Layout management
- Parameter generation and saving

### Components (`components.py`)
- `ModernButton`: Styled buttons with hover effects
- `SmartDateTimeWidget`: DateTime picker with presets
- `AdvancedModuleSelector`: Tabbed module selection
- `ConfigurationPanel`: Site and time configuration
- `ActionPanel`: Output and action buttons

### Themes (`themes.py`)
- `DarkMatrixTheme`: Complete dark theme with green accents
- Adaptive styling based on scale factor
- Color palette management

## Usage

### Launch the Application
```bash
# From the OnePyFlow_ultra directory
python launch_params_generator.py
```

### Or run directly
```bash
python -m params_generator.main_window
```

## Key Improvements

### 1. Adaptive Sizing
- Automatically detects screen resolution
- Scales UI elements proportionally
- Maintains readability on all screen sizes

### 2. Dark Matrix Theme
- Deep black backgrounds
- Matrix green accents (#00ff41)
- High contrast for better visibility
- Professional appearance

### 3. Modular Architecture
- Separated concerns for easier maintenance
- Reusable components
- Clean import structure

### 4. Enhanced UX
- Smooth hover effects
- Clear visual hierarchy
- Intuitive navigation
- Responsive feedback

## Color Palette
- **Primary Background**: #0a0a0a (Deep Black)
- **Secondary Background**: #1a1a1a (Dark Gray)
- **Accent Color**: #00ff41 (Matrix Green)
- **Text Primary**: #ffffff (White)
- **Text Secondary**: #cccccc (Light Gray)
- **PPR_Q Highlight**: #ffd700 (Gold)

## Dependencies
- PyQt5
- Standard Python libraries (json, datetime, os, sys)

## Future Enhancements
- [ ] Custom themes support
- [ ] Keyboard shortcuts
- [ ] Configuration presets
- [ ] Export/import settings
- [ ] Advanced module filtering 