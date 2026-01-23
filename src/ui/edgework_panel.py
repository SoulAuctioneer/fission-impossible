"""
Edgework panel - displays batteries, indicators, serial number, and ports.
Rendered at bottom of screen with graphical ASCII art elements.

PANEL LAYOUT (136 wide × 9 tall, positioned at x=2, y=35)
═════════════════════════════════════════════════════════════════════════════════

    ╔══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
    ║                                                  REACTOR EDGEWORK                                                                ║
    ║                                                                                                                                  ║
    ║   SERIAL NO.        BATTERIES                    PARALLEL PORT           INDICATOR LIGHTS                                       ║
    ║   ╔══════════╗      ┌──┬┐ ┌──┬┐ ┌──┬┐ ┌────┐    ╔══════════════════╗    ┌──────────────────────────────────────────────────────┐║
    ║   ║  AB3·CD5 ║      │▓▓││ │▓▓││ │▓▓││ │    │    ║ ooooooooooooooo ║    │ ◄●► CAR  ◄○► FRK  ◄●► SIG  ◄○► BOB                    │║
    ║   ╚══════════╝      └──┴┘ └──┴┘ └──┴┘ └────┘    ╚══════════════════╝    │ ◄●► CLR  ◄○► IND                                      │║
    ║                     × 3                          [INSTALLED]            └──────────────────────────────────────────────────────┘║
    ╚══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝

SECTION POSITIONS (relative to panel x, content starts at y+2):
    Serial plate:    x+2   (12 chars wide)
    Batteries:       x+18  (24 chars wide, 4 slots × 6 chars each)
    Parallel port:   x+46  (20 chars wide)
    Indicators:      x+70  (56 chars wide, up to 8 indicators in 2 rows)

Each section has:
    - Row 0: Label (e.g., "SERIAL NO.", "BATTERIES")
    - Rows 1-4: Graphical content
"""
from typing import TYPE_CHECKING

from src.terminal.box_drawing import draw_box, SINGLE, DOUBLE
from src.terminal.colors import Color

if TYPE_CHECKING:
    from src.terminal.text_buffer import TextBuffer
    from src.core.game_state import GameState


