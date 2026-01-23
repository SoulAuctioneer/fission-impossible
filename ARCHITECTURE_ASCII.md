# Fission Impossible — Technical Architecture (ASCII/ANSI)

## Overview

This document describes an alternative architecture using **Pygame-CE** with **ASCII/ANSI text-based graphics**, authentically emulating 1980s terminal and mainframe computer displays. No bitmap graphics — every visual element is rendered using characters from a monospace font.

This approach creates an extremely authentic retro aesthetic that perfectly fits the NuHaus Nuclear maintenance terminal fiction.

---

## The Aesthetic

### Authentic 1980s Terminal Experience

```
╔═════════════════════════════════════════════════════════════════════════════╗
║  ████  NUHAUS NUCLEAR — MAINTENANCE TERMINAL v2.4.1  ████                   ║
╠═════════════════════════════════════════════════════════════════════════════╣
║                                                                             ║
║   ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────────────┐ ║
║   │ COOLANT BYPASS  │  │ EMERGENCY OVRD  │  │ ╔═══════════════════════╗   │ ║
║   │                 │  │                 │  │ ║   REACTOR STATUS      ║   │ ║
║   │  ═══════[R]═══  │  │    ╔═══════╗    │  │ ║                       ║   │ ║
║   │  ═══════[B]═══  │  │    ║ HOLD  ║    │  │ ║   TIME: 04:32         ║   │ ║
║   │  ══╳════[Y]═══  │  │    ║       ║    │  │ ║                       ║   │ ║
║   │  ═══════[W]═══  │  │    ╚═══════╝    │  │ ║   ERRORS: [●][○][○]   ║   │ ║
║   │                 │  │                 │  │ ║                       ║   │ ║
║   │  STATUS: [●]    │  │  STRIP: [░░░░]  │  │ ║   TEMP: ▓▓▓▓▓░░░░░    ║   │ ║
║   └─────────────────┘  └─────────────────┘  │ ║                       ║   │ ║
║   ┌─────────────────┐  ┌─────────────────┐  │ ╚═══════════════════════╝   │ ║
║   │  VENT CODES     │  │ ROD ALIGNMENT   │  │                             │ ║
║   │                 │  │                 │  │  SERIAL: AB3CD5             │ ║
║   │   [☢] [△] [◊]   │  │    [R]          │  │  BATTERIES: 2               │ ║
║   │   [✱]           │  │ [G]   [B]       │  │  PARALLEL PORT: YES         │ ║
║   │                 │  │    [Y]          │  │                             │ ║
║   │  STATUS: [○]    │  │  STATUS: [○]    │  │  ──────────────────────     │ ║
║   └─────────────────┘  └─────────────────┘  │  Gary would have solved     │ ║
║                                             │  this by now.               │ ║
║                                             └─────────────────────────────┘ ║
╚═════════════════════════════════════════════════════════════════════════════╝
```

### Character Palette

```
BOX DRAWING (Single)         BOX DRAWING (Double)
─ │ ┌ ┐ └ ┘ ├ ┤ ┬ ┴ ┼       ═ ║ ╔ ╗ ╚ ╝ ╠ ╣ ╦ ╩ ╬

BLOCKS & SHADING             SYMBOLS
█ ▓ ▒ ░ ▀ ▄ ▌ ▐             ● ○ ◉ ◎ ■ □ ▪ ▫ 
                             ★ ☆ ✱ ✦ ◆ ◇ ◊ 
ARROWS                       ☢ ⚠ ⚡ ☠ ⚙ ⌂
▲ ▼ ◀ ▶ △ ▽ ◁ ▷ ← → ↑ ↓     

MISC
╳ ╱ ╲ ∙ · • ¤ ♦ ♠ ♣ ♥
```

### Color Palette (16 ANSI Colors)

```
STANDARD                     BRIGHT
════════                     ══════
0: Black      #000000        8:  Dark Gray    #555555
1: Red        #AA0000        9:  Light Red    #FF5555
2: Green      #00AA00        10: Light Green  #55FF55
3: Yellow     #AA5500        11: Light Yellow #FFFF55
4: Blue       #0000AA        12: Light Blue   #5555FF
5: Magenta    #AA00AA        13: Light Magenta #FF55FF
6: Cyan       #00AAAA        14: Light Cyan   #55FFFF
7: Light Gray #AAAAAA        15: White        #FFFFFF

PRIMARY UI COLORS:
• Background: Black (0)
• Text: Light Green (10) — classic terminal
• Warnings: Light Yellow (11)
• Errors: Light Red (9)
• Highlights: Light Cyan (14)
• Dim text: Dark Gray (8)
```

---

## Why ASCII/ANSI?

### Advantages

| Advantage | Details |
|-----------|---------|
| **Authentic aesthetic** | Perfectly matches 1980s mainframe/terminal fiction |
| **Zero art assets needed** | Everything is generated from text |
| **Tiny file size** | Just code and a font file (~100KB total) |
| **Instant "art"** | Layout changes are just text editing |
| **Perfect scaling** | Integer character scaling, always crisp |
| **Fast development** | Design in a text editor, see in game |
| **Consistent style** | Impossible to have mismatched art |
| **Accessibility** | Can potentially support screen readers |

### Disadvantages

| Disadvantage | Mitigation |
|--------------|------------|
| Limited visual variety | Embrace the constraint as style |
| No smooth graphics | Use block characters for gradients |
| Resolution constraints | Design around character grid |
| Learning curve for ASCII art | Plenty of existing examples |

---

