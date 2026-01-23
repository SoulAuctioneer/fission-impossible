"""
Screen flicker effect - simulates CRT display artifacts.
"""
import random
from typing import TYPE_CHECKING

from src.terminal.colors import Color

if TYPE_CHECKING:
    from src.terminal.text_buffer import TextBuffer


class ScreenFlicker:
    """Simulates CRT screen flicker by randomly dimming characters."""
    
    def __init__(self, intensity: float = 0.02):
        self.intensity = intensity
        self.active = True
    
    def apply(self, buffer: "TextBuffer"):
        """Apply random flicker to some characters."""
        if not self.active:
            return
        
        num_flickers = int(buffer.width * buffer.height * self.intensity)
        
        for _ in range(num_flickers):
            x = random.randint(0, buffer.width - 1)
            y = random.randint(0, buffer.height - 1)
            
            # Temporarily dim the character
            current_fg = buffer.fg_colors[y, x]
            if current_fg >= 8:  # Bright color
                buffer.fg_colors[y, x] = current_fg - 8  # Make dim


class StaticNoise:
    """Adds random static characters for glitch effect."""
    
    STATIC_CHARS = '░▒▓█▀▄▌▐■□●○'
    
    def __init__(self, intensity: float = 0.1):
        self.intensity = intensity
        self.active = False
        self.remaining = 0.0
    
    def trigger(self, duration: float = 0.1):
        """Trigger a burst of static."""
        self.active = True
        self.remaining = duration
    
    def update(self, dt: float):
        """Update static timer."""
        if self.active:
            self.remaining -= dt
            if self.remaining <= 0:
                self.active = False
    
    def apply(self, buffer: "TextBuffer"):
        """Apply static noise to buffer."""
        if not self.active:
            return
        
        num_static = int(buffer.width * buffer.height * self.intensity)
        
        for _ in range(num_static):
            x = random.randint(0, buffer.width - 1)
            y = random.randint(0, buffer.height - 1)
            char = random.choice(self.STATIC_CHARS)
            color = random.choice([Color.DARK_GRAY, Color.LIGHT_GRAY, Color.WHITE])
            buffer.put_char(x, y, char, color)


class ScanLines:
    """Subtle scan line effect for CRT feel."""
    
    def __init__(self, active: bool = False):
        self.active = active
        self.offset = 0
    
    def update(self, dt: float):
        """Update scan line animation."""
        # Slow scroll effect
        self.offset = (self.offset + 1) % 4
    
    def apply(self, buffer: "TextBuffer"):
        """Apply scan line effect."""
        if not self.active:
            return
        
        # Dim every 4th row
        for y in range(buffer.height):
            if (y + self.offset) % 4 == 0:
                for x in range(buffer.width):
                    current_fg = buffer.fg_colors[y, x]
                    if current_fg >= 8:
                        buffer.fg_colors[y, x] = current_fg - 8
