"""
Base state class for all game states.
"""
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING
import pygame

if TYPE_CHECKING:
    from src.core.game import Game
    from src.terminal.text_buffer import TextBuffer


class BaseState(ABC):
    """
    Abstract base class for game states.
    Provides common functionality for all states.
    """
    
    def __init__(self, game: "Game"):
        self.game = game
    
    @property
    def buffer(self) -> "TextBuffer":
        """Convenience access to game's text buffer."""
        return self.game.buffer
    
    def enter(self):
        """Called when this state becomes active."""
        pass
    
    def exit(self):
        """Called when this state is being left."""
        pass
    
    @abstractmethod
    def update(self, dt: float):
        """Update state logic. dt is delta time in seconds."""
        pass
    
    @abstractmethod
    def render(self, buffer: "TextBuffer"):
        """Render this state to the text buffer."""
        pass
    
    def handle_event(self, event: pygame.event.Event):
        """Handle a pygame event."""
        pass
