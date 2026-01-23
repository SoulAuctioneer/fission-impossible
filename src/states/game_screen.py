"""
Game screen - Main gameplay state with modules and reactor status.

SCREEN LAYOUT (140 cols × 45 rows)
══════════════════════════════════════════════════════════════════════════════════

    ╔══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
  0 ║                                     ████  NUHAUS NUCLEAR — MAINTENANCE ROOM 7-G  ████                                                    ║
    ╠══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
    ║   ┌─────────────────────────┐    ┌─────────────────────────┐    ┌─────────────────────────┐   ║ ╔═════════════════════════════════╗   ║
    ║   │   COOLANT BYPASS        │    │   EMERGENCY OVERRIDE    │    │   VENT CODES            │   ║ ║    REACTOR STATUS               ║   ║
  3 ║   │   (28×15)               │    │   (28×15)               │    │   (28×15)               │   ║ ║    (35×30)                      ║   ║
    ║   │   x=3                   │    │   x=35                  │    │   x=67                  │   ║ ║    x=103, y=3                   ║   ║
    ║   │                         │    │                         │    │                         │   ║ ║                                 ║   ║
    ║   │                         │    │                         │    │                         │   ║ ║  - Timer                        ║   ║
    ║   │                         │    │                         │    │                         │   ║ ║  - Strikes                      ║   ║
    ║   │                         │    │                         │    │                         │   ║ ║  - Temperature                  ║   ║
    ║   │                         │    │                         │    │                         │   ║ ║  - Serial (quick ref)           ║   ║
 17 ║   └─────────────────────────┘    └─────────────────────────┘    └─────────────────────────┘   ║ ║  - Status messages               ║   ║
 18 ║   (gap row)                                                                                    ║ ║                                 ║   ║
    ║   ┌─────────────────────────┐    ┌─────────────────────────┐    ┌─────────────────────────┐   ║ ║                                 ║   ║
    ║   │   PRESSURE LOCKS        │    │   ROD ALIGNMENT         │    │   SECURITY TERMINAL     │   ║ ║                                 ║   ║
 19 ║   │   (28×15)               │    │   (28×15)               │    │   (28×15)               │   ║ ║                                 ║   ║
    ║   │   x=3, y=19             │    │   x=35, y=19            │    │   x=67, y=19            │   ║ ║                                 ║   ║
    ║   │                         │    │                         │    │                         │   ║ ║                                 ║   ║
    ║   │                         │    │                         │    │                         │   ║ ╚═════════════════════════════════╝   ║
 33 ║   └─────────────────────────┘    └─────────────────────────┘    └─────────────────────────┘   ║                                       ║
 34 ║   (gap row)                                                                                                                            ║
    ╠══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
    ║   ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗ ║
 35 ║   ║                                          REACTOR EDGEWORK (136×9)                                                                  ║ ║
    ║   ║   SERIAL NO.   │   BATTERIES         │   PARALLEL PORT      │   INDICATOR LIGHTS                                                  ║ ║
    ║   ║   ╔══════════╗ │   ┌──┬┐ ┌──┬┐ ...   │   ╔════════════════╗ │   ┌──────────────────────────────────────────────┐                  ║ ║
    ║   ║   ║  AB3·CD5 ║ │   │▓▓││ │▓▓││       │   ║ ooooooooooooo  ║ │   │ ◄●► CAR  ◄○► FRK  ◄●► SIG  ◄○► BOB           │                  ║ ║
    ║   ║   ╚══════════╝ │   └──┴┘ └──┴┘       │   ╚════════════════╝ │   └──────────────────────────────────────────────┘                  ║ ║
 43 ║   ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝ ║
 44 ╚══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝

KEY COORDINATES:
    Screen:      140 cols × 45 rows (from SETTINGS)
    Modules:     2 rows × 3 cols, each 28×15 chars
                 Row 0: y=3,  Row 1: y=19  (gap of 1 row between)
                 Col 0: x=3,  Col 1: x=35, Col 2: x=67  (gap of 4 cols between)
    Status:      x=103, y=3, width=35, height=30
    Edgework:    x=2, y=35, width=136, height=9
    Outer border: x=0, y=0 to x=139, y=44

MODULE POSITION FORMULA:
    x = MODULE_START_X + col * (MODULE_WIDTH + MODULE_GAP_X)
    y = MODULE_START_Y + row * (MODULE_HEIGHT + 1)
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
from src.ui.edgework_panel import EdgewWorkPanel
from src.modules.base_module import BaseModule
from src.modules.coolant_valves import CoolantValvesModule
from src.modules.security_terminal import SecurityTerminalModule
from src.modules.emergency_override import EmergencyOverrideModule
from src.modules.vent_codes import VentCodesModule
from src.modules.rod_alignment import RodAlignmentModule
from src.modules.pressure_locks import PressureLocksModule
from src.audio.audio_manager import SFX

if TYPE_CHECKING:
    from src.core.game import Game
    from src.terminal.text_buffer import TextBuffer


class GameScreen(BaseState):
    """
    Main gameplay screen with module grid and reactor status panel.
    See module docstring above for detailed ASCII layout diagram.
    """
    
    # ═══════════════════════════════════════════════════════════════════════════
    # Module Grid Layout Constants
    # ═══════════════════════════════════════════════════════════════════════════
    # The 6 modules are arranged in a 2×3 grid on the left side of the screen.
    # Position formula: x = START_X + col*(WIDTH+GAP_X), y = START_Y + row*(HEIGHT+1)
    MODULE_WIDTH = 28         # Each module is 28 characters wide
    MODULE_HEIGHT = 15        # Each module is 15 characters tall
    MODULE_START_X = 3        # First module column starts at x=3
    MODULE_START_Y = 3        # First module row starts at y=3
    MODULE_GAP_X = 4          # 4-character horizontal gap between modules
    # Vertical gap is 1 row (built into the position formula)
    
    # Module names in grid order (left-to-right, top-to-bottom)
    MODULE_NAMES = [
        "COOLANT BYPASS", "EMERGENCY OVERRIDE",  # Row 0: y=3
        "VENT CODES", "ROD ALIGNMENT",           # Row 0: y=3
        "PRESSURE LOCKS", "SECURITY TERMINAL"    # Row 1: y=19
    ]
    
    def __init__(self, game: "Game"):
        super().__init__(game)
        
        # Game state
        self.game_state = GameState()
        
        # ═══════════════════════════════════════════════════════════════════════
        # UI Panel Positions (see docstring for visual layout)
        # ═══════════════════════════════════════════════════════════════════════
        
        # Reactor status panel - right side of screen
        # Position: x=103 (after module grid), y=3 (aligned with modules)
        # Size: 35×30 (reduced from 40 since edgework moved to bottom)
        self.status_panel = ReactorStatusPanel(103, 3, 35, 30)
        
        # Edgework panel - bottom of screen, below module grid
        # Position: x=2 (near left edge), y=35 (after modules end at y=33 + gap)
        # Size: 136×9 (spans most of screen width)
        self.edgework_panel = EdgewWorkPanel(2, 35, 136, 9)
        
        # Modules (will be populated in Phase 4)
        self.modules = []
        
        # Timer tick tracking (for playing tick sound each second)
        self._last_tick_second: int = -1
        
        # Register callbacks
        self.game_state.on_strike(self._on_strike)
        self.game_state.on_game_over(self._on_game_over)
    
    def enter(self):
        """Called when entering the game screen."""
        # Reset and generate new puzzle
        self.game_state.reset()
        self.game_state.edgework = generate_edgework()
        self._generate_modules()
        
        # Initialize tick tracking to current second
        self._last_tick_second = int(self.game_state.time_remaining)
    
    def _generate_modules(self):
        """Generate and initialize modules."""
        self.modules = []
        
        # Module positions (2 rows x 3 cols) with horizontal gaps
        positions = []
        for row in range(2):
            for col in range(3):
                x = self.MODULE_START_X + col * (self.MODULE_WIDTH + self.MODULE_GAP_X)
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
                name, self.game_state, self.game.audio
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
        self.game.audio.play_sound(SFX.MODULE_SOLVED)
    
    def _on_strike(self, strike_count: int):
        """Handle strike callback - trigger visual and audio effects."""
        self.game.trigger_static(duration=0.35)
        self.game.audio.play_sound(SFX.STRIKE)
    
    def _on_game_over(self, victory: bool):
        """Handle game over callback."""
        # Play appropriate end sound
        if victory:
            self.game.audio.play_sound(SFX.REACTOR_STABLE)
        else:
            self.game.audio.play_sound(SFX.MELTDOWN)
        
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
        
        # Check for timer tick (play sound each second)
        current_second = int(self.game_state.time_remaining)
        if current_second != self._last_tick_second and current_second >= 0:
            self._last_tick_second = current_second
            self.game.audio.play_sound(SFX.TIMER_TICK, volume=0.3)
        
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
        
        # Render edgework panel (bottom)
        self.edgework_panel.render(buffer, self.game_state)
    
    def _render_modules(self, buffer: "TextBuffer"):
        """Render the 2x3 module grid."""
        # Get positions that have actual modules
        module_positions = set()
        for module in self.modules:
            # Find which grid position this module is in
            for row in range(2):
                for col in range(3):
                    x = self.MODULE_START_X + col * (self.MODULE_WIDTH + self.MODULE_GAP_X)
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
                    x = self.MODULE_START_X + col * (self.MODULE_WIDTH + self.MODULE_GAP_X)
                    y = self.MODULE_START_Y + row * (self.MODULE_HEIGHT + 1)
                    
                    # Module frame
                    draw_titled_box(buffer, x, y, self.MODULE_WIDTH, self.MODULE_HEIGHT,
                                  self.MODULE_NAMES[idx], DOUBLE, Color.DARK_GRAY, Color.DARK_GRAY)
                    
                    # Placeholder content
                    center_y = y + self.MODULE_HEIGHT // 2
                    buffer.put_string(x + 5, center_y, "[INACTIVE]", Color.DARK_GRAY)
