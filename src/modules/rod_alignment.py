"""
Rod Alignment module (Simon Says).
Watch the flashing sequence and repeat with color mapping.
"""
import random
from typing import TYPE_CHECKING, List, Optional
from enum import Enum

from src.modules.base_module import BaseModule
from src.terminal.colors import Color
from src.audio.audio_manager import SFX

if TYPE_CHECKING:
    from src.terminal.text_buffer import TextBuffer
    from src.core.game_state import GameState


class RodAlignmentModule(BaseModule):
    """
    Rod Alignment module - equivalent to Simon Says.
    Watch colored light sequence and press in mapped order.
    """
    
    # Colors in the diamond layout
    COLORS = ['red', 'blue', 'green', 'yellow']
    
    # Color display mapping
    COLOR_MAP = {
        'red': Color.LIGHT_RED,
        'blue': Color.LIGHT_BLUE,
        'green': Color.LIGHT_GREEN,
        'yellow': Color.LIGHT_YELLOW,
    }
    
    # Color mapping tables based on serial vowel and strike count
    # Format: {has_vowel: {strike_count: {flash_color: press_color}}}
    MAPPINGS = {
        True: {  # Serial has vowel
            0: {'red': 'blue', 'blue': 'red', 'green': 'yellow', 'yellow': 'green'},
            1: {'red': 'yellow', 'blue': 'green', 'green': 'blue', 'yellow': 'red'},
            2: {'red': 'green', 'blue': 'red', 'green': 'yellow', 'yellow': 'blue'},
        },
        False: {  # Serial has no vowel
            0: {'red': 'blue', 'blue': 'yellow', 'green': 'green', 'yellow': 'red'},
            1: {'red': 'red', 'blue': 'blue', 'green': 'yellow', 'yellow': 'green'},
            2: {'red': 'yellow', 'blue': 'green', 'green': 'blue', 'yellow': 'red'},
        },
    }
    
    class State(Enum):
        IDLE = 0
        SHOWING = 1
        INPUT = 2
    
    def _initialize(self):
        """Initialize module variables."""
        self.sequence: List[str] = []  # The full sequence to complete
        self.current_stage = 0  # Current stage (0-4)
        self.max_stages = 5
        
        # Playback state
        self.state = self.State.IDLE
        self.show_index = 0  # Current position in sequence being shown
        self.show_timer = 0.0
        self.flash_on = False
        
        # Input state
        self.input_index = 0  # Current expected input position
        
        # Visual state
        self.active_color: Optional[str] = None  # Currently lit color
    
    def _generate_puzzle(self):
        """Generate the sequence."""
        # Generate full sequence upfront
        self.sequence = [random.choice(self.COLORS) for _ in range(self.max_stages)]
        
        # Start at stage 0
        self.current_stage = 0
        self._start_showing()
    
    def _get_mapping(self, flash_color: str) -> str:
        """Get the color to press based on flash color."""
        has_vowel = self.game_state.edgework.has_vowel_in_serial()
        strikes = min(self.game_state.strikes, 2)  # Cap at 2 for mapping table
        
        mapping = self.MAPPINGS[has_vowel][strikes]
        return mapping.get(flash_color, flash_color)
    
    def _start_showing(self):
        """Start showing the sequence."""
        self.state = self.State.SHOWING
        self.show_index = 0
        self.show_timer = 0.0
        self.flash_on = False
        self.active_color = None
    
    def _start_input(self):
        """Switch to input mode."""
        self.state = self.State.INPUT
        self.input_index = 0
        self.active_color = None
    
    def update(self, dt: float):
        """Update sequence display."""
        if self.solved:
            return
        
        if self.state == self.State.SHOWING:
            self.show_timer += dt
            
            # Flash timing: 0.5s on, 0.3s off
            if self.flash_on:
                if self.show_timer >= 0.5:
                    self.show_timer = 0.0
                    self.flash_on = False
                    self.active_color = None
                    self.show_index += 1
                    
                    # Check if done showing
                    if self.show_index > self.current_stage:
                        self._start_input()
            else:
                if self.show_timer >= 0.3:
                    self.show_timer = 0.0
                    self.flash_on = True
                    
                    if self.show_index <= self.current_stage:
                        self.active_color = self.sequence[self.show_index]
    
    def _handle_click(self, local_x: int, local_y: int) -> bool:
        """Handle color button press."""
        if self.state != self.State.INPUT:
            return False
        
        # Diamond layout:
        # Red at top: x=10-16, y=2-3
        # Green left: x=3-9, y=4-5
        # Blue right: x=17-23, y=4-5
        # Yellow bottom: x=10-16, y=6-7
        
        pressed_color = None
        
        if 10 <= local_x <= 16:
            if 2 <= local_y <= 3:
                pressed_color = 'red'
            elif 6 <= local_y <= 7:
                pressed_color = 'yellow'
        elif 4 <= local_y <= 5:
            if 3 <= local_x <= 9:
                pressed_color = 'green'
            elif 17 <= local_x <= 23:
                pressed_color = 'blue'
        
        if pressed_color:
            self._press_color(pressed_color)
            return True
        
        return False
    
    def _press_color(self, color: str):
        """Handle a color button press."""
        # Get expected color based on mapping
        flash_color = self.sequence[self.input_index]
        expected_color = self._get_mapping(flash_color)
        
        # Flash the pressed button briefly
        self.active_color = color
        self.play_sound(SFX.ROD_MOVE)
        
        if color == expected_color:
            self.input_index += 1
            self.play_sound(SFX.ROD_LOCK)
            
            # Check if stage complete
            if self.input_index > self.current_stage:
                self.current_stage += 1
                
                # Check if all stages complete
                if self.current_stage >= self.max_stages:
                    self.solve()
                else:
                    # Start next stage
                    self._start_showing()
        else:
            # Wrong color - strike and restart stage
            self.strike()
            self._start_showing()
        
        # Clear active color after brief flash (will be cleared in render)
    
    def _render_content(self, buffer: "TextBuffer"):
        """Render the diamond of colored buttons."""
        # Diamond positions (x, y, width, height)
        buttons = {
            'red':    (self.x + 10, self.y + 2, 7, 2),
            'green':  (self.x + 3,  self.y + 4, 7, 2),
            'blue':   (self.x + 17, self.y + 4, 7, 2),
            'yellow': (self.x + 10, self.y + 6, 7, 2),
        }
        
        for color, (bx, by, bw, bh) in buttons.items():
            is_active = (self.active_color == color)
            fg_color = self.COLOR_MAP[color]
            
            if is_active:
                # Bright/filled when active
                for dy in range(bh):
                    buffer.put_string(bx, by + dy, '█' * bw, fg_color)
            else:
                # Dim outline when inactive
                buffer.put_char(bx, by, '[', Color.DARK_GRAY)
                buffer.put_char(bx + 1, by, color[0].upper(), fg_color)
                buffer.put_char(bx + 2, by, ']', Color.DARK_GRAY)
        
        # Stage indicator
        stage_y = self.y + 9
        buffer.put_string(self.x + 2, stage_y, f"STAGE: {self.current_stage + 1}/{self.max_stages}", Color.LIGHT_CYAN)
        
        # State indicator
        if self.state == self.State.SHOWING:
            buffer.put_string(self.x + 16, stage_y, "WATCH", Color.LIGHT_YELLOW)
        elif self.state == self.State.INPUT:
            buffer.put_string(self.x + 16, stage_y, "INPUT", Color.LIGHT_GREEN)
