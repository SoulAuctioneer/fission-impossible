"""
TextBuffer - A 2D grid of character cells for terminal-style rendering.
"""
import numpy as np
from typing import Optional


class TextBuffer:
    """
    A 2D grid of character cells, similar to a terminal framebuffer.
    All rendering is done by writing to this buffer.
    """
    
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        
        # Use numpy for efficient storage
        # Each cell: [char_code, fg, bg, attributes, glow]
        self.chars = np.full((height, width), ord(' '), dtype=np.uint32)
        self.fg_colors = np.full((height, width), 10, dtype=np.uint8)  # Light green default
        self.bg_colors = np.zeros((height, width), dtype=np.uint8)  # Black default
        self.attributes = np.zeros((height, width), dtype=np.uint8)
        self.glow = np.zeros((height, width), dtype=np.uint8)  # 0=normal, 1+=high glow (for lit indicators)
        
        # Dirty tracking for efficient rendering
        self._dirty = True
        self._dirty_rows = set(range(height))
    
    def clear(self, char: str = ' ', fg: int = 10, bg: int = 0):
        """Clear the entire buffer."""
        self.chars.fill(ord(char))
        self.fg_colors.fill(fg)
        self.bg_colors.fill(bg)
        self.attributes.fill(0)
        self.glow.fill(0)
        self._dirty = True
        self._dirty_rows = set(range(self.height))
    
    def put_char(self, x: int, y: int, char: str, fg: Optional[int] = None, bg: Optional[int] = None, glow: int = 0):
        """Place a single character at (x, y)."""
        if 0 <= x < self.width and 0 <= y < self.height:
            self.chars[y, x] = ord(char[0]) if char else ord(' ')
            if fg is not None:
                self.fg_colors[y, x] = fg
            if bg is not None:
                self.bg_colors[y, x] = bg
            self.glow[y, x] = glow
            self._dirty_rows.add(y)
            self._dirty = True
    
    def put_string(self, x: int, y: int, text: str, fg: Optional[int] = None, bg: Optional[int] = None, glow: int = 0):
        """Place a string starting at (x, y)."""
        for i, char in enumerate(text):
            if x + i >= self.width:
                break
            self.put_char(x + i, y, char, fg, bg, glow)
    
    def put_string_centered(self, y: int, text: str, fg: Optional[int] = None, bg: Optional[int] = None, glow: int = 0):
        """Place a string centered on row y."""
        x = (self.width - len(text)) // 2
        self.put_string(x, y, text, fg, bg, glow)
    
    def fill_rect(self, x: int, y: int, w: int, h: int, 
                  char: str = ' ', fg: Optional[int] = None, bg: Optional[int] = None):
        """Fill a rectangular region."""
        for row in range(y, min(y + h, self.height)):
            for col in range(x, min(x + w, self.width)):
                self.put_char(col, row, char, fg, bg)
    
    def get_cell(self, x: int, y: int) -> tuple[str, int, int, int]:
        """Get character, colors, and glow at (x, y)."""
        if 0 <= x < self.width and 0 <= y < self.height:
            return (chr(self.chars[y, x]), 
                    int(self.fg_colors[y, x]), 
                    int(self.bg_colors[y, x]),
                    int(self.glow[y, x]))
        return (' ', 10, 0, 0)
    
    def is_dirty(self) -> bool:
        """Check if buffer needs redrawing."""
        return self._dirty
    
    def mark_clean(self):
        """Mark buffer as clean after rendering."""
        self._dirty = False
        self._dirty_rows.clear()
    
    def get_dirty_rows(self) -> set[int]:
        """Get set of rows that need redrawing."""
        return self._dirty_rows.copy()
