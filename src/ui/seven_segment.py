"""
Seven-segment display for ASCII timer rendering.
"""
from typing import TYPE_CHECKING, List

from src.terminal.colors import Color

if TYPE_CHECKING:
    from src.terminal.text_buffer import TextBuffer


class SevenSegmentDisplay:
    """
    ASCII art seven-segment display for numbers.
    Each digit is 3 chars wide × 5 chars tall.
    """
    
    # 7-segment patterns (each digit as 5 rows of 3 chars)
    DIGITS = {
        '0': ['█▀█', '█ █', '█ █', '█ █', '█▄█'],
        '1': [' ▀█', '  █', '  █', '  █', '  █'],
        '2': ['▀▀█', '  █', '█▀▀', '█  ', '█▄▄'],
        '3': ['▀▀█', '  █', '▀▀█', '  █', '▄▄█'],
        '4': ['█ █', '█ █', '▀▀█', '  █', '  █'],
        '5': ['█▀▀', '█  ', '▀▀█', '  █', '▄▄█'],
        '6': ['█▀▀', '█  ', '█▀█', '█ █', '█▄█'],
        '7': ['▀▀█', '  █', '  █', '  █', '  █'],
        '8': ['█▀█', '█ █', '█▀█', '█ █', '█▄█'],
        '9': ['█▀█', '█ █', '▀▀█', '  █', '▄▄█'],
        ':': [' ', '●', ' ', '●', ' '],
        ' ': ['   ', '   ', '   ', '   ', '   '],
    }
    
    def __init__(self, x: int, y: int, fg: int = Color.LIGHT_GREEN):
        self.x = x
        self.y = y
        self.fg = fg
        self.text = "00:00"
    
    def set_time(self, seconds: float):
        """Set display from seconds remaining."""
        mins = int(seconds) // 60
        secs = int(seconds) % 60
        self.text = f"{mins:02d}:{secs:02d}"
    
    def set_text(self, text: str):
        """Set arbitrary text."""
        self.text = text
    
    def get_width(self) -> int:
        """Get total width of the display in characters."""
        width = 0
        for char in self.text:
            if char in self.DIGITS:
                pattern = self.DIGITS[char]
                width += len(pattern[0]) + 1  # +1 for spacing
        return width - 1  # Remove trailing space
    
    def render(self, buffer: "TextBuffer"):
        """Render the display."""
        cursor_x = self.x
        
        for char in self.text:
            if char in self.DIGITS:
                pattern = self.DIGITS[char]
                for row_idx, row in enumerate(pattern):
                    buffer.put_string(cursor_x, self.y + row_idx, row, self.fg)
                cursor_x += len(pattern[0]) + 1  # +1 for spacing
            else:
                cursor_x += 2  # Unknown char, skip space


class SimpleTimerDisplay:
    """
    Simple single-line timer display.
    Format: MM:SS
    """
    
    def __init__(self, x: int, y: int, fg: int = Color.LIGHT_GREEN):
        self.x = x
        self.y = y
        self.fg = fg
        self.seconds = 0.0
    
    def set_time(self, seconds: float):
        """Set time in seconds."""
        self.seconds = max(0, seconds)
    
    def render(self, buffer: "TextBuffer"):
        """Render the timer."""
        mins = int(self.seconds) // 60
        secs = int(self.seconds) % 60
        time_str = f"{mins:02d}:{secs:02d}"
        buffer.put_string(self.x, self.y, time_str, self.fg)
