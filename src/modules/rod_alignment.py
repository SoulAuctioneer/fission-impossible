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

# Simon Says tone sounds for each color (low to high pitch)
COLOR_TONES = {
    'red': SFX.SIMON_TONE_RED,
    'blue': SFX.SIMON_TONE_BLUE,
    'green': SFX.SIMON_TONE_GREEN,
    'yellow': SFX.SIMON_TONE_YELLOW,
}

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
        
        # Watch button cooldown
        self.watch_cooldown = 0.0  # Seconds remaining before WATCH can be clicked
        self.WATCH_COOLDOWN_TIME = 10.0  # Cooldown duration in seconds
        
        # Stage flash effect
        self.stage_flash_timer = 0.0  # Time remaining for white flash on stage text
    
    def _generate_puzzle(self):
        """Generate the sequence."""
        # Generate full sequence upfront
        self.sequence = [random.choice(self.COLORS) for _ in range(self.max_stages)]
        
        # Start at stage 1 (2 colors), wait for player to press WATCH
        self.current_stage = 1
        self.state = self.State.INPUT
        self.input_index = 0
    
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
        
        # Update watch button cooldown
        if self.watch_cooldown > 0:
            self.watch_cooldown = max(0, self.watch_cooldown - dt)
        
        # Update stage flash timer
        if self.stage_flash_timer > 0:
            self.stage_flash_timer = max(0, self.stage_flash_timer - dt)
        
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
                        # Play the tone for this color
                        tone = COLOR_TONES.get(self.active_color)
                        if tone:
                            self.play_sound(tone)
    
    def _handle_click(self, local_x: int, local_y: int) -> bool:
        """Handle color button press."""
        # Check for WATCH button click (at y=9, x=15-24 area)
        if local_y == 9 and 15 <= local_x <= 24:
            if self.state == self.State.INPUT and self.watch_cooldown <= 0:
                self._start_showing()
                self.watch_cooldown = self.WATCH_COOLDOWN_TIME
                return True
            elif self.state == self.State.INPUT and self.watch_cooldown > 0:
                self.play_sound(SFX.BUTTON_ERROR)
                return True
        
        if self.state != self.State.INPUT:
            return False
        
        # Diamond layout (centered) - each button is 3 chars wide at letter position
        # Red: center x=14, y=2
        # Green: center x=8, y=4
        # Blue: center x=20, y=4
        # Yellow: center x=14, y=6
        
        pressed_color = None
        
        if local_y == 2 and 13 <= local_x <= 15:
            pressed_color = 'red'
        elif local_y == 4:
            if 7 <= local_x <= 9:
                pressed_color = 'green'
            elif 19 <= local_x <= 21:
                pressed_color = 'blue'
        elif local_y == 6 and 13 <= local_x <= 15:
            pressed_color = 'yellow'
        
        if pressed_color:
            # Play the tone for the pressed color
            tone = COLOR_TONES.get(pressed_color)
            if tone:
                self.play_sound(tone)
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
                    # Stage complete (but not final) - play sound and flash
                    self.play_sound(SFX.PATH_COMPLETE)
                    self.stage_flash_timer = 0.5  # Flash for 0.5 seconds
                    # Start next stage with cooldown
                    self._start_showing()
                    self.watch_cooldown = self.WATCH_COOLDOWN_TIME
        else:
            # Wrong color - strike and restart stage with cooldown
            self.strike()
            self._start_showing()
            self.watch_cooldown = self.WATCH_COOLDOWN_TIME
        
        # Clear active color after brief flash (will be cleared in render)
    
    def _render_content(self, buffer: "TextBuffer"):
        """Render the diamond of colored buttons."""
        # Diamond layout - centered in 28-char panel
        # Letter positions (center of each button)
        # Panel center is at x + 14
        buttons = {
            'red':    (self.x + 14, self.y + 2),   # Top center
            'green':  (self.x + 8,  self.y + 4),   # Left
            'blue':   (self.x + 20, self.y + 4),   # Right
            'yellow': (self.x + 14, self.y + 6),   # Bottom center
        }
        
        for color, (cx, cy) in buttons.items():
            is_active = (self.active_color == color)
            fg_color = self.COLOR_MAP[color]
            letter = color[0].upper()
            
            if is_active:
                # Lit up - filled box around letter
                buffer.put_char(cx - 1, cy, '█', fg_color)
                buffer.put_char(cx, cy, letter, Color.BLACK, fg_color)  # Letter with bg
                buffer.put_char(cx + 1, cy, '█', fg_color)
            else:
                # Dim outline when inactive
                buffer.put_char(cx - 1, cy, '[', Color.DARK_GRAY)
                buffer.put_char(cx, cy, letter, fg_color)
                buffer.put_char(cx + 1, cy, ']', Color.DARK_GRAY)
        
        # Stage indicator - centered (4 stages, starting from 2 colors)
        stage_y = self.y + 9
        total_stages = self.max_stages - 1  # 4 stages (skipping 1-color stage)
        display_stage = min(self.current_stage, total_stages)
        # Flash white when stage advances
        stage_color = Color.WHITE if self.stage_flash_timer > 0 else Color.LIGHT_CYAN
        buffer.put_string(self.x + 3, stage_y, f"STAGE: {display_stage}/{total_stages}", stage_color)
        
        # WATCH button / state indicator with border
        btn_x = self.x + 15
        btn_y = stage_y - 1  # Top border above stage line
        
        if self.state == self.State.SHOWING:
            # Currently showing sequence
            btn_color = Color.LIGHT_YELLOW
            btn_text = "SHOWING"
        elif self.state == self.State.INPUT:
            if self.watch_cooldown > 0:
                # Cooldown active - show remaining time
                btn_color = Color.DARK_GRAY
                btn_text = f"WAIT {int(self.watch_cooldown) + 1}s"
            else:
                # Ready to watch - clickable button
                btn_color = Color.LIGHT_GREEN
                btn_text = " WATCH "
        else:
            # IDLE state fallback
            btn_color = Color.DARK_GRAY
            btn_text = " WATCH "
        
        # Draw bordered button (9 chars wide interior)
        btn_text = btn_text.center(9)
        buffer.put_string(btn_x, btn_y, "┌─────────┐", btn_color)
        buffer.put_string(btn_x, btn_y + 1, f"│{btn_text}│", btn_color)
        buffer.put_string(btn_x, btn_y + 2, "└─────────┘", btn_color)
