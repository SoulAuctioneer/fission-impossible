"""
Game screen - Main gameplay state with modules and reactor status.

SCREEN LAYOUT (140 cols × 45 rows)
══════════════════════════════════════════════════════════════════════════════════

    ╔══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
  0 ║                                     ████  NÜCLEAR SOLUTIONS — MAINTENANCE ROOM 7-G  ████                                                    ║
    ╠══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
    ║   ┌─────────────────────────┐    ┌─────────────────────────┐    ┌─────────────────────────┐   ║ ╔═════════════════════════════════╗   ║
    ║   │   COOLANT BYPASS        │    │   EMERGENCY OVERRIDE    │    │   VENT CODES            │   ║ ║    REACTOR STATUS               ║   ║
  3 ║   │   (28×15)               │    │   (28×15)               │    │   (28×15)               │   ║ ║    (35×30)                      ║   ║
    ║   │   x=3                   │    │   x=35                  │    │   x=67                  │   ║ ║    x=101, y=3                   ║   ║
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
 35 ║   ║                                          REACTOR EDGEWORK (139×9)                                                                  ║ ║
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
    Status:      x=101, y=3, width=41, height=31
    Edgework:    x=3, y=35, width=139, height=9
    Outer border: x=0, y=0 to x=144, y=44

MODULE POSITION FORMULA:
    x = MODULE_START_X + col * (MODULE_WIDTH + MODULE_GAP_X)
    y = MODULE_START_Y + row * (MODULE_HEIGHT + 1)
"""
import pygame
import random
from typing import TYPE_CHECKING, List, Optional, Set, Tuple

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
from src.core.settings import SETTINGS

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
        # Position: x=100 (after module grid), y=3 (aligned with modules)
        # Size: 42×31 (expanded for wider log messages)
        self.status_panel = ReactorStatusPanel(100, 3, 42, 31)
        
        # Edgework panel - bottom of screen, below module grid
        # Position: x=3 (with 2-col margin from border), y=35 (after modules end at y=33 + gap)
        # Size: 139×9 (spans most of screen width with margins)
        self.edgework_panel = EdgewWorkPanel(3, 35, 139, 9)
        
        # Modules (will be populated in enter())
        self.modules = []
        self._occupied_positions: Set[int] = set()  # Track which grid positions have modules
        
        # Timer tick tracking (for playing tick sound each second)
        self._last_tick_second: int = -1
        
        # Outer border flash state
        self._border_flash_timer = 0.0
        self._border_flash_on = True
        
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
        """Generate and initialize modules with random selection and placement."""
        self.modules = []
        
        # All 6 grid positions (2 rows x 3 cols)
        all_positions: List[Tuple[int, int]] = []
        for row in range(2):
            for col in range(3):
                x = self.MODULE_START_X + col * (self.MODULE_WIDTH + self.MODULE_GAP_X)
                y = self.MODULE_START_Y + row * (self.MODULE_HEIGHT + 1)
                all_positions.append((x, y))
        
        # All available module types
        all_module_types = [
            (CoolantValvesModule, "COOLANT BYPASS"),
            (EmergencyOverrideModule, "EMERGENCY OVERRIDE"),
            (VentCodesModule, "VENT CODES"),
            (RodAlignmentModule, "ROD ALIGNMENT"),
            (PressureLocksModule, "PRESSURE LOCKS"),
            (SecurityTerminalModule, "SECURITY TERMINAL"),
        ]
        
        # Randomly select 4 modules from the 6 available
        selected_modules = random.sample(all_module_types, 4)
        
        # Randomly select 4 positions from the 6 available
        selected_position_indices = random.sample(range(6), 4)
        
        # Track which positions have modules (for blanking plate rendering)
        self._occupied_positions: Set[int] = set(selected_position_indices)
        
        # Create modules at random positions
        for (module_class, name), pos_idx in zip(selected_modules, selected_position_indices):
            x, y = all_positions[pos_idx]
            module = module_class(
                x, y,
                self.MODULE_WIDTH, self.MODULE_HEIGHT,
                name, self.game_state, self.game.audio
            )
            module.set_callbacks(self._on_module_strike, self._on_module_solve)
            self.modules.append(module)
        
        # Update total modules count (only 4 active modules)
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
        self.game.trigger_static(duration=SETTINGS.EFFECT_STATIC_DURATION)
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
            game_state=self.game_state
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
        
        # Update flicker intensity based on strikes
        if self.game_state.strikes >= 2:
            self.game.screen_flicker.intensity = SETTINGS.EFFECT_FLICKER_2_STRIKES
        elif self.game_state.strikes >= 1:
            self.game.screen_flicker.intensity = SETTINGS.EFFECT_FLICKER_1_STRIKE
        else:
            self.game.screen_flicker.intensity = SETTINGS.EFFECT_FLICKER_0_STRIKES
        
        # Update outer border flash based on strikes and time
        time_remaining = self.game_state.time_remaining
        strikes = self.game_state.strikes
        
        # Determine flash interval - faster with more strikes or less time
        # Base interval from strikes
        if strikes >= 2:
            strike_interval = 0.5
        elif strikes >= 1:
            strike_interval = 1.0
        else:
            strike_interval = 0.0  # No flash from strikes alone
        
        # Time-based interval (overrides if faster)
        if time_remaining < 30:
            time_interval = 0.2
        elif time_remaining < 60:
            time_interval = 0.4
        elif time_remaining < 120:
            time_interval = 0.8
        else:
            time_interval = 0.0  # No flash from time alone
        
        # Use the faster of the two (smaller non-zero interval)
        if strike_interval > 0 and time_interval > 0:
            flash_interval = min(strike_interval, time_interval)
        else:
            flash_interval = strike_interval or time_interval
        
        if flash_interval > 0:
            self._border_flash_timer += dt
            if self._border_flash_timer >= flash_interval:
                self._border_flash_timer = 0.0
                self._border_flash_on = not self._border_flash_on
        else:
            self._border_flash_on = True
            self._border_flash_timer = 0.0
        
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
    
    def _get_outer_border_color(self) -> int:
        """Get outer border color based on strikes and time, with flashing."""
        strikes = self.game_state.strikes
        time_remaining = self.game_state.time_remaining
        
        # Determine base color - worst condition wins
        if strikes >= 2 or time_remaining < 60:
            bright_color = Color.LIGHT_RED
            dim_color = Color.RED
        elif strikes >= 1 or time_remaining < 120:
            bright_color = Color.LIGHT_YELLOW
            dim_color = Color.YELLOW
        else:
            # Safe state - solid green, no flash
            return Color.GREEN
        
        return bright_color if self._border_flash_on else dim_color
    
    def render(self, buffer: "TextBuffer"):
        """Render the game screen."""
        buffer.clear()
        
        # Main border - color changes based on danger level
        border_color = self._get_outer_border_color()
        draw_box(buffer, 0, 0, buffer.width, buffer.height, DOUBLE, border_color)
        
        # Header
        header = "████  NÜCLEAR SOLUTIONS - MAINTENANCE ROOM 7-G  ████"
        buffer.put_string_centered(1, header, Color.LIGHT_GREEN)
        
        # Render module grid (left side)
        self._render_modules(buffer)
        
        # Render reactor status panel (right side)
        self.status_panel.render(buffer, self.game_state)
        
        # Render edgework panel (bottom)
        self.edgework_panel.render(buffer, self.game_state)
    
    def _render_modules(self, buffer: "TextBuffer"):
        """Render the 2x3 module grid with blanking plates for empty slots."""
        # Render actual modules
        for module in self.modules:
            module.render(buffer)
        
        # Render blanking plates for empty positions
        for row in range(2):
            for col in range(3):
                idx = row * 3 + col
                if idx not in self._occupied_positions:
                    x = self.MODULE_START_X + col * (self.MODULE_WIDTH + self.MODULE_GAP_X)
                    y = self.MODULE_START_Y + row * (self.MODULE_HEIGHT + 1)
                    self._render_blanking_plate(buffer, x, y)
    
    def _render_blanking_plate(self, buffer: "TextBuffer", x: int, y: int):
        """Render a blanking plate for an empty module slot."""
        w = self.MODULE_WIDTH
        h = self.MODULE_HEIGHT
        
        # Outer border (single line, dim)
        draw_box(buffer, x, y, w, h, SINGLE, Color.DARK_GRAY)
        
        # Fill interior with subtle pattern
        for row in range(1, h - 1):
            for col in range(1, w - 1):
                # Alternating dim pattern to simulate metal plate texture
                if (row + col) % 4 == 0:
                    buffer.put_char(x + col, y + row, '·', Color.DARK_GRAY)
                elif (row + col) % 4 == 2:
                    buffer.put_char(x + col, y + row, '∙', Color.DARK_GRAY)
                else:
                    buffer.put_char(x + col, y + row, ' ', Color.BLACK)
        
        # Corner rivets
        buffer.put_char(x + 2, y + 2, 'o', Color.DARK_GRAY)
        buffer.put_char(x + w - 3, y + 2, 'o', Color.DARK_GRAY)
        buffer.put_char(x + 2, y + h - 3, 'o', Color.DARK_GRAY)
        buffer.put_char(x + w - 3, y + h - 3, 'o', Color.DARK_GRAY)
        
        # Center label
        center_y = y + h // 2
        label = "▒ NOT INSTALLED ▒"
        label_x = x + (w - len(label)) // 2
        buffer.put_string(label_x, center_y, label, Color.DARK_GRAY)