## Technology Stack

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           TECHNOLOGY STACK                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   CORE                        RENDERING                    TOOLS            │
│   ════                        ═════════                    ═════            │
│                                                                             │
│   Python 3.11+                Character Grid               PyInstaller      │
│   pygame-ce 2.x               └── 80×45 or 120×67          └── Distribution │
│   pyserial                        characters                                │
│                                                                             │
│                               Monospace Font                                │
│                               └── IBM VGA / DOS font                        │
│                                   or modern equivalent                      │
│                                   (e.g., Px437, Terminus)                   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Font Selection

The font choice is critical. Recommended options:

| Font | Style | Source |
|------|-------|--------|
| **PxPlus IBM VGA8** | Authentic DOS/VGA | int10h.org |
| **Terminus** | Clean, modern bitmap | terminus-font.sf.net |
| **Px437 IBM BIOS** | Ultra-retro | int10h.org |
| **Fixedsys Excelsior** | Windows 3.1 style | fixedsysexcelsior.com |
| **Perfect DOS VGA 437** | Perfect DOS replica | dafont.com |

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           FISSION IMPOSSIBLE                                │
│                         (ASCII/ANSI Edition)                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │                       CHARACTER GRID SYSTEM                           │ │
│  │                                                                       │ │
│  │   ┌─────────────────────────────────────────────────────────────┐    │ │
│  │   │                    TextBuffer (120×67)                       │    │ │
│  │   │                                                              │    │ │
│  │   │  Each cell contains:                                         │    │ │
│  │   │  • character (Unicode codepoint)                             │    │ │
│  │   │  • foreground color (0-15)                                   │    │ │
│  │   │  • background color (0-15)                                   │    │ │
│  │   │  • attributes (blink, bold, etc.)                           │    │ │
│  │   │                                                              │    │ │
│  │   └─────────────────────────────────────────────────────────────┘    │ │
│  │                              │                                        │ │
│  │                              ▼                                        │ │
│  │   ┌─────────────────────────────────────────────────────────────┐    │ │
│  │   │                    FontRenderer                              │    │ │
│  │   │                                                              │    │ │
│  │   │  • Pre-renders all glyphs to surfaces                       │    │ │
│  │   │  • Caches colored variants                                   │    │ │
│  │   │  • Blits grid to screen each frame                          │    │ │
│  │   │                                                              │    │ │
│  │   └─────────────────────────────────────────────────────────────┘    │ │
│  │                              │                                        │ │
│  │                              ▼                                        │ │
│  │   ┌─────────────────────────────────────────────────────────────┐    │ │
│  │   │                    pygame.Surface                            │    │ │
│  │   │                    (1920×1072 @ 16×16 chars)                │    │ │
│  │   └─────────────────────────────────────────────────────────────┘    │ │
│  │                                                                       │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │                         UI COMPONENTS                                 │ │
│  │                                                                       │ │
│  │  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐        │ │
│  │  │   Panel    │ │   Window   │ │   Button   │ │  TextArea  │        │ │
│  │  │            │ │            │ │            │ │            │        │ │
│  │  │ Box-draw   │ │ Title bar  │ │ Clickable  │ │ Scrolling  │        │ │
│  │  │ borders    │ │ + borders  │ │ highlight  │ │ text       │        │ │
│  │  └────────────┘ └────────────┘ └────────────┘ └────────────┘        │ │
│  │                                                                       │ │
│  │  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐        │ │
│  │  │ ProgressBar│ │ ASCIIArt   │ │  Gauge     │ │ 7-Segment  │        │ │
│  │  │            │ │            │ │            │ │            │        │ │
│  │  │ ▓▓▓▓░░░░░  │ │ Multi-line │ │ ████░░░░  │ │ Digital    │        │ │
│  │  │ blocks     │ │ art        │ │ vertical   │ │ numbers    │        │ │
│  │  └────────────┘ └────────────┘ └────────────┘ └────────────┘        │ │
│  │                                                                       │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │                        MODULES (ASCII)                                │ │
│  │                                                                       │ │
│  │  Each module renders to a rectangular region of the TextBuffer       │ │
│  │  using box-drawing characters, symbols, and block graphics           │ │
│  │                                                                       │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Project Structure

```
fission-impossible/
├── main.py                      # Entry point
├── requirements.txt             # Python dependencies
│
├── src/
│   ├── __init__.py
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── game.py              # Main game class
│   │   ├── settings.py          # Configuration
│   │   └── state_machine.py     # Scene management
│   │
│   ├── terminal/                # THE KEY DIFFERENCE
│   │   ├── __init__.py
│   │   ├── text_buffer.py       # Character grid data structure
│   │   ├── font_renderer.py     # Renders buffer to pygame surface
│   │   ├── colors.py            # ANSI color definitions
│   │   └── box_drawing.py       # Box-drawing character helpers
│   │
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── component.py         # Base UI component
│   │   ├── panel.py             # Bordered panel
│   │   ├── window.py            # Window with title
│   │   ├── button.py            # Clickable button
│   │   ├── progress_bar.py      # Block-based progress
│   │   ├── gauge.py             # Vertical/horizontal gauge
│   │   └── seven_segment.py     # ASCII 7-segment display
│   │
│   ├── states/
│   │   ├── __init__.py
│   │   ├── base_state.py
│   │   ├── start_screen.py
│   │   ├── game_screen.py
│   │   └── end_screen.py
│   │
│   ├── modules/
│   │   ├── __init__.py
│   │   ├── base_module.py       # Base module (renders to TextBuffer region)
│   │   ├── coolant_valves.py
│   │   ├── emergency_override.py
│   │   ├── vent_codes.py
│   │   ├── rod_alignment.py
│   │   ├── pressure_locks.py
│   │   └── security_terminal.py
│   │
│   ├── audio/
│   │   ├── __init__.py
│   │   └── audio_manager.py
│   │
│   ├── usb/
│   │   ├── __init__.py
│   │   ├── serial_manager.py
│   │   └── protocol.py
│   │
│   └── utils/
│       ├── __init__.py
│       ├── edgework.py
│       └── ascii_art.py         # Pre-defined ASCII art pieces
│
├── assets/
│   ├── fonts/
│   │   └── PxPlus_IBM_VGA8.ttf  # DOS-style font
│   └── audio/
│       ├── sfx/
│       └── music/
│
└── docs/
    └── *.md
```

