"""
Base module class - abstract base for all puzzle modules.
"""
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Callable, Optional, Tuple
import pygame

from src.terminal.box_drawing import draw_titled_box, DOUBLE
from src.terminal.colors import Color

if TYPE_CHECKING:
    from src.terminal.text_buffer import TextBuffer
    from src.core.game_state import GameState
    from src.audio.audio_manager import AudioManager


class BaseModule(ABC):
    """
    Abstract base class for all puzzle modules.
    Each module occupies a rectangular region on the screen.
    """
    
    def __init__(self, x: int, y: int, width: int, height: int, name: str,
                 game_state: "GameState", audio: "AudioManager" = None):
        # Position and size
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.name = name
        
        # Game state reference
        self.game_state = game_state
        
        # Audio manager reference (optional)
        self.audio = audio
        
        # Module state
        self.solved = False
        self.active = True
        
        # Callbacks
        self._on_strike: Optional[Callable[[], None]] = None
        self._on_solve: Optional[Callable[[], None]] = None
        
        # Initialize the module
        self._initialize()
        self._generate_puzzle()
    
    @abstractmethod
    def _initialize(self):
        """Initialize module-specific variables."""
        pass
    
    @abstractmethod
    def _generate_puzzle(self):
        """Generate the puzzle configuration."""
        pass
    
    @abstractmethod
    def _render_content(self, buffer: "TextBuffer"):
        """Render the module-specific content."""
        pass
    
    @abstractmethod
    def _handle_click(self, local_x: int, local_y: int) -> bool:
        """
        Handle a click at local coordinates (relative to module).
        Returns True if the click was handled.
        """
        pass
    
    def set_callbacks(self, on_strike: Callable[[], None], on_solve: Callable[[], None]):
        """Set strike and solve callbacks."""
        self._on_strike = on_strike
        self._on_solve = on_solve
    
    def strike(self):
        """Record a strike."""
        if self._on_strike:
            self._on_strike()
    
    def solve(self):
        """Mark module as solved."""
        if not self.solved:
            self.solved = True
            if self._on_solve:
                self._on_solve()
    
    def play_sound(self, sound_name: str, volume: float = None):
        """Play a sound if audio manager is available."""
        if self.audio:
            self.audio.play_sound(sound_name, volume)
    
    def contains_char(self, cx: int, cy: int) -> bool:
        """Check if character position is inside module."""
        return (self.x <= cx < self.x + self.width and
                self.y <= cy < self.y + self.height)
    
    def to_local_coords(self, cx: int, cy: int) -> Tuple[int, int]:
        """Convert global char coords to local module coords."""
        return (cx - self.x, cy - self.y)
    
    def update(self, dt: float):
        """Update module state. Override for time-based behavior."""
        pass
    
    def handle_event(self, event: pygame.event.Event, cx: int, cy: int):
        """Handle a pygame event at character position (cx, cy)."""
        if self.solved or not self.active:
            return
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.contains_char(cx, cy):
                local_x, local_y = self.to_local_coords(cx, cy)
                self._handle_click(local_x, local_y)
    
    def render(self, buffer: "TextBuffer"):
        """Render the module."""
        # Draw frame
        frame_color = Color.DARK_GRAY if self.solved else Color.GREEN
        title_color = Color.DARK_GRAY if self.solved else Color.LIGHT_CYAN
        draw_titled_box(buffer, self.x, self.y, self.width, self.height,
                       self.name, DOUBLE, frame_color, title_color)
        
        # Draw content
        self._render_content(buffer)
        
        # Draw status LED
        self._render_status_led(buffer)
    
    def _render_status_led(self, buffer: "TextBuffer"):
        """Render the solved/unsolved status LED."""
        status_y = self.y + self.height - 2
        buffer.put_string(self.x + 2, status_y, "STATUS:", Color.DARK_GRAY)
        
        if self.solved:
            buffer.put_string(self.x + 10, status_y, "[●]", Color.LIGHT_GREEN)
            buffer.put_string(self.x + 14, status_y, "NOMINAL", Color.LIGHT_GREEN)
        else:
            buffer.put_string(self.x + 10, status_y, "[○]", Color.DARK_GRAY)
