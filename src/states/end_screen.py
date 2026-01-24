"""
End screen - Victory or failure display with auto-reset.
"""
import pygame
from typing import TYPE_CHECKING, Optional

from src.states.base_state import BaseState
from src.terminal.box_drawing import draw_box, draw_titled_box, DOUBLE, SINGLE
from src.terminal.colors import Color
from src.core.settings import SETTINGS
from src.ui.reactor_status import ReactorStatusPanel
from src.core.game_state import GameState

if TYPE_CHECKING:
    from src.core.game import Game
    from src.terminal.text_buffer import TextBuffer


class EndScreen(BaseState):
    """
    End screen showing victory or failure message.
    Auto-transitions back to start screen after a delay.
    """
    
    def __init__(self, game: "Game", victory: bool, game_state: Optional[GameState] = None,
                 time_remaining: float = 0, strikes: int = 0):
        super().__init__(game)
        self.victory = victory
        
        # Use provided game_state or create a minimal one for testing
        if game_state:
            self.game_state = game_state
            self.time_remaining = game_state.time_remaining
            self.strikes = game_state.strikes
        else:
            # Fallback for testing - create mock state
            self.game_state = GameState()
            self.game_state.time_remaining = time_remaining
            self.game_state.strikes = strikes
            self.time_remaining = time_remaining
            self.strikes = strikes
        
        # Freeze the game state (stop updates)
        self.game_state.game_over = True
        
        # Reactor status panel - same position as game screen (right side)
        self.status_panel = ReactorStatusPanel(100, 3, 42, 31)
        
        # Auto-reset timer (30 seconds)
        self.reset_timer = 30.0
        
        # Grace period before allowing skip (prevents accidental immediate skip)
        self.skip_grace_period = 2.0
        
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
            if self.flash_timer >= 1.5:
                self.flash_active = False
        
        # Update skip grace period
        if self.skip_grace_period > 0:
            self.skip_grace_period -= dt
        
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
        # Allow early skip with any key or click (after grace period)
        if self.skip_grace_period <= 0:
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                self._return_to_start()
    
    def render(self, buffer: "TextBuffer"):
        """Render end screen."""
        # Flash effect
        if self.flash_active:
            buffer.fill_rect(0, 0, buffer.width, buffer.height, '█', Color.WHITE, Color.WHITE)
            return
        
        buffer.clear()
        
        # Border - green for victory, red for failure
        border_color = Color.GREEN if self.victory else Color.RED
        draw_box(buffer, 0, 0, buffer.width, buffer.height, DOUBLE, border_color)
        
        if self.victory:
            self._render_victory(buffer)
        else:
            self._render_failure(buffer)
        
        # Render reactor status panel on the right (frozen state from end of game)
        self.status_panel.render(buffer, self.game_state)
        
        # Reset countdown (positioned in left area to avoid status panel)
        countdown = int(self.reset_timer) + 1
        buffer.put_string(5, buffer.height - 4, 
            f"Returning to clock-in terminal in {countdown}...", Color.DARK_GRAY)
        buffer.put_string(5, buffer.height - 3,
            "Press any key to continue", Color.DARK_GRAY)
    
    def _render_victory(self, buffer: "TextBuffer"):
        """Render victory screen."""
        # Content area is left side (before status panel at x=100)
        content_width = 95
        center_x = content_width // 2
        
        y = 5
        
        # Success header box
        box_text = [
            "╔══════════════════════════════════════════╗",
            "║                                          ║",
            "║            √ SHIFT COMPLETE √            ║",
            "║                                          ║",
            "╚══════════════════════════════════════════╝",
        ]
        for i, line in enumerate(box_text):
            buffer.put_string(center_x - len(line)//2, y + i, line, Color.LIGHT_GREEN)
        
        y += 8
        
        # Stats
        mins = int(self.time_remaining) // 60
        secs = int(self.time_remaining) % 60
        # buffer.put_string(5, y, f"Safety violations logged: {self.strikes}", Color.LIGHT_CYAN)
        # buffer.put_string(35, y, "(within acceptable parameters)", Color.DARK_GRAY)
        
        # y += 3
        # buffer.put_string(7, y, "─" * 85, Color.GREEN)

        y += 3
        buffer.put_string(17, y, "INCIDENT CLASSIFICATION:", Color.LIGHT_YELLOW)
        y += 1
        buffer.put_string(17, y, '"Minor Fluctuation - No Further Action Required (probably)"', Color.DARK_GRAY)
        
        # y += 2
        # buffer.put_string(5, y, "OFFICIAL STATEMENT:", Color.LIGHT_GREEN)
        # y += 1
        # buffer.put_string(5, y, '"At no point was there any danger to personnel or the public."', Color.DARK_GRAY)
        # y += 1
        # buffer.put_string(5, y, '"The reactor performed exactly as designed."', Color.DARK_GRAY)
        # y += 1
        # buffer.put_string(5, y, '"We have always been at war with thermodynamics."', Color.DARK_GRAY)
        
        y += 2
        buffer.put_string(17, y, "ACTION ITEMS:", Color.LIGHT_YELLOW)
        y += 1
        buffer.put_string(17, y, "• Scan your dosimeter for radiation levels.", Color.DARK_GRAY)
        y += 1
        buffer.put_string(17, y, "• Your debriefing has been scheduled. Attendance is mandatory.", Color.DARK_GRAY)
        y += 1
        buffer.put_string(17, y, "• Coffee will be provided. The coffee is also mandatory.", Color.DARK_GRAY)
        # y += 1
        # buffer.put_string(5, y, "• Please do not discuss this shift with family, friends, or regulators.", Color.DARK_GRAY)

        # y += 3
        # buffer.put_string(7, y, "─" * 85, Color.GREEN)

        y += 7
        buffer.put_string(17, y, 'NÜCLEAR SOLUTIONS - "Powering Tomorrow, Today... Eventually."', Color.GREEN)
        
    
    def _render_failure(self, buffer: "TextBuffer"):
        """Render failure screen."""
        # Content area is left side (before status panel at x=100)
        content_width = 95
        center_x = content_width // 2
        
        y = 3
        
        # Failure header
        fail_text = [
            "████████████████████████████████████████████",
            "████████████████████████████████████████████",
            "████      SIGNAL LOST      ████",
            "████████████████████████████████████████████",
            "████████████████████████████████████████████",
        ]
        for i, line in enumerate(fail_text):
            if i == 2:
                buffer.put_string(center_x - len(line)//2, y + i, line, Color.WHITE, Color.RED)
            else:
                buffer.put_string(center_x - len(line)//2, y + i, line, Color.LIGHT_RED)
        
        y += 7
        buffer.put_string(5, y, "─" * 85, Color.DARK_GRAY)
        
        y += 2
        buffer.put_string(5, y, "AUTOMATED CORPORATE RESPONSE:", Color.LIGHT_RED)
        y += 1
        buffer.put_string(5, y, '"Nüclear Solutions extends its deepest condolences to the families of', Color.DARK_GRAY)
        y += 1
        buffer.put_string(5, y, '[INSERT EMPLOYEE NAME(S) HERE]. Their sacrifice will be remembered', Color.DARK_GRAY)
        y += 1
        buffer.put_string(5, y, 'at this year\'s mandatory memorial barbecue (weather permitting)."', Color.DARK_GRAY)
        
        y += 3
        buffer.put_string(5, y, "LEGAL NOTICE:", Color.LIGHT_YELLOW)
        y += 1
        buffer.put_string(5, y, "By dying on company property, you have agreed to the terms outlined in", Color.DARK_GRAY)
        y += 1
        buffer.put_string(5, y, "Form 19-C (Posthumous Liability Waiver). All personal effects have been", Color.DARK_GRAY)
        y += 1
        buffer.put_string(5, y, "confiscated for 'safety analysis.' Your final paycheck will be docked", Color.DARK_GRAY)
        y += 1
        buffer.put_string(5, y, "for uniform replacement costs.", Color.DARK_GRAY)
        
        y += 3
        buffer.put_string(5, y, "─" * 85, Color.DARK_GRAY)
        
        # y += 2
        # buffer.put_string(5, y, "Please direct all complaints to HR Director Stasia via fax.", Color.DARK_GRAY)
        # y += 1
        # buffer.put_string(5, y, "Stasia has been 'checking on something' since 1974.", Color.DARK_GRAY)
        
        y += 5
        buffer.put_string(5, y, "Resetting terminal for next shift...", Color.LIGHT_RED)
        y += 1
        buffer.put_string(5, y, "(Your replacement has already been notified. They seem nice.)", Color.DARK_GRAY)