---

## Core Terminal System

### Text Buffer

```python
# src/terminal/text_buffer.py
from dataclasses import dataclass
from typing import Optional
import numpy as np

@dataclass
class Cell:
    """A single character cell."""
    char: str = ' '
    fg: int = 10      # Light green (default terminal color)
    bg: int = 0       # Black
    bold: bool = False
    blink: bool = False

class TextBuffer:
    """
    A 2D grid of character cells, similar to a terminal framebuffer.
    All rendering is done by writing to this buffer.
    """
    
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        
        # Use numpy for efficient storage
        # Each cell: [char_code, fg, bg, attributes]
        self.chars = np.full((height, width), ord(' '), dtype=np.uint32)
        self.fg_colors = np.full((height, width), 10, dtype=np.uint8)
        self.bg_colors = np.zeros((height, width), dtype=np.uint8)
        self.attributes = np.zeros((height, width), dtype=np.uint8)
        
        # Dirty tracking for efficient rendering
        self._dirty = True
        self._dirty_rows = set(range(height))
    
    def clear(self, char: str = ' ', fg: int = 10, bg: int = 0):
        """Clear the entire buffer."""
        self.chars.fill(ord(char))
        self.fg_colors.fill(fg)
        self.bg_colors.fill(bg)
        self.attributes.fill(0)
        self._dirty = True
        self._dirty_rows = set(range(self.height))
    
    def put_char(self, x: int, y: int, char: str, fg: int = None, bg: int = None):
        """Place a single character at (x, y)."""
        if 0 <= x < self.width and 0 <= y < self.height:
            self.chars[y, x] = ord(char[0]) if char else ord(' ')
            if fg is not None:
                self.fg_colors[y, x] = fg
            if bg is not None:
                self.bg_colors[y, x] = bg
            self._dirty_rows.add(y)
            self._dirty = True
    
    def put_string(self, x: int, y: int, text: str, fg: int = None, bg: int = None):
        """Place a string starting at (x, y)."""
        for i, char in enumerate(text):
            self.put_char(x + i, y, char, fg, bg)
    
    def put_string_centered(self, y: int, text: str, fg: int = None, bg: int = None):
        """Place a string centered on row y."""
        x = (self.width - len(text)) // 2
        self.put_string(x, y, text, fg, bg)
    
    def fill_rect(self, x: int, y: int, w: int, h: int, 
                  char: str = ' ', fg: int = None, bg: int = None):
        """Fill a rectangular region."""
        for row in range(y, min(y + h, self.height)):
            for col in range(x, min(x + w, self.width)):
                self.put_char(col, row, char, fg, bg)
    
    def get_cell(self, x: int, y: int) -> tuple[str, int, int]:
        """Get character and colors at (x, y)."""
        if 0 <= x < self.width and 0 <= y < self.height:
            return (chr(self.chars[y, x]), 
                    self.fg_colors[y, x], 
                    self.bg_colors[y, x])
        return (' ', 10, 0)
    
    def is_dirty(self) -> bool:
        return self._dirty
    
    def mark_clean(self):
        self._dirty = False
        self._dirty_rows.clear()
```

### Box Drawing Helpers

```python
# src/terminal/box_drawing.py
from dataclasses import dataclass

@dataclass
class BoxStyle:
    """Box drawing character set."""
    h: str      # Horizontal
    v: str      # Vertical
    tl: str     # Top-left
    tr: str     # Top-right
    bl: str     # Bottom-left
    br: str     # Bottom-right
    t_down: str # T pointing down
    t_up: str   # T pointing up
    t_right: str# T pointing right
    t_left: str # T pointing left
    cross: str  # Cross/plus

# Predefined styles
SINGLE = BoxStyle('─', '│', '┌', '┐', '└', '┘', '┬', '┴', '├', '┤', '┼')
DOUBLE = BoxStyle('═', '║', '╔', '╗', '╚', '╝', '╦', '╩', '╠', '╣', '╬')
HEAVY  = BoxStyle('━', '┃', '┏', '┓', '┗', '┛', '┳', '┻', '┣', '┫', '╋')
ROUND  = BoxStyle('─', '│', '╭', '╮', '╰', '╯', '┬', '┴', '├', '┤', '┼')

def draw_box(buffer, x: int, y: int, w: int, h: int, 
             style: BoxStyle = SINGLE, fg: int = 10, bg: int = None):
    """Draw a box using box-drawing characters."""
    # Corners
    buffer.put_char(x, y, style.tl, fg, bg)
    buffer.put_char(x + w - 1, y, style.tr, fg, bg)
    buffer.put_char(x, y + h - 1, style.bl, fg, bg)
    buffer.put_char(x + w - 1, y + h - 1, style.br, fg, bg)
    
    # Top and bottom edges
    for i in range(1, w - 1):
        buffer.put_char(x + i, y, style.h, fg, bg)
        buffer.put_char(x + i, y + h - 1, style.h, fg, bg)
    
    # Left and right edges
    for i in range(1, h - 1):
        buffer.put_char(x, y + i, style.v, fg, bg)
        buffer.put_char(x + w - 1, y + i, style.v, fg, bg)

def draw_titled_box(buffer, x: int, y: int, w: int, h: int,
                    title: str, style: BoxStyle = DOUBLE, 
                    fg: int = 10, title_fg: int = 14):
    """Draw a box with a title in the top border."""
    draw_box(buffer, x, y, w, h, style, fg)
    
    # Title (centered in top border)
    title_text = f" {title} "
    title_x = x + (w - len(title_text)) // 2
    buffer.put_string(title_x, y, title_text, title_fg)
```

