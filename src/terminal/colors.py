"""
ANSI color definitions for terminal rendering.
Standard 16-color CGA-style palette.
"""

# Standard 16-color ANSI palette (CGA-style)
ANSI_COLORS = {
    # Normal colors
    0:  (0, 0, 0),         # Black
    1:  (170, 0, 0),       # Red
    2:  (0, 170, 0),       # Green
    3:  (170, 85, 0),      # Yellow/Brown
    4:  (0, 0, 170),       # Blue
    5:  (170, 0, 170),     # Magenta
    6:  (0, 170, 170),     # Cyan
    7:  (170, 170, 170),   # Light Gray
    
    # Bright colors
    8:  (85, 85, 85),      # Dark Gray
    9:  (255, 85, 85),     # Light Red
    10: (85, 255, 85),     # Light Green
    11: (255, 255, 85),    # Light Yellow
    12: (85, 85, 255),     # Light Blue
    13: (255, 85, 255),    # Light Magenta
    14: (85, 255, 255),    # Light Cyan
    15: (255, 255, 255),   # White
}


class Color:
    """Semantic color constants."""
    BLACK = 0
    RED = 1
    GREEN = 2
    YELLOW = 3
    BLUE = 4
    MAGENTA = 5
    CYAN = 6
    LIGHT_GRAY = 7
    DARK_GRAY = 8
    LIGHT_RED = 9
    LIGHT_GREEN = 10
    LIGHT_YELLOW = 11
    LIGHT_BLUE = 12
    LIGHT_MAGENTA = 13
    LIGHT_CYAN = 14
    WHITE = 15
    
    # Semantic aliases for our theme
    TERMINAL = LIGHT_GREEN
    WARNING = LIGHT_YELLOW
    ERROR = LIGHT_RED
    HIGHLIGHT = LIGHT_CYAN
    DIM = DARK_GRAY
    PANEL_BORDER = GREEN
    TITLE = LIGHT_CYAN
