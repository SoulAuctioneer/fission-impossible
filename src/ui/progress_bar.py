"""
ASCII progress bar and gauge components.
"""
from typing import TYPE_CHECKING

from src.terminal.colors import Color

if TYPE_CHECKING:
    from src.terminal.text_buffer import TextBuffer


class ASCIIProgressBar:
    """A progress bar using block characters."""
    
    # Block characters for smooth gradients
    BLOCKS = ' ░▒▓█'  # 0%, 25%, 50%, 75%, 100%
    
    def __init__(self, x: int, y: int, width: int, 
                 fg: int = Color.LIGHT_GREEN, 
                 bg: int = Color.DARK_GRAY,
                 show_brackets: bool = False):
        self.x = x
        self.y = y
        self.width = width
        self.fg = fg
        self.bg = bg
        self.show_brackets = show_brackets
        self.value = 0.0  # 0.0 to 1.0
    
    def set_value(self, value: float):
        """Set progress value (0.0 to 1.0)."""
        self.value = max(0.0, min(1.0, value))
    
    def render(self, buffer: "TextBuffer"):
        """Render progress bar to buffer."""
        # Draw brackets if enabled
        start_x = self.x
        bar_width = self.width
        
        if self.show_brackets:
            buffer.put_char(start_x, self.y, '[', self.fg)
            buffer.put_char(start_x + self.width + 1, self.y, ']', self.fg)
            start_x += 1
        
        filled = self.value * bar_width
        
        for i in range(bar_width):
            if i < int(filled):
                # Fully filled - use high glow for lit portion
                char = '█'
                color = self.fg
                glow = 1
            elif i < filled:
                # Partially filled (use intermediate block) - also glow
                frac = filled - int(filled)
                block_idx = int(frac * 4) + 1
                char = self.BLOCKS[min(block_idx, 4)]
                color = self.fg
                glow = 1
            else:
                # Empty - no glow
                char = '░'
                color = self.bg
                glow = 0
            
            buffer.put_char(start_x + i, self.y, char, color, glow=glow)


class TemperatureGauge(ASCIIProgressBar):
    """Temperature gauge that changes color based on value."""
    
    def __init__(self, x: int, y: int, width: int, 
                 bg: int = Color.DARK_GRAY,
                 show_brackets: bool = False):
        super().__init__(x, y, width, Color.LIGHT_GREEN, bg, show_brackets)
    
    def render(self, buffer: "TextBuffer"):
        """Render with dynamic color based on temperature."""
        # Determine color based on value
        if self.value >= 0.8:
            self.fg = Color.LIGHT_RED
        elif self.value >= 0.5:
            self.fg = Color.LIGHT_YELLOW
        else:
            self.fg = Color.LIGHT_GREEN
        
        super().render(buffer)


class StrikeIndicator:
    """Strike indicator showing filled/empty circles."""
    
    def __init__(self, x: int, y: int, max_strikes: int = 3,
                 lit_color: int = Color.LIGHT_RED,
                 unlit_color: int = Color.DARK_GRAY):
        self.x = x
        self.y = y
        self.max_strikes = max_strikes
        self.strikes = 0
        self.lit_color = lit_color
        self.unlit_color = unlit_color
    
    def set_strikes(self, count: int):
        """Set current strike count."""
        self.strikes = min(count, self.max_strikes)
    
    def add_strike(self):
        """Add one strike."""
        self.set_strikes(self.strikes + 1)
    
    def render(self, buffer: "TextBuffer"):
        """Render strike indicators."""
        for i in range(self.max_strikes):
            if i < self.strikes:
                # Lit indicator - use high glow
                buffer.put_string(self.x + i * 4, self.y, "[■]", self.lit_color, glow=1)
            else:
                # Unlit indicator - no glow
                buffer.put_string(self.x + i * 4, self.y, "[·]", self.unlit_color, glow=0)


class ModuleProgressIndicator:
    """Module progress indicator showing solved/unsolved modules as filled squares."""
    
    def __init__(self, x: int, y: int, total_modules: int = 6,
                 solved_color: int = Color.LIGHT_GREEN,
                 unsolved_color: int = Color.DARK_GRAY):
        self.x = x
        self.y = y
        self.total_modules = total_modules
        self.solved = 0
        self.solved_color = solved_color
        self.unsolved_color = unsolved_color
    
    def set_progress(self, solved: int, total: int):
        """Set current progress."""
        self.solved = solved
        self.total_modules = total
    
    def render(self, buffer: "TextBuffer"):
        """Render module progress indicators."""
        for i in range(self.total_modules):
            if i < self.solved:
                # Solved module - use high glow
                buffer.put_string(self.x + i * 4, self.y, "[■]", self.solved_color, glow=1)
            else:
                # Unsolved module - no glow
                buffer.put_string(self.x + i * 4, self.y, "[·]", self.unsolved_color, glow=0)