### Font Renderer

```python
# src/terminal/font_renderer.py
import pygame
from pathlib import Path
from src.terminal.colors import ANSI_COLORS

class FontRenderer:
    """
    Renders a TextBuffer to a pygame Surface using a bitmap font.
    """
    
    def __init__(self, font_path: Path, char_width: int = 16, char_height: int = 16):
        self.char_width = char_width
        self.char_height = char_height
        
        # Load font (sized to match character dimensions)
        self.font = pygame.font.Font(str(font_path), char_height)
        
        # Pre-render glyph cache: {(char, fg_color): Surface}
        self._glyph_cache: dict[tuple[int, int], pygame.Surface] = {}
        
        # Pre-render common characters
        self._prerender_common_glyphs()
    
    def _prerender_common_glyphs(self):
        """Pre-render frequently used characters in all colors."""
        common_chars = (
            " !\"#$%&'()*+,-./0123456789:;<=>?@"
            "ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`"
            "abcdefghijklmnopqrstuvwxyz{|}~"
            "─│┌┐└┘├┤┬┴┼═║╔╗╚╝╠╣╦╩╬"
            "░▒▓█▀▄▌▐■□●○◆◇★☆▲▼◀▶"
            "☢⚠✱"
        )
        
        for char in common_chars:
            for color_idx in range(16):
                self._get_glyph(ord(char), color_idx)
    
    def _get_glyph(self, char_code: int, fg_color: int) -> pygame.Surface:
        """Get or create a rendered glyph."""
        key = (char_code, fg_color)
        
        if key not in self._glyph_cache:
            char = chr(char_code)
            color = ANSI_COLORS[fg_color]
            
            # Render with antialiasing off for crisp pixels
            glyph = self.font.render(char, False, color)
            
            # Ensure consistent size
            if glyph.get_size() != (self.char_width, self.char_height):
                sized = pygame.Surface((self.char_width, self.char_height), pygame.SRCALPHA)
                sized.blit(glyph, (0, 0))
                glyph = sized
            
            self._glyph_cache[key] = glyph
        
        return self._glyph_cache[key]
    
    def render(self, buffer, target: pygame.Surface):
        """Render the entire TextBuffer to target surface."""
        for y in range(buffer.height):
            for x in range(buffer.width):
                char_code = buffer.chars[y, x]
                fg = buffer.fg_colors[y, x]
                bg = buffer.bg_colors[y, x]
                
                px = x * self.char_width
                py = y * self.char_height
                
                # Draw background
                if bg != 0:  # 0 = black, skip for performance
                    bg_rect = pygame.Rect(px, py, self.char_width, self.char_height)
                    pygame.draw.rect(target, ANSI_COLORS[bg], bg_rect)
                
                # Draw character
                if char_code != ord(' '):  # Skip spaces for performance
                    glyph = self._get_glyph(char_code, fg)
                    target.blit(glyph, (px, py))
    
    def render_dirty(self, buffer, target: pygame.Surface):
        """Render only dirty rows (optimization)."""
        for y in buffer._dirty_rows:
            for x in range(buffer.width):
                char_code = buffer.chars[y, x]
                fg = buffer.fg_colors[y, x]
                bg = buffer.bg_colors[y, x]
                
                px = x * self.char_width
                py = y * self.char_height
                
                # Clear cell
                cell_rect = pygame.Rect(px, py, self.char_width, self.char_height)
                pygame.draw.rect(target, ANSI_COLORS[0], cell_rect)  # Black
                
                # Draw background
                if bg != 0:
                    pygame.draw.rect(target, ANSI_COLORS[bg], cell_rect)
                
                # Draw character
                if char_code != ord(' '):
                    glyph = self._get_glyph(char_code, fg)
                    target.blit(glyph, (px, py))
```

### Color Definitions

```python
# src/terminal/colors.py

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

# Semantic color names
class Color:
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
```

---

## Settings

```python
# src/core/settings.py
from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class Settings:
    # Terminal dimensions (in characters)
    COLS: int = 120           # Characters wide
    ROWS: int = 45            # Characters tall
    
    # Character cell size (in pixels)
    CHAR_WIDTH: int = 16
    CHAR_HEIGHT: int = 16
    
    # Calculated window size
    @property
    def WINDOW_WIDTH(self) -> int:
        return self.COLS * self.CHAR_WIDTH    # 1920
    
    @property
    def WINDOW_HEIGHT(self) -> int:
        return self.ROWS * self.CHAR_HEIGHT   # 720
    
    # Game settings
    FPS: int = 60
    TITLE: str = "Fission Impossible — NuHaus Nuclear Terminal"
    
    STARTING_TIME: float = 300.0
    MAX_STRIKES: int = 3
    
    # Paths
    ASSETS_DIR: Path = Path("assets")
    FONT_PATH: Path = ASSETS_DIR / "fonts" / "PxPlus_IBM_VGA8.ttf"
    AUDIO_DIR: Path = ASSETS_DIR / "audio"
    
    # USB
    USB_ENABLED: bool = False
    USB_BAUD_RATE: int = 115200

