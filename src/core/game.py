"""
Main game class - manages the game loop and systems.
"""
import pygame
from typing import Optional

from src.core.settings import SETTINGS
from src.core.state_machine import StateMachine
from src.core.input import InputHandler
from src.terminal.text_buffer import TextBuffer
from src.terminal.font_renderer import FontRenderer
from src.terminal.colors import ANSI_COLORS


class Game:
    """
    Main game class that manages the game loop and all systems.
    """
    
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        
        # Create window
        self.screen = pygame.display.set_mode(
            (SETTINGS.WINDOW_WIDTH, SETTINGS.WINDOW_HEIGHT)
        )
        pygame.display.set_caption(SETTINGS.TITLE)
        
        # Create text buffer (the "terminal")
        self.buffer = TextBuffer(SETTINGS.COLS, SETTINGS.ROWS)
        
        # Create font renderer
        self.font_renderer = FontRenderer(
            SETTINGS.FONT_PATH,
            SETTINGS.CHAR_WIDTH,
            SETTINGS.CHAR_HEIGHT
        )
        
        # Create render surface
        self.render_surface = pygame.Surface(
            (SETTINGS.WINDOW_WIDTH, SETTINGS.WINDOW_HEIGHT)
        )
        
        # Systems
        self.clock = pygame.time.Clock()
        self.input = InputHandler()
        
        # State machine
        self.state_machine = StateMachine()
        
        # Game state
        self.running = True
        self._dt = 0.0
    
    def start(self):
        """Start the game with the initial state."""
        from src.states.start_screen import StartScreen
        self.state_machine.push(StartScreen(self))
    
    def run(self):
        """Main game loop."""
        self.start()
        
        while self.running:
            self._dt = self.clock.tick(SETTINGS.FPS) / 1000.0
            
            self._handle_events()
            self._update(self._dt)
            self._render()
        
        self._cleanup()
    
    def _handle_events(self):
        """Process pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
            
            # Update input handler for mouse events
            if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION):
                self.input.update()
            
            # Pass event to current state
            self.state_machine.handle_event(event)
    
    def _update(self, dt: float):
        """Update game logic."""
        self.input.update()
        self.state_machine.update(dt)
    
    def _render(self):
        """Render the current frame."""
        # Clear render surface with black
        self.render_surface.fill(ANSI_COLORS[0])
        
        # Render current state to text buffer
        self.state_machine.render(self.buffer)
        
        # Render text buffer to surface
        self.font_renderer.render(self.buffer, self.render_surface)
        
        # Blit to screen
        self.screen.blit(self.render_surface, (0, 0))
        
        pygame.display.flip()
    
    def _cleanup(self):
        """Clean up resources on exit."""
        pygame.quit()
    
    def quit(self):
        """Request game to quit."""
        self.running = False
