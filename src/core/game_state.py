"""
Game state management for tracking timer, strikes, modules, and edgework.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Callable, Optional
from src.core.settings import SETTINGS


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
        
        # Callbacks for state changes
        self._on_strike_callbacks: List[Callable[[int], None]] = []
        self._on_solve_callbacks: List[Callable[[int], None]] = []
        self._on_game_over_callbacks: List[Callable[[bool], None]] = []
    
    def reset(self):
        """Reset game state for a new game."""
        self.time_remaining = SETTINGS.STARTING_TIME
        self.timer_paused = False
        self.strikes = 0
        self.temperature = 0.0
        self.modules_solved = 0
        self.game_over = False
        self.victory = False
    
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
    
    @property
    def time_formatted(self) -> str:
        """Get time remaining as MM:SS string."""
        mins = int(self.time_remaining) // 60
        secs = int(self.time_remaining) % 60
        return f"{mins:02d}:{secs:02d}"
    
    @property
    def timer_digit(self) -> int:
        """Get the current ones digit of the timer (for button module)."""
        return int(self.time_remaining) % 10
