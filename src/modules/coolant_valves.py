"""
Coolant Valves module (Wires).
Player must close the correct valve to stabilize coolant flow.
"""
import random
from typing import TYPE_CHECKING, List, Set

from src.modules.base_module import BaseModule
from src.terminal.colors import Color

if TYPE_CHECKING:
    from src.terminal.text_buffer import TextBuffer
    from src.core.game_state import GameState


class CoolantValvesModule(BaseModule):
    """
    Coolant Valves module - equivalent to Wires.
    3-6 colored pipes that must be closed in the right order.
    """
    
    # Wire/pipe colors
    COLORS = ['red', 'blue', 'yellow', 'white', 'black']
    
    # Display mapping
    COLOR_DISPLAY = {
        'red':    ('R', Color.LIGHT_RED),
        'blue':   ('B', Color.LIGHT_BLUE),
        'yellow': ('Y', Color.LIGHT_YELLOW),
        'white':  ('W', Color.WHITE),
        'black':  ('K', Color.DARK_GRAY),
    }
    
    def _initialize(self):
        """Initialize module variables."""
        self.wire_count = 0
        self.wire_colors: List[str] = []
        self.correct_wire = 0
        self.cut_wires: Set[int] = set()
    
    def _generate_puzzle(self):
        """Generate random wire configuration."""
        # Random number of wires (3-6)
        self.wire_count = random.randint(3, 6)
        
        # Random colors for each wire
        self.wire_colors = [random.choice(self.COLORS) for _ in range(self.wire_count)]
        
        # Determine correct wire based on rules
        self.correct_wire = self._determine_correct_wire()
        
        # Reset cut wires
        self.cut_wires = set()
    
    def _determine_correct_wire(self) -> int:
        """
        Determine which wire to cut based on game rules.
        Wire indices are 0-based internally, 1-based in display.
        """
        colors = self.wire_colors
        count = self.wire_count
        edgework = self.game_state.edgework
        
        # Count occurrences of each color
        red_count = colors.count('red')
        blue_count = colors.count('blue')
        yellow_count = colors.count('yellow')
        white_count = colors.count('white')
        black_count = colors.count('black')
        
        # Find last wire of each color
        def last_of_color(color):
            for i in range(count - 1, -1, -1):
                if colors[i] == color:
                    return i
            return -1
        
        # 3 wires
        if count == 3:
            if red_count == 0:
                return 1  # Second wire (0-indexed: 1)
            elif colors[-1] == 'white':
                return count - 1  # Last wire
            elif blue_count > 1:
                return last_of_color('blue')
            else:
                return count - 1  # Last wire
        
        # 4 wires
        elif count == 4:
            if red_count > 1 and edgework.serial_last_digit_odd():
                return last_of_color('red')
            elif colors[-1] == 'yellow' and red_count == 0:
                return 0  # First wire
            elif blue_count == 1:
                return 0  # First wire
            elif yellow_count > 1:
                return count - 1  # Last wire
            else:
                return 1  # Second wire
        
        # 5 wires
        elif count == 5:
            if colors[-1] == 'black' and edgework.serial_last_digit_odd():
                return 3  # Fourth wire (0-indexed: 3)
            elif red_count == 1 and yellow_count > 1:
                return 0  # First wire
            elif black_count == 0:
                return 1  # Second wire
            else:
                return 0  # First wire
        
        # 6 wires
        else:  # count == 6
            if yellow_count == 0 and edgework.serial_last_digit_odd():
                return 2  # Third wire (0-indexed: 2)
            elif yellow_count == 1 and white_count > 1:
                return 3  # Fourth wire (0-indexed: 3)
            elif red_count == 0:
                return count - 1  # Last wire
            else:
                return 3  # Fourth wire (0-indexed: 3)
    
    def _handle_click(self, local_x: int, local_y: int) -> bool:
        """Handle click to cut a wire."""
        # Check if click is on a wire
        wire_start_y = 2
        
        for i in range(self.wire_count):
            wire_y = wire_start_y + i * 2
            
            # Check if clicked on this wire's row (with some tolerance)
            if local_y == wire_y and 2 <= local_x <= self.width - 3:
                if i not in self.cut_wires:
                    self._cut_wire(i)
                    return True
        
        return False
    
    def _cut_wire(self, wire_index: int):
        """Cut the specified wire."""
        self.cut_wires.add(wire_index)
        
        if wire_index == self.correct_wire:
            # Correct wire - solve the module
            self.solve()
        else:
            # Wrong wire - strike!
            self.strike()
    
    def _render_content(self, buffer: "TextBuffer"):
        """Render the wire display."""
        wire_start_y = self.y + 2
        
        for i, color in enumerate(self.wire_colors):
            wire_y = wire_start_y + i * 2
            
            # Wire label
            label, label_color = self.COLOR_DISPLAY[color]
            buffer.put_char(self.x + 2, wire_y, '[', Color.DARK_GRAY)
            buffer.put_char(self.x + 3, wire_y, label, label_color)
            buffer.put_char(self.x + 4, wire_y, ']', Color.DARK_GRAY)
            
            # Wire itself
            if i in self.cut_wires:
                # Cut wire
                wire_text = "═══╳═══════"
            else:
                # Intact wire
                wire_text = "═══════════"
            
            # Adjust color for cut wires
            wire_color = Color.DARK_GRAY if i in self.cut_wires else label_color
            buffer.put_string(self.x + 6, wire_y, wire_text, wire_color)
            
            # Wire number for reference
            buffer.put_char(self.x + 19, wire_y, str(i + 1), Color.DARK_GRAY)