SETTINGS = Settings()
```

---

## UI Components

### ASCII Button

```python
# src/ui/button.py
from src.terminal.text_buffer import TextBuffer
from src.terminal.box_drawing import draw_box, SINGLE, DOUBLE
from src.terminal.colors import Color

class ASCIIButton:
    """A clickable button rendered in ASCII."""
    
    def __init__(self, x: int, y: int, text: str, width: int = None):
        self.x = x
        self.y = y
        self.text = text
        self.width = width or len(text) + 4
        self.height = 3
        
        self.hovered = False
        self.pressed = False
        self.enabled = True
    
    def contains_char(self, cx: int, cy: int) -> bool:
        """Check if character position is inside button."""
        return (self.x <= cx < self.x + self.width and
                self.y <= cy < self.y + self.height)
    
    def render(self, buffer: TextBuffer):
        """Render button to buffer."""
        if not self.enabled:
            fg = Color.DARK_GRAY
            border = SINGLE
        elif self.pressed:
            fg = Color.BLACK
            bg = Color.LIGHT_GREEN
            border = DOUBLE
        elif self.hovered:
            fg = Color.LIGHT_CYAN
            border = DOUBLE
        else:
            fg = Color.LIGHT_GREEN
            border = SINGLE
        
        # Draw border
        draw_box(buffer, self.x, self.y, self.width, self.height, border, fg)
        
        # Draw text (centered)
        text_x = self.x + (self.width - len(self.text)) // 2
        text_y = self.y + 1
        
        if self.pressed:
            buffer.put_string(text_x, text_y, self.text, Color.BLACK, Color.LIGHT_GREEN)
        else:
            buffer.put_string(text_x, text_y, self.text, fg)
```

### ASCII Progress Bar

```python
# src/ui/progress_bar.py
from src.terminal.text_buffer import TextBuffer
from src.terminal.colors import Color

class ASCIIProgressBar:
    """A progress bar using block characters."""
    
    # Block characters for smooth gradients
    BLOCKS = ' ░▒▓█'  # 0%, 25%, 50%, 75%, 100%
    
    def __init__(self, x: int, y: int, width: int, 
                 fg: int = Color.LIGHT_GREEN, 
                 bg: int = Color.DARK_GRAY):
        self.x = x
        self.y = y
        self.width = width
        self.fg = fg
        self.bg = bg
        self.value = 0.0  # 0.0 to 1.0
    
    def set_value(self, value: float):
        """Set progress value (0.0 to 1.0)."""
        self.value = max(0.0, min(1.0, value))
    
    def render(self, buffer: TextBuffer):
        """Render progress bar to buffer."""
        filled = self.value * self.width
        
        for i in range(self.width):
            if i < int(filled):
                # Fully filled
                char = '█'
                color = self.fg
            elif i < filled:
                # Partially filled (use intermediate block)
                frac = filled - int(filled)
                block_idx = int(frac * 4) + 1
                char = self.BLOCKS[min(block_idx, 4)]
                color = self.fg
            else:
                # Empty
                char = '░'
                color = self.bg
            
            buffer.put_char(self.x + i, self.y, char, color)
```

### Seven-Segment Display

```python
# src/ui/seven_segment.py
from src.terminal.text_buffer import TextBuffer
from src.terminal.colors import Color

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
        ':': [' ', '●', ' ', '●', ' '],  # Colon for time display
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
    
    def render(self, buffer: TextBuffer):
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
```

---

## Module Rendering (ASCII Style)

### Coolant Valves Module

```python
# src/modules/coolant_valves.py
from src.modules.base_module import ASCIIModule
from src.terminal.text_buffer import TextBuffer
from src.terminal.box_drawing import draw_titled_box, DOUBLE
from src.terminal.colors import Color

class CoolantValvesModule(ASCIIModule):
    """Coolant Valves module rendered in ASCII."""
    
    WIRE_CHARS = {
        'intact': '═══════',
        'cut':    '═══╳═══',
    }
    
    COLOR_DISPLAY = {
        'red':    ('R', Color.LIGHT_RED),
        'blue':   ('B', Color.LIGHT_BLUE),
        'yellow': ('Y', Color.LIGHT_YELLOW),
        'white':  ('W', Color.WHITE),
        'black':  ('K', Color.DARK_GRAY),
    }
    
    def _initialize(self):
        self.name = "COOLANT BYPASS"
        self.wire_count = 0
        self.wire_colors = []
        self.correct_wire = 0
        self.cut_wires = set()
    
    def _render_module(self, buffer: TextBuffer, x: int, y: int, w: int, h: int):
        """Render module content."""
        # Title box
        draw_titled_box(buffer, x, y, w, h, self.name, DOUBLE, Color.GREEN, Color.LIGHT_CYAN)
        
        # Render wires
        wire_start_y = y + 2
        
        for i, color in enumerate(self.wire_colors):
            wire_y = wire_start_y + i * 2
            
            # Wire label
            label, label_color = self.COLOR_DISPLAY[color]
            buffer.put_char(x + 2, wire_y, '[', Color.DARK_GRAY)
            buffer.put_char(x + 3, wire_y, label, label_color)
            buffer.put_char(x + 4, wire_y, ']', Color.DARK_GRAY)
            
            # Wire itself
            if i in self.cut_wires:
                wire_text = self.WIRE_CHARS['cut']
            else:
                wire_text = self.WIRE_CHARS['intact']
            
            buffer.put_string(x + 6, wire_y, wire_text, label_color)
            
            # Wire number for clicking
            buffer.put_char(x + w - 3, wire_y, str(i + 1), Color.DARK_GRAY)
        
        # Status indicator
        status_y = y + h - 2
        buffer.put_string(x + 2, status_y, "STATUS:", Color.DARK_GRAY)
        
        if self.is_solved:
            buffer.put_string(x + 10, status_y, "[●]", Color.LIGHT_GREEN)
            buffer.put_string(x + 14, status_y, "NOMINAL", Color.LIGHT_GREEN)
        else:
            buffer.put_string(x + 10, status_y, "[○]", Color.DARK_GRAY)
