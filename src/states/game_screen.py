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
from src.core.events import MIDI_NOTE_ON, MIDI_NOTE_OFF
from src.core.game_state import GameState, GamePhase
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
from src.modules.piano_module import PianoModule
from src.modules.resonance_chamber import ResonanceChamberModule
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
        self.modules: List[BaseModule] = []
        self._occupied_positions: Set[int] = set()  # Track which grid positions have modules
        self._disabled_positions: Set[int] = set()  # Positions with disabled (training) modules
        self._training_module_idx: int = 0  # Index in self.modules of the training module
        self._training_module_original_pos: Optional[Tuple[int, int]] = None  # Original position for restoration
        
        # Timer tick tracking (for playing tick sound each second)
        self._last_tick_second: int = -1
        
        # Outer border flash state
        self._border_flash_timer = 0.0
        self._border_flash_on = True
        
        # ═══════════════════════════════════════════════════════════════════════
        # Training Mode / Phase Transition State
        # ═══════════════════════════════════════════════════════════════════════
        self._phase_timer: float = 0.0  # Timer for phase transitions
        self._modal_flash_timer: float = 0.0  # Timer for modal border flashing
        self._modal_flash_on: bool = True
        self._screen_flash_timer: float = 0.0  # Timer for red screen flash
        self._screen_flash_active: bool = False
        self._klaxon_playing: bool = False
        
        # Training exit confirmation and inactivity timeout
        self._show_exit_training_modal: bool = False
        self._inactivity_timer: float = 0.0
        self._inactivity_timeout: float = 180.0  # 3 minutes
        
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
        
        # Reset inactivity timer
        self._inactivity_timer = 0.0
        self._show_exit_training_modal = False
        
        # Track current music state for dynamic switching
        self._current_music = None
        
        # Play initial gameplay music (calm)
        self._update_music()
    
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
            (PianoModule, "REACTOR TUNE"),
            (ResonanceChamberModule, "RESONANCE CHAMBER"),
        ]
        
        # Randomly select 4 modules from the available types
        selected_modules = random.sample(all_module_types, 4)
        
        # Randomly select 4 positions from the 6 available
        selected_position_indices = random.sample(range(6), 4)
        
        # Track which positions have modules (for blanking plate rendering)
        self._occupied_positions: Set[int] = set(selected_position_indices)
        
        # Pick one module to be the training module
        # Emergency Override requires the timer; Reactor Tune requires MIDI keyboard
        valid_training_indices = [
            i for i, (module_class, _) in enumerate(selected_modules)
            if module_class != EmergencyOverrideModule
            and (module_class != PianoModule or self.game.midi_input.is_connected)
            and (module_class != ResonanceChamberModule or self.game.midi_input.is_connected)
        ]
        self._training_module_idx = random.choice(valid_training_indices) if valid_training_indices else 0
        
        # Track disabled module positions (all except training module during training)
        self._disabled_positions: Set[int] = set()
        
        # Create modules at random positions
        for i, ((module_class, name), pos_idx) in enumerate(zip(selected_modules, selected_position_indices)):
            x, y = all_positions[pos_idx]
            module = module_class(
                x, y,
                self.MODULE_WIDTH, self.MODULE_HEIGHT,
                name, self.game_state, self.game.audio
            )
            module.set_callbacks(self._on_module_strike, self._on_module_solve)
            self.modules.append(module)
            
            # Disable all modules except the training one during training phase
            if i != self._training_module_idx:
                module.active = False
                self._disabled_positions.add(pos_idx)
        
        # During training, only 1 module counts
        # After training, all 4 will count (minus the one already solved)
        self.game_state.modules_total = 1  # Start with just training module
        self.game_state.training_module_index = self._training_module_idx
        
        # Store original position of training module and center it
        training_module = self.modules[self._training_module_idx]
        self._training_module_original_pos = (training_module.x, training_module.y)
        self._center_training_module()
    
    def _on_module_strike(self):
        """Handle module strike."""
        if self.game_state.is_training:
            # During training, play sound but don't count strike or show effects
            self.game.audio.play_sound(SFX.STRIKE, volume=0.5)
            return
        self.game_state.add_strike()
    
    def _on_module_solve(self):
        """Handle module solve."""
        self.game.audio.play_sound(SFX.MODULE_SOLVED)
        
        if self.game_state.phase == GamePhase.TRAINING:
            # Training module completed - restore position and transition to TRAINING_COMPLETE
            self._restore_training_module_position()
            self.game_state.modules_solved = 1
            self.game_state.set_phase(GamePhase.TRAINING_COMPLETE)
            self._phase_timer = 0.0
            return
        
        # Normal game - count the solve
        self.game_state.solve_module()
    
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
            game_state=self.game_state,
            status_panel=self.status_panel
        ))
    
    def update(self, dt: float):
        """Update game logic."""
        if self.game_state.game_over:
            return
        
        # Don't update game while showing exit modal
        if self._show_exit_training_modal:
            return
        
        # ═══════════════════════════════════════════════════════════════════════
        # Inactivity timeout during training phase
        # ═══════════════════════════════════════════════════════════════════════
        if self.game_state.phase == GamePhase.TRAINING:
            self._inactivity_timer += dt
            if self._inactivity_timer >= self._inactivity_timeout:
                self._return_to_start()
                return
        
        # ═══════════════════════════════════════════════════════════════════════
        # Phase-specific updates
        # ═══════════════════════════════════════════════════════════════════════
        phase = self.game_state.phase
        
        if phase == GamePhase.TRAINING_COMPLETE:
            # Show "TRAINING COMPLETE" modal for 5 seconds, then transition
            self._phase_timer += dt
            self._update_modal_flash(dt, 1.0)  # Slow flash for celebration
            
            if self._phase_timer >= 4.0:
                self._start_emergency_warning()
        
        elif phase == GamePhase.EMERGENCY_WARNING:
            # Warning modal for 7 seconds with dramatic effects
            self._phase_timer += dt
            self._update_modal_flash(dt, 0.15)  # Fast flash for urgency
            self._update_screen_flash(dt)
            
            if self._phase_timer >= 7.0:
                self._start_real_game()
        
        elif phase == GamePhase.REAL_GAME:
            # Normal game updates
            self._update_real_game(dt)
        
        # Training phase has no timer updates
        
        # Update status panel (always)
        self.status_panel.update(dt, self.game_state)
        
        # Update modules (always, but some may be inactive)
        for module in self.modules:
            module.update(dt)
        
        # Update music based on current game state
        self._update_music()
    
    def _update_modal_flash(self, dt: float, interval: float):
        """Update modal border flash timer."""
        self._modal_flash_timer += dt
        if self._modal_flash_timer >= interval:
            self._modal_flash_timer = 0.0
            self._modal_flash_on = not self._modal_flash_on
    
    def _update_screen_flash(self, dt: float):
        """Update screen red flash effect during emergency warning."""
        self._screen_flash_timer += dt
        if self._screen_flash_timer >= 0.2:
            self._screen_flash_timer = 0.0
            self._screen_flash_active = not self._screen_flash_active
    
    def _start_emergency_warning(self):
        """Transition to emergency warning phase with dramatic effects."""
        self.game_state.set_phase(GamePhase.EMERGENCY_WARNING)
        self._phase_timer = 0.0
        self._screen_flash_active = True
        self._screen_flash_timer = 0.0
        
        # Trigger dramatic effects
        self.game.trigger_static(duration=1.5)
        self.game.audio.play_sound(SFX.EMERGENCY_KLAXON)
        self._klaxon_playing = True
        
        # Heavy flicker
        self.game.screen_flicker.intensity = SETTINGS.EFFECT_FLICKER_2_STRIKES
    
    def _center_training_module(self):
        """Center the training module on screen during training."""
        if self._training_module_original_pos is None:
            return
        training_module = self.modules[self._training_module_idx]
        # Center on screen (buffer dimensions from SETTINGS)
        from src.core.settings import SETTINGS
        centered_x = (SETTINGS.COLS - self.MODULE_WIDTH) // 2
        centered_y = (SETTINGS.ROWS - self.MODULE_HEIGHT) // 2
        training_module.x = centered_x
        training_module.y = centered_y
    
    def _restore_training_module_position(self):
        """Restore training module to its original position after training."""
        if self._training_module_original_pos is None:
            return
        training_module = self.modules[self._training_module_idx]
        training_module.x, training_module.y = self._training_module_original_pos
    
    def _start_real_game(self):
        """Transition to real game - unlock modules and start timer."""
        # Unlock disabled modules
        for module in self.modules:
            module.active = True
        self._disabled_positions.clear()
        
        # Start the real game (3 minutes, resets strikes)
        self.game_state.modules_total = len(self.modules)  # All 4 modules now count
        self.game_state.modules_solved = 1  # Training module already solved
        self.game_state.start_real_game()
        
        # Reset effects
        self._screen_flash_active = False
        self.game.screen_flicker.intensity = SETTINGS.EFFECT_FLICKER_0_STRIKES
        self._klaxon_playing = False
        
        # Initialize tick tracking
        self._last_tick_second = int(self.game_state.time_remaining)
    
    def _return_to_start(self):
        """Return to start screen (exit training)."""
        # Reset flicker to nominal (calm) state
        self.game.screen_flicker.intensity = SETTINGS.EFFECT_FLICKER_NOMINAL
        from src.states.start_screen import StartScreen
        self.game.state_machine.switch(StartScreen(self.game))
    
    def _update_music(self):
        """Update music based on current game drama level."""
        # Determine target music based on game state
        phase = self.game_state.phase
        
        if phase == GamePhase.TRAINING:
            target_music = "gameplay_calm.mp3"
        elif phase == GamePhase.TRAINING_COMPLETE:
            target_music = "gameplay_calm.mp3"
        elif phase == GamePhase.EMERGENCY_WARNING:
            target_music = "gameplay_critical.mp3"
        elif phase == GamePhase.REAL_GAME:
            # Dynamic music based on time and strikes
            time_remaining = self.game_state.time_remaining
            strikes = self.game_state.strikes
            
            # Critical: under 60 seconds OR 2+ strikes
            if time_remaining < 60 or strikes >= 2:
                target_music = "gameplay_critical.mp3"
            # Tense: under 120 seconds OR 1 strike
            elif time_remaining < 120 or strikes >= 1:
                target_music = "gameplay_tense.mp3"
            else:
                target_music = "gameplay_calm.mp3"
        else:
            target_music = "gameplay_calm.mp3"
        
        # Only change music if target is different
        if target_music != self._current_music:
            self._current_music = target_music
            self.game.audio.play_music(target_music)
    
    def _update_real_game(self, dt: float):
        """Update logic for real game phase."""
        # Update game state (timer, etc.)
        self.game_state.update(dt)
        
        # Check for timer tick (play sound each second)
        current_second = int(self.game_state.time_remaining)
        if current_second != self._last_tick_second and current_second >= 0:
            self._last_tick_second = current_second
            self.game.audio.play_sound(SFX.TIMER_TICK, volume=0.3)
        
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
        if strikes >= 2:
            strike_interval = 0.5
        elif strikes >= 1:
            strike_interval = 1.0
        else:
            strike_interval = 0.0
        
        # Time-based interval
        if time_remaining < 30:
            time_interval = 0.2
        elif time_remaining < 60:
            time_interval = 0.4
        elif time_remaining < 120:
            time_interval = 0.8
        else:
            time_interval = 0.0
        
        # Use the faster of the two
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
    
    def handle_event(self, event: pygame.event.Event):
        """Handle input events."""
        if self.game_state.game_over:
            return
        
        # Reset inactivity timer on any input during training
        if self.game_state.phase == GamePhase.TRAINING:
            if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN, pygame.MOUSEMOTION):
                self._inactivity_timer = 0.0
        
        # Handle exit confirmation modal
        if self._show_exit_training_modal:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_y, pygame.K_RETURN):
                    self._return_to_start()
                elif event.key in (pygame.K_n, pygame.K_ESCAPE):
                    self._show_exit_training_modal = False
            return
        
        # ESC key shows exit confirmation (works at any time)
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self._show_exit_training_modal = True
            return
        
        # Handle MIDI events (no mouse coords) - pass to all modules; only MIDI module reacts
        if event.type in (MIDI_NOTE_ON, MIDI_NOTE_OFF):
            if self.game_state.phase == GamePhase.TRAINING:
                training_module = self.modules[self._training_module_idx]
                training_module.handle_event(event, 0, 0)
            else:
                for module in self.modules:
                    module.handle_event(event, 0, 0)
            return

        # Handle module events (mouse)
        if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION):
            cx, cy = pixel_to_char(*event.pos)
            
            # During training, only process the training module
            if self.game_state.phase == GamePhase.TRAINING:
                training_module = self.modules[self._training_module_idx]
                training_module.handle_event(event, cx, cy)
            else:
                # Normal game - process all modules
                for module in self.modules:
                    module.handle_event(event, cx, cy)
    
    def _get_outer_border_color(self) -> int:
        """Get outer border color based on game phase, strikes, and time."""
        phase = self.game_state.phase
        
        # During training phases, use phase-appropriate colors
        if phase == GamePhase.TRAINING:
            return Color.GREEN  # Calm training mode
        elif phase == GamePhase.TRAINING_COMPLETE:
            # Celebratory flash
            return Color.LIGHT_GREEN if self._modal_flash_on else Color.GREEN
        elif phase == GamePhase.EMERGENCY_WARNING:
            # Urgent red flashing
            return Color.LIGHT_RED if self._screen_flash_active else Color.RED
        
        # Real game - normal logic
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
        
        phase = self.game_state.phase
        
        # During training, show only the training module (centered)
        if phase == GamePhase.TRAINING:
            self._render_training_only(buffer)
            return
        
        # Main border - color changes based on danger level
        border_color = self._get_outer_border_color()
        draw_box(buffer, 0, 0, buffer.width, buffer.height, DOUBLE, border_color)
        
        # Header - changes based on phase
        if phase == GamePhase.TRAINING_COMPLETE:
            header = "████  NÜCLEAR SOLUTIONS - TRAINING SIMULATION  ████"
            header_color = Color.LIGHT_CYAN
        elif phase == GamePhase.EMERGENCY_WARNING:
            header = "████  ⚠ EMERGENCY ALERT - REAL INCIDENT ⚠  ████"
            header_color = Color.LIGHT_RED if self._screen_flash_active else Color.RED
        else:
            header = "████  NÜCLEAR SOLUTIONS - MAINTENANCE ROOM 7-G  ████"
            header_color = Color.LIGHT_GREEN
        buffer.put_string_centered(1, header, header_color)
        
        # Render module grid (left side)
        self._render_modules(buffer)
        
        # Render reactor status panel (right side)
        self.status_panel.render(buffer, self.game_state)
        
        # Render edgework panel (bottom)
        self.edgework_panel.render(buffer, self.game_state)
        
        # Render phase-specific modals on top
        if phase == GamePhase.TRAINING_COMPLETE:
            self._render_training_complete_modal(buffer)
        elif phase == GamePhase.EMERGENCY_WARNING:
            self._render_emergency_warning_modal(buffer)
        
        # Render exit training confirmation modal
        if self._show_exit_training_modal:
            self._render_exit_training_modal(buffer)
    
    def _render_training_only(self, buffer: "TextBuffer"):
        """Render only the training module, centered on screen during training phase."""
        # Main border - green for training
        border_color = Color.GREEN
        draw_box(buffer, 0, 0, buffer.width, buffer.height, DOUBLE, border_color)
        
        # Simplified header
        header = "████  NÜCLEAR SOLUTIONS - TRAINING SIMULATION  ████"
        buffer.put_string_centered(1, header, Color.LIGHT_CYAN)
        
        # Render the training module (already centered in _center_training_module)
        training_module = self.modules[self._training_module_idx]
        training_module.render(buffer)
        
        # Render exit training confirmation modal if shown
        if self._show_exit_training_modal:
            self._render_exit_training_modal(buffer)
    
    def _render_modules(self, buffer: "TextBuffer"):
        """Render the 2x3 module grid with blanking plates for empty slots."""
        # Render actual modules
        for i, module in enumerate(self.modules):
            # During training phases, render disabled modules specially
            if not module.active and self.game_state.is_training:
                self._render_disabled_training_module(buffer, module)
            else:
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
    
    def _render_disabled_training_module(self, buffer: "TextBuffer", module: BaseModule):
        """Render a disabled module during training (yellow 'DISABLED FOR TRAINING' style)."""
        x, y = module.x, module.y
        w = self.MODULE_WIDTH
        h = self.MODULE_HEIGHT
        
        # Outer border (single line, yellow) - no title bar during training
        draw_box(buffer, x, y, w, h, SINGLE, Color.YELLOW)
        
        # Fill interior with subtle yellow pattern
        for row in range(1, h - 1):
            for col in range(1, w - 1):
                if (row + col) % 4 == 0:
                    buffer.put_char(x + col, y + row, '·', Color.YELLOW)
                elif (row + col) % 4 == 2:
                    buffer.put_char(x + col, y + row, '∙', Color.YELLOW)
                else:
                    buffer.put_char(x + col, y + row, ' ', Color.BLACK)
        
        # Corner rivets (yellow)
        buffer.put_char(x + 2, y + 2, 'o', Color.YELLOW)
        buffer.put_char(x + w - 3, y + 2, 'o', Color.YELLOW)
        buffer.put_char(x + 2, y + h - 3, 'o', Color.YELLOW)
        buffer.put_char(x + w - 3, y + h - 3, 'o', Color.YELLOW)
        
        # Center labels
        center_y = y + h // 2
        label1 = "▒ DISABLED ▒"
        label2 = "FOR TRAINING"
        buffer.put_string(x + (w - len(label1)) // 2, center_y - 1, label1, Color.LIGHT_YELLOW)
        buffer.put_string(x + (w - len(label2)) // 2, center_y + 1, label2, Color.YELLOW)
    
    def _render_training_complete_modal(self, buffer: "TextBuffer"):
        """Render the 'TRAINING COMPLETE' congratulations modal."""
        modal_width = 60
        modal_height = 13
        modal_x = (buffer.width - modal_width) // 2
        modal_y = (buffer.height - modal_height) // 2
        
        # Dim background
        buffer.fill_rect(modal_x - 1, modal_y - 1, modal_width + 2, modal_height + 2,
                        '░', Color.DARK_GRAY, Color.BLACK)
        
        # Clear modal interior
        buffer.fill_rect(modal_x, modal_y, modal_width, modal_height,
                        ' ', Color.LIGHT_GREEN, Color.BLACK)
        
        # Draw border (flashing green)
        border_color = Color.LIGHT_GREEN if self._modal_flash_on else Color.GREEN
        draw_box(buffer, modal_x, modal_y, modal_width, modal_height, DOUBLE, border_color)
        
        # Title
        title = " TRAINING COMPLETE "
        title_x = modal_x + (modal_width - len(title)) // 2
        buffer.put_string(title_x, modal_y, title, Color.LIGHT_GREEN)
        
        # Content
        lines = [
            "",
            "Congratulations, Recruits!",
            "",
            "You have successfully completed the",
            "mandatory safety certification exercise.",
            "",
            "Logging success, please stand by...",
        ]
        
        for i, line in enumerate(lines):
            if "Congratulations" in line:
                color = Color.LIGHT_YELLOW
            elif "Logging success" in line:
                color = Color.DARK_GRAY
            else:
                color = Color.LIGHT_GREEN
            buffer.put_string(modal_x + (modal_width - len(line)) // 2, modal_y + 2 + i, line, color)
    
    def _render_emergency_warning_modal(self, buffer: "TextBuffer"):
        """Render the emergency warning modal with dramatic red styling."""
        modal_width = 70
        modal_height = 15
        modal_x = (buffer.width - modal_width) // 2
        modal_y = (buffer.height - modal_height) // 2
        
        # Red-tinted background for urgency
        bg_char = '▓' if self._screen_flash_active else '░'
        buffer.fill_rect(modal_x - 1, modal_y - 1, modal_width + 2, modal_height + 2,
                        bg_char, Color.RED, Color.BLACK)
        
        # Clear modal interior
        buffer.fill_rect(modal_x, modal_y, modal_width, modal_height,
                        ' ', Color.LIGHT_RED, Color.BLACK)
        
        # Draw border (flashing red)
        border_color = Color.LIGHT_RED if self._modal_flash_on else Color.RED
        draw_box(buffer, modal_x, modal_y, modal_width, modal_height, DOUBLE, border_color)
        
        # Title
        title = " ⚠ EMERGENCY ALERT ⚠ "
        title_x = modal_x + (modal_width - len(title)) // 2
        buffer.put_string(title_x, modal_y, title, Color.LIGHT_RED)
        
        # Content
        lines = [
            "",
            "THIS IS NOT A DRILL",
            "",
            "MASSIVE COOLANT LEAK",
            "",
            "T-MINUS 4:00 TO MELTDOWN",
            "",
            "REPAIR ALL MODULES BEFORE MELTDOWN",
        ]
        
        for i, line in enumerate(lines):
            if "NOT A DRILL" in line or "MELTDOWN" in line:
                color = Color.LIGHT_YELLOW if self._screen_flash_active else Color.YELLOW
            elif "═" in line:
                color = Color.RED
            else:
                color = Color.LIGHT_RED if self._screen_flash_active else Color.RED
            buffer.put_string(modal_x + (modal_width - len(line)) // 2, modal_y + 2 + i, line, color)
    
    def _render_exit_training_modal(self, buffer: "TextBuffer"):
        """Render the exit/abandon shift confirmation modal."""
        modal_width = 54
        modal_height = 11
        modal_x = (buffer.width - modal_width) // 2
        modal_y = (buffer.height - modal_height) // 2
        
        # Dim background
        buffer.fill_rect(modal_x - 1, modal_y - 1, modal_width + 2, modal_height + 2,
                        '░', Color.DARK_GRAY, Color.BLACK)
        
        # Clear modal interior
        buffer.fill_rect(modal_x, modal_y, modal_width, modal_height,
                        ' ', Color.LIGHT_YELLOW, Color.BLACK)
        
        # Draw border
        draw_box(buffer, modal_x, modal_y, modal_width, modal_height, DOUBLE, Color.LIGHT_YELLOW)
        
        # Title and content change based on phase
        is_training = self.game_state.is_training
        
        title = " EXIT TRAINING " if is_training else " ABANDON SHIFT "
        title_x = modal_x + (modal_width - len(title)) // 2
        buffer.put_string(title_x, modal_y, title, Color.LIGHT_YELLOW)
        
        # Content
        if is_training:
            lines = [
                "",
                "Abandon training exercise?",
                "",
                "Your progress will not be saved.",
                "(There was no progress to save anyway.)",
                "",
                "[Y] Yes, abandon    [N] No, continue",
            ]
        else:
            lines = [
                "",
                "Abandon your shift?",
                "",
                "The reactor WILL melt down without you.",
                "(HR will be notified of your desertion.)",
                "",
                "[Y] Yes, flee    [N] No, stay",
            ]
        
        for i, line in enumerate(lines):
            if "Abandon" in line or "shift" in line:
                color = Color.LIGHT_YELLOW
            elif "[Y]" in line:
                color = Color.LIGHT_CYAN
            elif "progress" in line.lower() or "HR" in line or "melt down" in line:
                color = Color.DARK_GRAY
            else:
                color = Color.LIGHT_GREEN
            buffer.put_string(modal_x + (modal_width - len(line)) // 2, modal_y + 2 + i, line, color)
