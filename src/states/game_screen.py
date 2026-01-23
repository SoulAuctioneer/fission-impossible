"""
Game screen - Main gameplay state with modules and reactor status.
"""
import pygame
from typing import TYPE_CHECKING, List, Optional

from src.states.base_state import BaseState
from src.terminal.box_drawing import draw_box, draw_titled_box, DOUBLE, SINGLE
from src.terminal.colors import Color
from src.core.input import pixel_to_char
from src.core.game_state import GameState
from src.utils.edgework import generate_edgework
from src.ui.reactor_status import ReactorStatusPanel
from src.modules.base_module import BaseModule
from src.modules.coolant_valves import CoolantValvesModule
from src.modules.security_terminal import SecurityTerminalModule
from src.modules.emergency_override import EmergencyOverrideModule
from src.modules.vent_codes import VentCodesModule
from src.modules.rod_alignment import RodAlignmentModule
from src.modules.pressure_locks import PressureLocksModule

if TYPE_CHECKING:
    from src.core.game import Game
    from src.terminal.text_buffer import TextBuffer


class GameScreen(BaseState):
    """
    Main gameplay screen with module grid and reactor status panel.
    """
    
    # Module grid constants
    MODULE_WIDTH = 28
    MODULE_HEIGHT = 13
    MODULE_START_X = 2
    MODULE_START_Y = 3
    MODULE_NAMES = [
        "COOLANT BYPASS", "EMERGENCY OVERRIDE",
        "VENT CODES", "ROD ALIGNMENT",
        "PRESSURE LOCKS", "SECURITY TERMINAL"
    ]
    
    def __init__(self, game: "Game"):
        super().__init__(game)
        
        # Game state
        self.game_state = GameState()
        
        # Reactor status panel
        self.status_panel = ReactorStatusPanel(89, 3, 29, 40)
        
        # Modules (will be populated in Phase 4)
        self.modules = []
        
        # Register callbacks
        self.game_state.on_game_over(self._on_game_over)
    
    def enter(self):
        """Called when entering the game screen."""
        # Reset and generate new puzzle
        self.game_state.reset()
        self.game_state.edgework = generate_edgework()
        self._generate_modules()
    
    def _generate_modules(self):
        """Generate and initialize modules."""
        self.modules = []
        
        # Module positions (2 rows x 3 cols)
        positions = []
        for row in range(2):
            for col in range(3):
                x = self.MODULE_START_X + col * (self.MODULE_WIDTH + 1)
                y = self.MODULE_START_Y + row * (self.MODULE_HEIGHT + 1)
                positions.append((x, y))
        
        # Module class mapping to positions
        module_classes = [
            (CoolantValvesModule, "COOLANT BYPASS"),       # Position 0
            (EmergencyOverrideModule, "EMERGENCY OVERRIDE"), # Position 1
            (VentCodesModule, "VENT CODES"),               # Position 2
            (RodAlignmentModule, "ROD ALIGNMENT"),         # Position 3
            (PressureLocksModule, "PRESSURE LOCKS"),       # Position 4
            (SecurityTerminalModule, "SECURITY TERMINAL"), # Position 5
        ]
        
        # Create all modules
        for idx, (module_class, name) in enumerate(module_classes):
            module = module_class(
                positions[idx][0], positions[idx][1],
                self.MODULE_WIDTH, self.MODULE_HEIGHT,
                name, self.game_state
            )
            module.set_callbacks(self._on_module_strike, self._on_module_solve)
            self.modules.append(module)
        
        # Update total modules count
        self.game_state.modules_total = len(self.modules)
    
    def _on_module_strike(self):
        """Handle module strike."""
        self.game_state.add_strike()
    
    def _on_module_solve(self):
        """Handle module solve."""
        self.game_state.solve_module()
    
    def _on_game_over(self, victory: bool):
        """Handle game over callback."""
        from src.states.end_screen import EndScreen
        self.game.state_machine.switch(EndScreen(
            self.game,
            victory=victory,
            time_remaining=self.game_state.time_remaining,
            strikes=self.game_state.strikes
        ))
    
    def update(self, dt: float):
        """Update game logic."""
        if self.game_state.game_over:
            return
        
        # Update game state
        self.game_state.update(dt)
        
        # Update status panel
        self.status_panel.update(dt, self.game_state)
        
        # Update modules
        for module in self.modules:
            module.update(dt)
    
    def handle_event(self, event: pygame.event.Event):
        """Handle input events."""
        if self.game_state.game_over:
            return
        
        # Handle module events
        if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION):
            cx, cy = pixel_to_char(*event.pos)
            
            for module in self.modules:
                module.handle_event(event, cx, cy)
    
    def render(self, buffer: "TextBuffer"):
        """Render the game screen."""
        buffer.clear()
        
        # Main border
        draw_box(buffer, 0, 0, buffer.width, buffer.height, DOUBLE, Color.GREEN)
        
        # Header
        header = "████  NUHAUS NUCLEAR — MAINTENANCE ROOM 7-G  ████"
        buffer.put_string_centered(1, header, Color.LIGHT_GREEN)
        
        # Render module grid (left side)
        self._render_modules(buffer)
        
        # Render reactor status panel (right side)
        self.status_panel.render(buffer, self.game_state)
    
    def _render_modules(self, buffer: "TextBuffer"):
        """Render the 2x3 module grid."""
        # Get positions that have actual modules
        module_positions = set()
        for module in self.modules:
            # Find which grid position this module is in
            for row in range(2):
                for col in range(3):
                    x = self.MODULE_START_X + col * (self.MODULE_WIDTH + 1)
                    y = self.MODULE_START_Y + row * (self.MODULE_HEIGHT + 1)
                    if module.x == x and module.y == y:
                        module_positions.add(row * 3 + col)
        
        # Render actual modules
        for module in self.modules:
            module.render(buffer)
        
        # Render placeholder modules for empty positions
        for row in range(2):
            for col in range(3):
                idx = row * 3 + col
                if idx not in module_positions:
                    x = self.MODULE_START_X + col * (self.MODULE_WIDTH + 1)
                    y = self.MODULE_START_Y + row * (self.MODULE_HEIGHT + 1)
                    
                    # Module frame
                    draw_titled_box(buffer, x, y, self.MODULE_WIDTH, self.MODULE_HEIGHT,
                                  self.MODULE_NAMES[idx], DOUBLE, Color.DARK_GRAY, Color.DARK_GRAY)
                    
                    # Placeholder content
                    center_y = y + self.MODULE_HEIGHT // 2
                    buffer.put_string(x + 5, center_y, "[INACTIVE]", Color.DARK_GRAY)
