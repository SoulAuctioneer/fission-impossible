"""
End screen - Victory or failure display with auto-reset.
"""
import pygame
from typing import TYPE_CHECKING

from src.states.base_state import BaseState
from src.terminal.box_drawing import draw_box, draw_titled_box, DOUBLE, SINGLE
from src.terminal.colors import Color
from src.core.settings import SETTINGS

if TYPE_CHECKING:
    from src.core.game import Game
    from src.terminal.text_buffer import TextBuffer


class EndScreen(BaseState):
    """
    End screen showing victory or failure message.
    Auto-transitions back to start screen after a delay.
    """
    
    def __init__(self, game: "Game", victory: bool, time_remaining: float, strikes: int):
        super().__init__(game)
        self.victory = victory
        self.time_remaining = time_remaining
        self.strikes = strikes
        
        # Auto-reset timer (10 seconds)
        self.reset_timer = 10.0
        
        # Flash effect for failure
        self.flash_timer = 0.0
        self.flash_active = not victory
    
    def enter(self):
        """Called when entering end screen."""
        # Set heavy flicker for failure screen (flicker persists from game)
        if not self.victory:
            self.game.screen_flicker.intensity = SETTINGS.EFFECT_FLICKER_FAILURE
    
    def update(self, dt: float):
        """Update end screen."""
        # Update flash effect
        if self.flash_active:
            self.flash_timer += dt
            if self.flash_timer >= 0.3:
                self.flash_active = False
        
        # Update reset timer
        self.reset_timer -= dt
        if self.reset_timer <= 0:
            self._return_to_start()
    
    def _return_to_start(self):
        """Return to start screen."""
        # Reset flicker to calm state
        self.game.screen_flicker.intensity = SETTINGS.EFFECT_FLICKER_0_STRIKES
        from src.states.start_screen import StartScreen
        self.game.state_machine.switch(StartScreen(self.game))
    
    def handle_event(self, event: pygame.event.Event):
        """Handle input events."""
        # Allow early skip with any key or click
        if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
            self._return_to_start()
    
    def render(self, buffer: "TextBuffer"):
        """Render end screen."""
        # Flash effect
        if self.flash_active:
            buffer.fill_rect(0, 0, buffer.width, buffer.height, '█', Color.WHITE, Color.WHITE)
            return
        
        buffer.clear()
        
        # Border
        draw_box(buffer, 0, 0, buffer.width, buffer.height, DOUBLE, Color.GREEN)
        
        if self.victory:
            self._render_victory(buffer)
        else:
            self._render_failure(buffer)
        
        # Reset countdown
        countdown = int(self.reset_timer) + 1
        buffer.put_string_centered(buffer.height - 4, 
            f"Returning to clock-in terminal in {countdown}...", Color.DARK_GRAY)
        buffer.put_string_centered(buffer.height - 3,
            "Press any key to continue", Color.DARK_GRAY)
    
    def _render_victory(self, buffer: "TextBuffer"):
        """Render victory screen."""
        center_y = buffer.height // 2 - 8
        
        # Success message
        buffer.put_string_centered(center_y, "╔════════════════════════════════════╗", Color.LIGHT_GREEN)
        buffer.put_string_centered(center_y + 1, "║                                    ║", Color.LIGHT_GREEN)
        buffer.put_string_centered(center_y + 2, "║       √ SHIFT COMPLETE √          ║", Color.LIGHT_GREEN)
        buffer.put_string_centered(center_y + 3, "║                                    ║", Color.LIGHT_GREEN)
        buffer.put_string_centered(center_y + 4, "╚════════════════════════════════════╝", Color.LIGHT_GREEN)
        
        # Stats
        y = center_y + 7
        buffer.put_string_centered(y, "All systems stabilized. Meltdown averted.", Color.LIGHT_GREEN)
        
        y += 2
        mins = int(self.time_remaining) // 60
        secs = int(self.time_remaining) % 60
        buffer.put_string_centered(y, f"Time remaining: {mins:02d}:{secs:02d}", Color.LIGHT_CYAN)
        
        y += 1
        buffer.put_string_centered(y, f"Errors logged: {self.strikes}", Color.LIGHT_CYAN)
        
        y += 3
        buffer.put_string_centered(y, "─────────────────────────────────────", Color.GREEN)
        
        y += 2
        buffer.put_string_centered(y, "This incident has been classified as:", Color.LIGHT_GREEN)
        y += 1
        buffer.put_string_centered(y, '"MINOR FLUCTUATION - NO FURTHER ACTION"', Color.LIGHT_YELLOW)
        
        y += 3
        buffer.put_string_centered(y, "Your performance review has been updated.", Color.DARK_GRAY)
        
        # Footer
        buffer.put_string_centered(buffer.height - 6, 
            'NUHAUS NUCLEAR - "Powering Tomorrow, Today... Eventually"', Color.DARK_GRAY)
    
    def _render_failure(self, buffer: "TextBuffer"):
        """Render failure screen."""
        center_y = buffer.height // 2 - 8
        
        # Failure message
        buffer.put_string_centered(center_y, "████████████████████████████████████", Color.LIGHT_RED)
        buffer.put_string_centered(center_y + 1, "████████████████████████████████████", Color.LIGHT_RED)
        buffer.put_string_centered(center_y + 2, "████    SIGNAL LOST    ████", Color.WHITE, Color.RED)
        buffer.put_string_centered(center_y + 3, "████████████████████████████████████", Color.LIGHT_RED)
        buffer.put_string_centered(center_y + 4, "████████████████████████████████████", Color.LIGHT_RED)
        
        y = center_y + 7
        buffer.put_string_centered(y, "─────────────────────────────────────", Color.DARK_GRAY)
        
        y += 2
        buffer.put_string_centered(y, '"NuHaus Nuclear extends its deepest condolences', Color.DARK_GRAY)
        y += 1
        buffer.put_string_centered(y, 'to the families of [INSERT EMPLOYEE NAMES HERE]."', Color.DARK_GRAY)
        
        y += 3
        buffer.put_string_centered(y, "Please direct all complaints by fax to our Legal department, Boris.", Color.DARK_GRAY)
        
        y += 2
        buffer.put_string_centered(y, "─────────────────────────────────────", Color.DARK_GRAY)
        
        y += 2
        buffer.put_string_centered(y, "Resetting terminal for next shift...", Color.DARK_GRAY)
