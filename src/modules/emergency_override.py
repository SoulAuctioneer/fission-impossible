"""
Emergency Override module (The Button).
Press or hold based on button color, label, and edgework.
"""
import random
from typing import TYPE_CHECKING, Optional

from src.modules.base_module import BaseModule
from src.terminal.box_drawing import draw_box, DOUBLE, SINGLE
from src.terminal.colors import Color

if TYPE_CHECKING:
    from src.terminal.text_buffer import TextBuffer
    from src.core.game_state import GameState


class EmergencyOverrideModule(BaseModule):
    """
    Emergency Override module - equivalent to The Button.
    Press or hold the button based on complex rules.
    """
    
    # Button colors
    BUTTON_COLORS = ['red', 'blue', 'yellow', 'white']
    
    # Button labels
    BUTTON_LABELS = ['ABORT', 'DETONATE', 'HOLD', 'PRESS']
    
    # Strip colors
    STRIP_COLORS = ['blue', 'yellow', 'red', 'white']
    
    # Color display mapping
    COLOR_MAP = {
        'red': Color.LIGHT_RED,
        'blue': Color.LIGHT_BLUE,
        'yellow': Color.LIGHT_YELLOW,
        'white': Color.WHITE,
    }
    
    def _initialize(self):
        """Initialize module variables."""
        self.button_color = 'red'
        self.button_label = 'ABORT'
        self.strip_color = 'blue'
        
        # Button state
        self.is_holding = False
        self.hold_time = 0.0
        self.strip_visible = False
        
        # Determines whether to hold or press
        self.should_hold = False
    
    def _generate_puzzle(self):
        """Generate button configuration."""
        self.button_color = random.choice(self.BUTTON_COLORS)
        self.button_label = random.choice(self.BUTTON_LABELS)
        self.strip_color = random.choice(self.STRIP_COLORS)
        
        # Determine if player should hold or press
        self.should_hold = self._determine_action()
        
        # Reset state
        self.is_holding = False
        self.hold_time = 0.0
        self.strip_visible = False
    
    def _determine_action(self) -> bool:
        """
        Determine if player should hold the button.
        Returns True if should hold, False if should press.
        """
        edgework = self.game_state.edgework
        
        # If the button is blue and the button says "ABORT", hold
        if self.button_color == 'blue' and self.button_label == 'ABORT':
            return True
        
        # If there is more than 1 battery and the button says "DETONATE", press
        if edgework.batteries > 1 and self.button_label == 'DETONATE':
            return False
        
        # If the button is white and there is a lit indicator with label CAR, hold
        if self.button_color == 'white' and edgework.indicator_lit('CAR'):
            return True
        
        # If there are more than 2 batteries and there is a lit indicator with label FRK, press
        if edgework.batteries > 2 and edgework.indicator_lit('FRK'):
            return False
        
        # If the button is yellow, hold
        if self.button_color == 'yellow':
            return True
        
        # If the button is red and the button says "HOLD", press
        if self.button_color == 'red' and self.button_label == 'HOLD':
            return False
        
        # Otherwise, hold
        return True
    
    def _get_release_digit(self) -> int:
        """Get the digit when player should release based on strip color."""
        strip_rules = {
            'blue': 4,
            'yellow': 5,
            'red': 1,
            'white': 1,
        }
        return strip_rules.get(self.strip_color, 1)
    
    def _handle_click(self, local_x: int, local_y: int) -> bool:
        """Handle button press."""
        # Button area: roughly center of module
        button_x1, button_x2 = 6, 22
        button_y1, button_y2 = 3, 7
        
        if button_x1 <= local_x <= button_x2 and button_y1 <= local_y <= button_y2:
            if not self.is_holding:
                self._press_button()
            return True
        
        return False
    
    def _press_button(self):
        """Start pressing the button."""
        self.is_holding = True
        self.hold_time = 0.0
        self.strip_visible = True
    
    def _release_button(self):
        """Release the button and check result."""
        was_holding = self.is_holding
        self.is_holding = False
        self.strip_visible = False
        
        if not was_holding:
            return
        
        if self.should_hold:
            # Check if released at correct time
            release_digit = self._get_release_digit()
            timer_digit = self.game_state.timer_digit
            
            if timer_digit == release_digit:
                self.solve()
            else:
                self.strike()
        else:
            # Should have been a quick press
            if self.hold_time < 0.5:
                self.solve()
            else:
                self.strike()
    
    def update(self, dt: float):
        """Update hold timer."""
        if self.is_holding:
            self.hold_time += dt
    
    def handle_event(self, event, cx: int, cy: int):
        """Handle mouse events."""
        import pygame
        
        if self.solved or not self.active:
            return
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.contains_char(cx, cy):
                local_x, local_y = self.to_local_coords(cx, cy)
                self._handle_click(local_x, local_y)
        
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.is_holding:
                self._release_button()
    
    def _render_content(self, buffer: "TextBuffer"):
        """Render the button."""
        # Button
        button_color = self.COLOR_MAP.get(self.button_color, Color.WHITE)
        button_x = self.x + 6
        button_y = self.y + 3
        
        draw_box(buffer, button_x, button_y, 16, 5, DOUBLE, button_color)
        
        # Button label
        label_x = button_x + (16 - len(self.button_label)) // 2
        label_y = button_y + 2
        
        if self.is_holding:
            # Inverted colors when pressed
            buffer.put_string(label_x, label_y, self.button_label, Color.BLACK, button_color)
        else:
            buffer.put_string(label_x, label_y, self.button_label, Color.WHITE)
        
        # Strip indicator (when holding)
        strip_y = self.y + 9
        buffer.put_string(self.x + 2, strip_y, "STRIP:", Color.DARK_GRAY)
        
        if self.strip_visible:
            strip_color = self.COLOR_MAP.get(self.strip_color, Color.WHITE)
            buffer.put_string(self.x + 9, strip_y, "[████████]", strip_color)
        else:
            buffer.put_string(self.x + 9, strip_y, "[░░░░░░░░]", Color.DARK_GRAY)