class EdgewWorkPanel:
    """
    Graphical edgework display panel showing batteries and indicators.
    """
    
    def __init__(self, x: int, y: int, width: int, height: int):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
    
    def render(self, buffer: "TextBuffer", game_state: "GameState"):
        """Render the edgework panel."""
        edgework = game_state.edgework
        
        # Draw main panel border
        draw_box(buffer, self.x, self.y, self.width, self.height, DOUBLE, Color.GREEN)
        
        # Title
        title = " REACTOR EDGEWORK "
        title_x = self.x + (self.width - len(title)) // 2
        buffer.put_string(title_x, self.y, title, Color.LIGHT_CYAN)
        
        # Content starts at y+2 to leave room for border and spacing
        content_y = self.y + 2
        
        # === SERIAL NUMBER (left section) ===
        self._render_serial_plate(buffer, self.x + 2, content_y, edgework.serial_number)
        
        # === BATTERIES (center-left section) ===
        self._render_batteries(buffer, self.x + 18, content_y, edgework.batteries)
        
        # === PARALLEL PORT (center section) ===
        self._render_parallel_port(buffer, self.x + 46, content_y, edgework.has_parallel)
        
        # === INDICATORS (right section) ===
        self._render_indicators(buffer, self.x + 70, content_y, edgework.indicators)
    
    def _render_serial_plate(self, buffer: "TextBuffer", x: int, y: int, serial: str):
        """Render serial number on a metal plate."""
        # Label
        buffer.put_string(x, y, "SERIAL NO.", Color.DARK_GRAY)
        
        # Compact plate
        plate_y = y + 1
        buffer.put_string(x, plate_y, "╔══════════╗", Color.LIGHT_GRAY)
        buffer.put_string(x, plate_y + 1, "║  " + serial[:3] + "·" + serial[3:] + " ║", Color.LIGHT_GRAY)
        buffer.put_string(x, plate_y + 2, "╚══════════╝", Color.LIGHT_GRAY)
        
        # Serial number colored
        buffer.put_string(x + 3, plate_y + 1, serial[:3], Color.LIGHT_YELLOW)
        buffer.put_char(x + 6, plate_y + 1, "·", Color.DARK_GRAY)
        buffer.put_string(x + 7, plate_y + 1, serial[3:], Color.LIGHT_YELLOW)
        
        # Rivets
        buffer.put_char(x + 1, plate_y + 2, "◦", Color.DARK_GRAY)
        buffer.put_char(x + 10, plate_y + 2, "◦", Color.DARK_GRAY)
    
    def _render_batteries(self, buffer: "TextBuffer", x: int, y: int, count: int):
        """Render battery holders with ASCII art batteries."""
        buffer.put_string(x, y, "BATTERIES", Color.DARK_GRAY)
        
        # Battery slot row - compact 3-row design
        slot_y = y + 1
        
        # Draw 4 battery slots (each 6 chars wide)
        for i in range(4):
            slot_x = x + i * 6
            
            if i < count:
                # Filled battery - compact AA style
                buffer.put_string(slot_x, slot_y, "┌──┬┐", Color.LIGHT_GRAY)
                buffer.put_string(slot_x, slot_y + 1, "│▓▓││", Color.LIGHT_GREEN)
                buffer.put_string(slot_x, slot_y + 2, "└──┴┘", Color.LIGHT_GRAY)
                # Positive terminal
                buffer.put_char(slot_x + 3, slot_y, "┬", Color.LIGHT_CYAN)
                buffer.put_char(slot_x + 3, slot_y + 1, "│", Color.LIGHT_CYAN)
            else:
                # Empty slot
                buffer.put_string(slot_x, slot_y, "┌────┐", Color.DARK_GRAY)
                buffer.put_string(slot_x, slot_y + 1, "│    │", Color.DARK_GRAY)
                buffer.put_string(slot_x, slot_y + 2, "└────┘", Color.DARK_GRAY)
        
        # Count indicator
        buffer.put_string(x + 1, slot_y + 3, f"× {count}", Color.LIGHT_CYAN)
    
    def _render_parallel_port(self, buffer: "TextBuffer", x: int, y: int, has_port: bool):
        """Render parallel port connector."""
        buffer.put_string(x, y, "PARALLEL PORT", Color.DARK_GRAY)
        
        port_y = y + 1
        
        if has_port:
            # DB-25 style parallel port (present) - compact
            buffer.put_string(x, port_y, "╔══════════════════╗", Color.LIGHT_CYAN)
            buffer.put_string(x, port_y + 1, "║ ooooooooooooooo ║", Color.LIGHT_CYAN)
            buffer.put_string(x, port_y + 2, "╚══════════════════╝", Color.LIGHT_CYAN)
            # Pin holes colored
            buffer.put_string(x + 2, port_y + 1, "ooooooooooooooo", Color.DARK_GRAY)
            # Status
            buffer.put_string(x + 4, port_y + 3, "[INSTALLED]", Color.LIGHT_GREEN)
        else:
            # Empty port slot
            buffer.put_string(x, port_y, "╔══════════════════╗", Color.DARK_GRAY)
            buffer.put_string(x, port_y + 1, "║     [EMPTY]      ║", Color.DARK_GRAY)
            buffer.put_string(x, port_y + 2, "╚══════════════════╝", Color.DARK_GRAY)
            buffer.put_string(x + 6, port_y + 3, "[NONE]", Color.DARK_GRAY)
    
    def _render_indicators(self, buffer: "TextBuffer", x: int, y: int, indicators: dict):
        """Render indicator lights panel."""
        buffer.put_string(x, y, "INDICATOR LIGHTS", Color.DARK_GRAY)
        
        # Panel background - compact 2 rows
        panel_y = y + 1
        panel_width = 56
        buffer.put_string(x, panel_y, "┌" + "─" * (panel_width - 2) + "┐", Color.LIGHT_GRAY)
        buffer.put_string(x, panel_y + 1, "│" + " " * (panel_width - 2) + "│", Color.LIGHT_GRAY)
        buffer.put_string(x, panel_y + 2, "│" + " " * (panel_width - 2) + "│", Color.LIGHT_GRAY)
        buffer.put_string(x, panel_y + 3, "└" + "─" * (panel_width - 2) + "┘", Color.LIGHT_GRAY)
        
        # Render indicators in 2 rows, 4 per row max
        col = 0
        row = 0
        for label, lit in indicators.items():
            led_x = x + 2 + col * 13
            led_y = panel_y + 1 + row
            
            # LED housing and light with label
            if lit:
                # Lit indicator - glowing LED
                buffer.put_string(led_x, led_y, "◄", Color.LIGHT_YELLOW)
                buffer.put_char(led_x + 1, led_y, "●", Color.LIGHT_YELLOW)
                buffer.put_string(led_x + 2, led_y, "►", Color.LIGHT_YELLOW)
                buffer.put_string(led_x + 4, led_y, label, Color.WHITE)
            else:
                # Unlit indicator - dark LED
                buffer.put_string(led_x, led_y, "◄", Color.DARK_GRAY)
                buffer.put_char(led_x + 1, led_y, "○", Color.DARK_GRAY)
                buffer.put_string(led_x + 2, led_y, "►", Color.DARK_GRAY)
                buffer.put_string(led_x + 4, led_y, label, Color.DARK_GRAY)
            
            col += 1
            if col >= 4:
                col = 0
                row += 1
