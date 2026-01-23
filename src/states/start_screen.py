"""
Start screen - Clock-in terminal for NuHaus Nuclear.
"""
import pygame
from typing import TYPE_CHECKING

from src.states.base_state import BaseState
from src.terminal.box_drawing import draw_box, draw_titled_box, DOUBLE, SINGLE
from src.terminal.colors import Color
from src.ui.button import ASCIIButton
from src.core.input import pixel_to_char
from src.audio.audio_manager import SFX

if TYPE_CHECKING:
    from src.core.game import Game
    from src.terminal.text_buffer import TextBuffer


class StartScreen(BaseState):
    """
    Clock-in terminal start screen.
    Displays shift briefing and CLOCK IN button.
    """
    
    def __init__(self, game: "Game"):
        super().__init__(game)
        
        # Create clock-in button (centered)
        button_width = 20
        button_x = (game.buffer.width - button_width) // 2
        self.clock_in_btn = ASCIIButton(
            x=button_x,
            y=32,
            text="[ CLOCK IN ]",
            width=button_width,
            on_click=self._on_clock_in
        )
        
        # Blink timer for cursor effect
        self.blink_timer = 0.0
        self.blink_state = True
    
    def _on_clock_in(self):
        """Handle clock-in button press."""
        self.game.audio.play_sound(SFX.CLOCK_IN)
        # Import here to avoid circular imports
        from src.states.game_screen import GameScreen
        self.game.state_machine.switch(GameScreen(self.game))
    
    def enter(self):
        """Called when entering this state."""
        pass
    
    def update(self, dt: float):
        """Update start screen."""
        # Update blink timer
        self.blink_timer += dt
        if self.blink_timer >= 0.5:
            self.blink_timer = 0.0
            self.blink_state = not self.blink_state
    
    def handle_event(self, event: pygame.event.Event):
        """Handle input events."""
        if event.type == pygame.MOUSEMOTION:
            cx, cy = pixel_to_char(*event.pos)
            was_hovered = self.clock_in_btn.hovered
            self.clock_in_btn.handle_mouse_move(cx, cy)
            # Play hover sound when entering button
            if not was_hovered and self.clock_in_btn.hovered:
                self.game.audio.play_sound(SFX.BUTTON_HOVER, volume=0.3)
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                cx, cy = pixel_to_char(*event.pos)
                if self.clock_in_btn.handle_mouse_down(cx, cy):
                    self.game.audio.play_sound(SFX.BUTTON_CLICK)
        
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                cx, cy = pixel_to_char(*event.pos)
                self.clock_in_btn.handle_mouse_up(cx, cy)
    
    def render(self, buffer: "TextBuffer"):
        """Render start screen."""
        buffer.clear()
        
        # Outer border
        draw_box(buffer, 0, 0, buffer.width, buffer.height, DOUBLE, Color.GREEN)
        
        # Header
        header = "████  NUHAUS NUCLEAR — MAINTENANCE TERMINAL v2.4.1  ████"
        buffer.put_string_centered(2, header, Color.LIGHT_GREEN)
        
        # Divider
        buffer.put_string(2, 4, "═" * (buffer.width - 4), Color.GREEN)
        
        # Shift briefing box
        box_width = 90
        box_x = (buffer.width - box_width) // 2
        draw_titled_box(buffer, box_x, 6, box_width, 22, "Ω  SHIFT BRIEFING  Ω", SINGLE, Color.GREEN, Color.LIGHT_YELLOW)
        
        # Briefing content
        content_x = box_x + 3
        briefing = [
            "",
            "        ALERT: Reactor systems experiencing anomalies.",
            "",
            "        Maintenance Room 7-G requires immediate attention.",
            "",
            "        ──────────────────────────────────────────────────────────────",
            "",
            "        TECHNICIAN: Resolve all system faults before meltdown.",
            "        HOTLINE:    Consult the Operations Manual. Guide them through.",
            "",
            "        ! DO NOT exceed 3 operational errors.",
            "        ! DO NOT allow the reactor to reach critical temperature.",
            "",
            "        ──────────────────────────────────────────────────────────────",
            "",
            "        Manual available at:  http://localhost:8080/manual",
            "",
        ]
        
        for i, line in enumerate(briefing):
            color = Color.LIGHT_YELLOW if "ALERT" in line or "! DO NOT" in line else Color.LIGHT_GREEN
            if "Manual" in line:
                color = Color.LIGHT_CYAN
            buffer.put_string(content_x, 7 + i, line, color)
        
        # Clock-in button
        self.clock_in_btn.render(buffer)
        
        # Instructions
        instruction = "Click CLOCK IN to begin your shift"
        buffer.put_string_centered(36, instruction, Color.DARK_GRAY)
        
        # Blinking cursor
        if self.blink_state:
            buffer.put_char(buffer.width // 2 + len(instruction) // 2 + 1, 36, '█', Color.LIGHT_GREEN)
        
        # Footer
        footer_y = buffer.height - 3
        buffer.put_string(2, footer_y, 'NUHAUS NUCLEAR — "We\'re Glad You\'re Expendable"', Color.DARK_GRAY)
        buffer.put_string(buffer.width - 15, footer_y, "TERMINAL 7-G", Color.DARK_GRAY)
        
        # Version and status
        buffer.put_string(2, buffer.height - 2, "ESC to quit", Color.DARK_GRAY)
        buffer.put_string(buffer.width - 25, buffer.height - 2, "STATUS: AWAITING INPUT", Color.GREEN)
