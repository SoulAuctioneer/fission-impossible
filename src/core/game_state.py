"""
Game state management for tracking timer, strikes, modules, and edgework.
"""
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, List, Callable, Optional
from src.core.settings import SETTINGS


class GamePhase(Enum):
    """
    Game phases for the training-to-real-emergency progression.
    
    TRAINING: Initial state - only one module active, timer/errors hidden
    TRAINING_COMPLETE: First module solved - show congratulations modal
    EMERGENCY_WARNING: Klaxon + warning modal - dramatic transition
    REAL_GAME: Full game mode - all modules active, timer running
    """
    TRAINING = auto()
    TRAINING_COMPLETE = auto()
    EMERGENCY_WARNING = auto()
    REAL_GAME = auto()


@dataclass
class Edgework:
    """Bomb/reactor edgework information."""
    serial_number: str = "AA0AA0"
    batteries: int = 0
    has_parallel: bool = False
    indicators: Dict[str, bool] = field(default_factory=dict)
    
    def has_vowel_in_serial(self) -> bool:
        """Check if serial number contains a vowel."""
        return any(c in 'AEIOU' for c in self.serial_number)
    
    def serial_last_digit_odd(self) -> bool:
        """Check if the last digit of serial number is odd."""
        for c in reversed(self.serial_number):
            if c.isdigit():
                return int(c) % 2 == 1
        return False
    
    def serial_last_digit_even(self) -> bool:
        """Check if the last digit of serial number is even."""
        return not self.serial_last_digit_odd()
    
    def indicator_lit(self, label: str) -> bool:
        """Check if a specific indicator is lit."""
        return self.indicators.get(label, False)
    
    def indicator_unlit(self, label: str) -> bool:
        """Check if a specific indicator exists but is unlit."""
        return label in self.indicators and not self.indicators[label]


class GameState:
    """
    Central game state management.
    Tracks all runtime game data and provides signals for state changes.
    """
    
    # Real game time after emergency (4 minutes)
    REAL_GAME_TIME: float = 240.0
    
    def __init__(self):
        # Timer
        self.time_remaining: float = SETTINGS.STARTING_TIME
        self.timer_paused: bool = False
        
        # Strikes
        self.strikes: int = 0
        self.max_strikes: int = SETTINGS.MAX_STRIKES
        
        # Temperature (visual indicator)
        self.temperature: float = 0.0  # 0.0 to 1.0
        
        # Edgework
        self.edgework = Edgework()
        
        # Modules
        self.modules_total: int = 6
        self.modules_solved: int = 0
        
        # Game over state
        self.game_over: bool = False
        self.victory: bool = False
        
        # Training mode state
        self.phase: GamePhase = GamePhase.TRAINING
        self.training_module_index: int = 0  # Which module is the training module
        
        # Callbacks for state changes
        self._on_strike_callbacks: List[Callable[[int], None]] = []
        self._on_solve_callbacks: List[Callable[[int], None]] = []
        self._on_game_over_callbacks: List[Callable[[bool], None]] = []
        self._on_phase_change_callbacks: List[Callable[[GamePhase], None]] = []
    
    def reset(self):
        """Reset game state for a new game."""
        self.time_remaining = SETTINGS.STARTING_TIME
        self.timer_paused = True  # Paused during training
        self.strikes = 0
        self.temperature = 0.0
        self.modules_total = 0  # Will be set by game screen after module generation
        self.modules_solved = 0
        self.game_over = False
        self.victory = False
        self.phase = GamePhase.TRAINING
        self.training_module_index = 0
    
    def update(self, dt: float):
        """Update game state. dt is delta time in seconds."""
        if self.game_over or self.timer_paused:
            return
        
        # Update timer
        self.time_remaining -= dt
        
        # Update temperature based on time and strikes
        time_factor = 1.0 - (self.time_remaining / SETTINGS.STARTING_TIME)
        strike_factor = self.strikes * 0.1
        self.temperature = min(1.0, time_factor + strike_factor)
        
        # Check for time out
        if self.time_remaining <= 0:
            self.time_remaining = 0
            self._trigger_game_over(victory=False)
    
    def add_strike(self):
        """Add a strike and check for game over."""
        if self.game_over:
            return
        
        self.strikes += 1
        
        # Notify callbacks
        for callback in self._on_strike_callbacks:
            callback(self.strikes)
        
        # Check for game over
        if self.strikes >= self.max_strikes:
            self._trigger_game_over(victory=False)
    
    def solve_module(self):
        """Mark a module as solved and check for victory."""
        if self.game_over:
            return
        
        self.modules_solved += 1
        
        # Notify callbacks
        for callback in self._on_solve_callbacks:
            callback(self.modules_solved)
        
        # Check for victory
        if self.modules_solved >= self.modules_total:
            self._trigger_game_over(victory=True)
    
    def _trigger_game_over(self, victory: bool):
        """Trigger game over state."""
        self.game_over = True
        self.victory = victory
        
        # Notify callbacks
        for callback in self._on_game_over_callbacks:
            callback(victory)
    
    def on_strike(self, callback: Callable[[int], None]):
        """Register callback for strike events."""
        self._on_strike_callbacks.append(callback)
    
    def on_solve(self, callback: Callable[[int], None]):
        """Register callback for module solve events."""
        self._on_solve_callbacks.append(callback)
    
    def on_game_over(self, callback: Callable[[bool], None]):
        """Register callback for game over events."""
        self._on_game_over_callbacks.append(callback)
    
    def on_phase_change(self, callback: Callable[["GamePhase"], None]):
        """Register callback for phase change events."""
        self._on_phase_change_callbacks.append(callback)
    
    def set_phase(self, new_phase: "GamePhase"):
        """Change the game phase and notify callbacks."""
        if self.phase != new_phase:
            self.phase = new_phase
            for callback in self._on_phase_change_callbacks:
                callback(new_phase)
    
    def start_real_game(self):
        """Transition from training to real game mode."""
        self.phase = GamePhase.REAL_GAME
        self.time_remaining = self.REAL_GAME_TIME  # 3 minutes
        self.timer_paused = False
        self.strikes = 0  # Reset strikes for real game
        # Notify phase change
        for callback in self._on_phase_change_callbacks:
            callback(self.phase)
    
    @property
    def is_training(self) -> bool:
        """Check if we're in any training phase (not real game)."""
        return self.phase != GamePhase.REAL_GAME
    
    @property
    def show_timer_and_errors(self) -> bool:
        """Whether to show timer and error indicators."""
        return self.phase == GamePhase.REAL_GAME
    
    @property
    def time_formatted(self) -> str:
        """Get time remaining as MM:SS string."""
        mins = int(self.time_remaining) // 60
        secs = int(self.time_remaining) % 60
        return f"{mins:02d}:{secs:02d}"
    
    def timer_contains_digit(self, digit: int) -> bool:
        """Check if the timer display contains a specific digit (for button module)."""
        mins = int(self.time_remaining) // 60
        secs = int(self.time_remaining) % 60
        # Check all four digits of MM:SS display
        return (
            mins // 10 == digit or
            mins % 10 == digit or
            secs // 10 == digit or
            secs % 10 == digit
        )
