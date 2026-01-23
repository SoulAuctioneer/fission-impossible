"""
State machine for managing game screens and transitions.
"""
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Optional
import pygame

if TYPE_CHECKING:
    from src.terminal.text_buffer import TextBuffer


class State(ABC):
    """
    Abstract base class for game states.
    Each state represents a screen or mode of the game.
    """
    
    def __init__(self, game: "Game"):
        self.game = game
    
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
        """Handle a pygame event. Override to add custom handling."""
        pass


class StateMachine:
    """
    Manages a stack of game states.
    Supports push, pop, and switch operations.
    """
    
    def __init__(self):
        self._states: list[State] = []
    
    @property
    def current(self) -> Optional[State]:
        """Get the current (top) state."""
        return self._states[-1] if self._states else None
    
    def push(self, state: State):
        """Push a new state onto the stack."""
        if self.current:
            self.current.exit()
        self._states.append(state)
        state.enter()
    
    def pop(self) -> Optional[State]:
        """Pop the current state from the stack."""
        if self._states:
            old_state = self._states.pop()
            old_state.exit()
            if self.current:
                self.current.enter()
            return old_state
        return None
    
    def switch(self, state: State):
        """Replace the current state with a new one."""
        if self._states:
            old_state = self._states.pop()
            old_state.exit()
        self._states.append(state)
        state.enter()
    
    def clear(self):
        """Remove all states from the stack."""
        while self._states:
            self._states.pop().exit()
    
    def update(self, dt: float):
        """Update the current state."""
        if self.current:
            self.current.update(dt)
    
    def render(self, buffer: "TextBuffer"):
        """Render the current state."""
        if self.current:
            self.current.render(buffer)
    
    def handle_event(self, event: pygame.event.Event):
        """Pass event to the current state."""
        if self.current:
            self.current.handle_event(event)


# Forward reference for type hints
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.core.game import Game