```

---

## Complete Screen Layout

### Start Screen (ASCII)

```python
# src/states/start_screen.py
from src.terminal.text_buffer import TextBuffer
from src.terminal.box_drawing import draw_box, draw_titled_box, DOUBLE, SINGLE
from src.terminal.colors import Color
from src.ui.button import ASCIIButton

class StartScreen:
    """Clock-in terminal start screen."""
    
    HEADER_ART = [
        "████████╗███████╗██████╗ ███╗   ███╗██╗███╗   ██╗ █████╗ ██╗     ",
        "╚══██╔══╝██╔════╝██╔══██╗████╗ ████║██║████╗  ██║██╔══██╗██║     ",
        "   ██║   █████╗  ██████╔╝██╔████╔██║██║██╔██╗ ██║███████║██║     ",
        "   ██║   ██╔══╝  ██╔══██╗██║╚██╔╝██║██║██║╚██╗██║██╔══██║██║     ",
        "   ██║   ███████╗██║  ██║██║ ╚═╝ ██║██║██║ ╚████║██║  ██║███████╗",
        "   ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝╚══════╝",
    ]
    
    def __init__(self, game):
        self.game = game
        self.buffer = game.buffer
        
        # Create clock-in button
        self.clock_in_btn = ASCIIButton(
            x=50, y=35, 
            text="[ CLOCK IN ]", 
            width=20
        )
    
    def render(self):
        self.buffer.clear()
        
        # Header
        self.buffer.put_string(2, 1, 
            "████  NUHAUS NUCLEAR — MAINTENANCE TERMINAL v2.4.1  ████", 
            Color.LIGHT_GREEN)
        
        # Border
        draw_box(self.buffer, 0, 0, 120, 45, DOUBLE, Color.GREEN)
        
        # Shift briefing box
        draw_titled_box(self.buffer, 10, 8, 100, 20, 
                       "SHIFT BRIEFING", SINGLE, Color.GREEN, Color.LIGHT_CYAN)
        
        # Briefing content
        briefing = [
            "",
            "              ☢  ALERT: Reactor systems experiencing anomalies.  ☢",
            "",
            "         Maintenance Room 7-G requires immediate attention.",
            "",
            "         ─────────────────────────────────────────────────────",
            "",
            "         TECHNICIAN: Resolve all system faults before meltdown.",
            "         HOTLINE:    Consult the Operations Manual. Guide them through.",
            "",
            "         ⚠ DO NOT exceed 3 operational errors.",
            "         ⚠ DO NOT allow the reactor to reach critical temperature.",
            "",
            "         ─────────────────────────────────────────────────────",
            "",
            "         Manual: http://localhost:8080/manual",
        ]
        
        for i, line in enumerate(briefing):
            self.buffer.put_string(12, 10 + i, line, Color.LIGHT_GREEN)
        
        # Clock-in button
        self.clock_in_btn.render(self.buffer)
        
        # Footer
        self.buffer.put_string(2, 43, 
            'NUHAUS NUCLEAR — "We\'re Glad You\'re Expendable"', 
            Color.DARK_GRAY)
        self.buffer.put_string(90, 43, 
            "TERMINAL 7-G", 
            Color.DARK_GRAY)
