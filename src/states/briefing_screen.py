"""
Briefing screen - Interstitial shown between start and game screens.
"""
import pygame
from typing import TYPE_CHECKING

from src.states.base_state import BaseState
from src.terminal.box_drawing import draw_box, DOUBLE
from src.terminal.colors import Color

if TYPE_CHECKING:
    from src.core.game import Game
    from src.terminal.text_buffer import TextBuffer


class BriefingScreen(BaseState):
    """
    Brief interstitial screen shown after clocking in.
    Displays important instructions for the technician.
    """
    
    DISPLAY_DURATION = 5.0  # seconds
    
    def __init__(self, game: "Game"):
        super().__init__(game)
        self.elapsed_time = 0.0
        self.blink_timer = 0.0
        self.blink_state = True
    
    def enter(self):
        """Called when entering this state."""
        self.elapsed_time = 0.0
    
    def update(self, dt: float):
        """Update briefing screen."""
        self.elapsed_time += dt
        
        # Update blink timer for visual effects
        self.blink_timer += dt
        if self.blink_timer >= 0.4:
            self.blink_timer = 0.0
            self.blink_state = not self.blink_state
        
        # Transition to game screen after duration
        if self.elapsed_time >= self.DISPLAY_DURATION:
            from src.states.game_screen import GameScreen
            self.game.state_machine.switch(GameScreen(self.game))
    
    def handle_event(self, event: pygame.event.Event):
        """Handle input events."""
        # Allow skipping with any key or mouse click
        if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
            from src.states.game_screen import GameScreen
            self.game.state_machine.switch(GameScreen(self.game))
    
    def render(self, buffer: "TextBuffer"):
        """Render briefing screen."""
        buffer.clear()
        
        # Outer border
        draw_box(buffer, 0, 0, buffer.width, buffer.height, DOUBLE, Color.GREEN)
        
        # Header
        header = "████  NUHAUS NUCLEAR - MAINTENANCE TERMINAL v2.4.1  ████"
        buffer.put_string_centered(2, header, Color.LIGHT_GREEN)
        
        # Divider
        buffer.put_string(2, 4, "═" * (buffer.width - 4), Color.GREEN)
        
        # Main message - centered vertically
        center_y = buffer.height // 2
        
        # Role indicator
        role_line = "▶ TECHNICIAN ◀"
        buffer.put_string_centered(center_y - 4, role_line, Color.LIGHT_CYAN)
        
        # Main instructions
        line1 = "This terminal is for your eyes ONLY."
        line2 = "You CANNOT read the maintenance manual."
        
        buffer.put_string_centered(center_y - 1, line1, Color.LIGHT_YELLOW)
        buffer.put_string_centered(center_y + 1, line2, Color.LIGHT_YELLOW)
        
        # Emphasis box around the message
        box_width = max(len(line1), len(line2)) + 8
        box_x = (buffer.width - box_width) // 2
        draw_box(buffer, box_x, center_y - 3, box_width, 7, DOUBLE, Color.LIGHT_YELLOW)
        
        # Progress indicator
        progress_y = center_y + 6
        remaining = max(0, self.DISPLAY_DURATION - self.elapsed_time)
        progress_text = f"Initializing systems... {remaining:.1f}s"
        buffer.put_string_centered(progress_y, progress_text, Color.DARK_GRAY)
        
        # Progress bar
        bar_width = 30
        bar_x = (buffer.width - bar_width) // 2
        progress = self.elapsed_time / self.DISPLAY_DURATION
        filled = int(progress * bar_width)
        bar_str = "█" * filled + "░" * (bar_width - filled)
        buffer.put_string(bar_x, progress_y + 2, bar_str, Color.GREEN)
        
        # Skip hint (blinking)
        if self.blink_state:
            skip_hint = "Press any key to continue..."
            buffer.put_string_centered(buffer.height - 5, skip_hint, Color.DARK_GRAY)
        
        # Footer
        footer_y = buffer.height - 3
        buffer.put_string(2, footer_y, 'NUHAUS NUCLEAR - "We\'re Glad You\'re Expendable"', Color.DARK_GRAY)
        buffer.put_string(buffer.width - 15, footer_y, "TERMINAL 7-G", Color.DARK_GRAY)