```

### Game Screen Layout

```
╔══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
║  ████  NUHAUS NUCLEAR — MAINTENANCE ROOM 7-G  ████                                        TIME: 04:32   SHIFT: DAY  ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
║                                                                                                                      ║
║  ╔═══════════════════════════╗  ╔═══════════════════════════╗  ╔════════════════════════════════════════════════╗  ║
║  ║    COOLANT BYPASS         ║  ║    EMERGENCY OVERRIDE     ║  ║             REACTOR STATUS                     ║  ║
║  ║                           ║  ║                           ║  ║                                                ║  ║
║  ║  [R] ═══════════════════  ║  ║      ╔═════════════╗      ║  ║  ╔══════════════════════════════════════════╗  ║  ║
║  ║  [B] ═══════════════════  ║  ║      ║             ║      ║  ║  ║                                          ║  ║  ║
║  ║  [Y] ═══════╳═══════════  ║  ║      ║    HOLD     ║      ║  ║  ║    ██▀█▀██   ▀▀█▀█▀   ▀▀█▀█▀   █▀█▀██    ║  ║  ║
║  ║  [W] ═══════════════════  ║  ║      ║             ║      ║  ║  ║    ██ █ ██    ▀█ █     ▀█ █    █ █ ██    ║  ║  ║
║  ║                           ║  ║      ╚═════════════╝      ║  ║  ║    ██▄█▄██   ▄▄█▄█    ▄▄█▄█    █▄█▄██    ║  ║  ║
║  ║  STATUS: [●] NOMINAL      ║  ║                           ║  ║  ║                                          ║  ║  ║
║  ╚═══════════════════════════╝  ║  STRIP: [████████░░░░]    ║  ║  ╚══════════════════════════════════════════╝  ║  ║
║  ╔═══════════════════════════╗  ║                           ║  ║                                                ║  ║
║  ║    VENT CODES             ║  ║  STATUS: [○]              ║  ║  ERRORS:  [●] [○] [○]                          ║  ║
║  ║                           ║  ╚═══════════════════════════╝  ║                                                ║  ║
║  ║   ┌─────┐ ┌─────┐         ║  ╔═══════════════════════════╗  ║  TEMP: ▓▓▓▓▓▓▓▓▓▓░░░░░░░░░░                    ║  ║
║  ║   │ ☢  │ │ ⚠  │         ║  ║    ROD ALIGNMENT          ║  ║                                                ║  ║
║  ║   └─────┘ └─────┘         ║  ║                           ║  ║  ════════════════════════════════════════      ║  ║
║  ║   ┌─────┐ ┌─────┐         ║  ║         [R]               ║  ║                                                ║  ║
║  ║   │ ✱  │ │ ◊  │         ║  ║      [G]   [B]            ║  ║  SERIAL NUMBER: AB3CD5                         ║  ║
║  ║   └─────┘ └─────┘         ║  ║         [Y]               ║  ║  BATTERIES:     2                              ║  ║
║  ║                           ║  ║                           ║  ║  PARALLEL PORT: YES                            ║  ║
║  ║  STATUS: [○]              ║  ║  STATUS: [○]              ║  ║  INDICATORS:    CAR [●]  FRK [○]               ║  ║
║  ╚═══════════════════════════╝  ╚═══════════════════════════╝  ║                                                ║  ║
║  ╔═══════════════════════════╗  ╔═══════════════════════════╗  ║  ════════════════════════════════════════      ║  ║
║  ║    PRESSURE LOCKS         ║  ║    SECURITY TERMINAL      ║  ║                                                ║  ║
║  ║                           ║  ║                           ║  ║  > Gary would have solved this by now.         ║  ║
║  ║   ┌───┬───┬───┬───┬───┐   ║  ║  ┌───┬───┬───┬───┬───┐   ║  ║  > Remember: Safety is YOUR responsibility.    ║  ║
║  ║   │   │   │ ● │   │   │   ║  ║  │ ▲ │ ▲ │ ▲ │ ▲ │ ▲ │   ║  ║  > Tip: Refer to manual section 7.4.2          ║  ║
║  ║   ├───┼───┼───┼───┼───┤   ║  ║  ├───┼───┼───┼───┼───┤   ║  ║                                                ║  ║
║  ║   │   │   │   │   │   │   ║  ║  │ P │ L │ A │ N │ T │   ║  ║                                                ║  ║
║  ║   ├───┼───┼───┼───┼───┤   ║  ║  ├───┼───┼───┼───┼───┤   ║  ║                                                ║  ║
║  ║   │   │   │   │   │ ▲ │   ║  ║  │ ▼ │ ▼ │ ▼ │ ▼ │ ▼ │   ║  ║                                                ║  ║
║  ║   └───┴───┴───┴───┴───┘   ║  ║  └───┴───┴───┴───┴───┘   ║  ║                                                ║  ║
║  ║    [▲] [▼] [◀] [▶]        ║  ║                           ║  ║                                                ║  ║
║  ║                           ║  ║  ╔═══════════════════╗    ║  ║                                                ║  ║
║  ║  STATUS: [○]              ║  ║  ║     [SUBMIT]      ║    ║  ║                                                ║  ║
║  ╚═══════════════════════════╝  ║  ╚═══════════════════╝    ║  ╚════════════════════════════════════════════════╝  ║
║                                 ║  STATUS: [○]              ║                                                      ║
║                                 ╚═══════════════════════════╝                                                      ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
```

---

## Input Handling

Since we're using a character grid, mouse clicks need to be converted to character coordinates:

```python
# src/core/input.py
from src.core.settings import SETTINGS

def pixel_to_char(px: int, py: int) -> tuple[int, int]:
    """Convert pixel coordinates to character coordinates."""
    cx = px // SETTINGS.CHAR_WIDTH
    cy = py // SETTINGS.CHAR_HEIGHT
    return (cx, cy)

def char_to_pixel(cx: int, cy: int) -> tuple[int, int]:
    """Convert character coordinates to pixel coordinates (top-left of cell)."""
    px = cx * SETTINGS.CHAR_WIDTH
    py = cy * SETTINGS.CHAR_HEIGHT
    return (px, py)

class InputHandler:
    """Handles input and converts to character-grid coordinates."""
    
    def __init__(self):
        self.mouse_char_pos = (0, 0)
        self.mouse_pixel_pos = (0, 0)
    
    def update(self):
        """Update mouse position tracking."""
        self.mouse_pixel_pos = pygame.mouse.get_pos()
        self.mouse_char_pos = pixel_to_char(*self.mouse_pixel_pos)
    
    def get_char_pos(self) -> tuple[int, int]:
        """Get current mouse position in character coordinates."""
        return self.mouse_char_pos
```

---

## Effects (ASCII Style)

### Screen Flicker

```python
# src/effects/flicker.py
import random
from src.terminal.text_buffer import TextBuffer
from src.terminal.colors import Color

class ScreenFlicker:
    """Simulates CRT screen flicker by randomly dimming characters."""
    
    def __init__(self, intensity: float = 0.02):
        self.intensity = intensity
        self.active = True
    
    def apply(self, buffer: TextBuffer):
        """Apply random flicker to some characters."""
        if not self.active:
            return
        
        for _ in range(int(buffer.width * buffer.height * self.intensity)):
            x = random.randint(0, buffer.width - 1)
            y = random.randint(0, buffer.height - 1)
            
            # Temporarily dim the character
            current_fg = buffer.fg_colors[y, x]
            if current_fg >= 8:  # Bright color
                buffer.fg_colors[y, x] = current_fg - 8  # Make dim
```

### Typing Effect

```python
# src/effects/typing.py
from src.terminal.text_buffer import TextBuffer

class TypingEffect:
    """Reveals text character by character like typing."""
    
    def __init__(self, x: int, y: int, text: str, 
                 chars_per_second: float = 30, fg: int = 10):
        self.x = x
        self.y = y
        self.text = text
        self.fg = fg
        self.chars_per_second = chars_per_second
        
        self.elapsed = 0.0
        self.revealed = 0
        self.complete = False
    
    def update(self, dt: float):
        if self.complete:
            return
        
        self.elapsed += dt
        self.revealed = int(self.elapsed * self.chars_per_second)
        
        if self.revealed >= len(self.text):
            self.revealed = len(self.text)
            self.complete = True
    
    def render(self, buffer: TextBuffer):
        visible_text = self.text[:self.revealed]
        buffer.put_string(self.x, self.y, visible_text, self.fg)
        
        # Cursor blink
        if not self.complete and int(self.elapsed * 4) % 2 == 0:
            cursor_x = self.x + self.revealed
            buffer.put_char(cursor_x, self.y, '█', self.fg)
```

### Static/Noise

```python
# src/effects/static.py
import random
from src.terminal.text_buffer import TextBuffer
from src.terminal.colors import Color

class StaticNoise:
    """Adds random static characters for glitch effect."""
    
    STATIC_CHARS = '░▒▓█▀▄▌▐■□●○'
    
    def __init__(self, intensity: float = 0.01):
        self.intensity = intensity
        self.active = False
    
    def trigger(self, duration: float = 0.1):
        """Trigger a burst of static."""
        self.active = True
        self.remaining = duration
    
    def update(self, dt: float):
        if self.active:
            self.remaining -= dt
            if self.remaining <= 0:
                self.active = False
    
    def apply(self, buffer: TextBuffer):
        if not self.active:
            return
        
        num_static = int(buffer.width * buffer.height * self.intensity)
        
        for _ in range(num_static):
            x = random.randint(0, buffer.width - 1)
            y = random.randint(0, buffer.height - 1)
            char = random.choice(self.STATIC_CHARS)
            color = random.choice([Color.DARK_GRAY, Color.LIGHT_GRAY, Color.WHITE])
            buffer.put_char(x, y, char, color)
```

---

## Main Game Loop

```python
# src/core/game.py
import pygame
from src.core.settings import SETTINGS
from src.terminal.text_buffer import TextBuffer
from src.terminal.font_renderer import FontRenderer
from src.terminal.colors import ANSI_COLORS
from src.core.state_machine import StateMachine
from src.core.input import InputHandler
from src.states.start_screen import StartScreen
from src.audio.audio_manager import AudioManager

class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        
        # Create window
        self.screen = pygame.display.set_mode(
            (SETTINGS.WINDOW_WIDTH, SETTINGS.WINDOW_HEIGHT)
        )
        pygame.display.set_caption(SETTINGS.TITLE)
        
        # Create text buffer (the "terminal")
        self.buffer = TextBuffer(SETTINGS.COLS, SETTINGS.ROWS)
        
        # Create font renderer
        self.font_renderer = FontRenderer(
            SETTINGS.FONT_PATH,
            SETTINGS.CHAR_WIDTH,
            SETTINGS.CHAR_HEIGHT
        )
        
        # Create render surface
        self.render_surface = pygame.Surface(
            (SETTINGS.WINDOW_WIDTH, SETTINGS.WINDOW_HEIGHT)
        )
        
        # Systems
        self.clock = pygame.time.Clock()
        self.input = InputHandler()
        self.audio = AudioManager()
        
        # State machine
        self.state_machine = StateMachine()
        self.state_machine.push(StartScreen(self))
        
        self.running = True
    
    def run(self):
        while self.running:
            dt = self.clock.tick(SETTINGS.FPS) / 1000.0
            
            self._handle_events()
            self._update(dt)
            self._render()
    
    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
            
            # Update input handler
            self.input.update()
            
            # Pass to state (with character coordinates for mouse events)
            if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION):
                char_pos = self.input.get_char_pos()
                event.char_pos = char_pos
            
            self.state_machine.handle_event(event)
    
    def _update(self, dt: float):
        self.state_machine.update(dt)
    
    def _render(self):
        # Clear render surface with black
        self.render_surface.fill(ANSI_COLORS[0])
        
        # Render current state to text buffer
        self.state_machine.render(self.buffer)
        
        # Render text buffer to surface
        self.font_renderer.render(self.buffer, self.render_surface)
        
        # Blit to screen
        self.screen.blit(self.render_surface, (0, 0))
        
        pygame.display.flip()
```

---

### Build

Same PyInstaller process as the bitmap version:

```bash
pyinstaller --onefile --windowed --name=FissionImpossible \
    --add-data="assets:assets" main.py
```
