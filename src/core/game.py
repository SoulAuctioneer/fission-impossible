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
from src.terminal.colors import ANSI_COLORS, Color
from src.terminal.box_drawing import draw_box, DOUBLE
from src.effects.crt import CRTPostProcessor
from src.effects.flicker import ScreenFlicker, StaticNoise, ScanLines
from src.audio.audio_manager import AudioManager, SFX


class Game:
    """
    Main game class that manages the game loop and all systems.
    """
    
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        
        # Create window (native resolution, no scaling)
        self._fullscreen = SETTINGS.FULLSCREEN
        display_flags = pygame.FULLSCREEN if self._fullscreen else 0
        
        self.screen = pygame.display.set_mode(
            (SETTINGS.WINDOW_WIDTH, SETTINGS.WINDOW_HEIGHT),
            display_flags
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
        
        # CRT post-processing effects (pixel-level)
        self.crt_processor = CRTPostProcessor(
            width=SETTINGS.WINDOW_WIDTH,
            height=SETTINGS.WINDOW_HEIGHT,
            scanlines=SETTINGS.CRT_SCANLINES,
            scanline_alpha=SETTINGS.CRT_SCANLINE_ALPHA,
            vignette=SETTINGS.CRT_VIGNETTE,
            vignette_strength=SETTINGS.CRT_VIGNETTE_STRENGTH,
            refresh_line=SETTINGS.CRT_REFRESH_LINE,
            refresh_speed=SETTINGS.CRT_REFRESH_SPEED,
            glow=SETTINGS.CRT_GLOW,
            glow_strength=SETTINGS.CRT_GLOW_STRENGTH,
            indicator_glow_strength=SETTINGS.CRT_INDICATOR_GLOW_STRENGTH,
        )
        
        # Glow layer surface for lit indicators (separate from main render)
        self.glow_surface = pygame.Surface(
            (SETTINGS.WINDOW_WIDTH, SETTINGS.WINDOW_HEIGHT),
            pygame.SRCALPHA
        )
        
        # Text buffer effects (character-level)
        self.screen_flicker = ScreenFlicker(intensity=SETTINGS.EFFECT_FLICKER_0_STRIKES)
        self.screen_flicker.active = SETTINGS.EFFECT_FLICKER
        
        self.static_noise = StaticNoise(intensity=SETTINGS.EFFECT_STATIC_INTENSITY)
        # StaticNoise is trigger-based, so we just keep it ready
        # Call game.static_noise.trigger(duration) to activate it
        
        self.text_scanlines = ScanLines(
            active=SETTINGS.EFFECT_TEXT_SCANLINES,
            speed=SETTINGS.EFFECT_TEXT_SCANLINES_SPEED
        )
        
        # State machine
        self.state_machine = StateMachine()
        
        # Audio manager
        self.audio = AudioManager()
        self.audio.load_all_sounds()
        
        # Game state
        self.running = True
        self._dt = 0.0
        self._show_exit_modal = False
        self._kiosk_mode = SETTINGS.KIOSK_MODE  # Kiosk mode - prevents exit when True
    
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
                # Block window close in kiosk mode
                if not self._kiosk_mode:
                    self.running = False
            
            elif event.type == pygame.KEYDOWN:
                # F12 toggles kiosk mode (always available)
                if event.key == pygame.K_F12:
                    self._toggle_kiosk_mode()
                    continue
                
                # Handle exit confirmation modal
                if self._show_exit_modal:
                    if event.key in (pygame.K_y, pygame.K_RETURN):
                        self.running = False
                    elif event.key in (pygame.K_n, pygame.K_ESCAPE):
                        self._show_exit_modal = False
                else:
                    if event.key == pygame.K_ESCAPE:
                        # Block ESC exit dialog in kiosk mode
                        if not self._kiosk_mode:
                            self._show_exit_modal = True
                    elif event.key in (pygame.K_F11, pygame.K_F10):
                        # F11 or F10 toggles fullscreen (F10 for macOS where F11 is system shortcut)
                        self._toggle_fullscreen()
            
            # Don't pass events to state when modal is showing
            if self._show_exit_modal:
                continue
            
            # Update input handler for mouse events
            if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION):
                self.input.update()
            
            # Pass event to current state
            self.state_machine.handle_event(event)
    
    def _update(self, dt: float):
        """Update game logic."""
        self.input.update()
        self.state_machine.update(dt)
        
        # Update text buffer effects
        self.static_noise.update(dt)
        self.text_scanlines.update(dt)
    
    def _render(self):
        """Render the current frame."""
        # Clear render surface with black
        self.render_surface.fill(ANSI_COLORS[0])
        
        # Clear glow layer for lit indicators
        self.glow_surface.fill((0, 0, 0, 0))
        
        # Render current state to text buffer
        self.state_machine.render(self.buffer)
        
        # Render exit confirmation modal on top if active
        if self._show_exit_modal:
            self._render_exit_modal()
        
        # Apply text buffer effects (character-level)
        self.screen_flicker.apply(self.buffer)
        self.static_noise.apply(self.buffer)
        self.text_scanlines.apply(self.buffer)
        
        # Render text buffer to surface (also renders high-glow chars to glow_surface)
        self.font_renderer.render(self.buffer, self.render_surface, self.glow_surface)
        
        # Apply CRT post-processing effects (pixel-level), including indicator glow
        self.crt_processor.apply(self.render_surface, self._dt, self.glow_surface)
        
        # Blit to screen
        self.screen.blit(self.render_surface, (0, 0))
        
        pygame.display.flip()
    
    def _cleanup(self):
        """Clean up resources on exit."""
        self.audio.cleanup()
        pygame.quit()
    
    def quit(self):
        """Request game to quit."""
        self.running = False
    
    def trigger_static(self, duration: float = 0.15):
        """Trigger a burst of static noise (e.g., on strike/error)."""
        if SETTINGS.EFFECT_STATIC_NOISE:
            self.static_noise.trigger(duration)
    
    def _toggle_fullscreen(self):
        """Toggle between fullscreen and windowed mode."""
        self._fullscreen = not self._fullscreen
        
        display_flags = pygame.FULLSCREEN if self._fullscreen else 0
        
        self.screen = pygame.display.set_mode(
            (SETTINGS.WINDOW_WIDTH, SETTINGS.WINDOW_HEIGHT),
            display_flags
        )
    
    def _toggle_kiosk_mode(self):
        """Toggle kiosk mode (prevents game exit when enabled)."""
        self._kiosk_mode = not self._kiosk_mode
        # Play a sound to indicate the mode change
        self.audio.play_sound(SFX.BUTTON_CLICK)
    
    def _render_exit_modal(self):
        """Render the exit confirmation modal overlay."""
        # Modal dimensions
        modal_width = 50
        modal_height = 9
        modal_x = (self.buffer.width - modal_width) // 2
        modal_y = (self.buffer.height - modal_height) // 2
        
        # Dim background by filling modal area with dark background
        self.buffer.fill_rect(modal_x - 1, modal_y - 1, modal_width + 2, modal_height + 2, 
                              '░', Color.DARK_GRAY, Color.BLACK)
        
        # Clear modal interior
        self.buffer.fill_rect(modal_x, modal_y, modal_width, modal_height, 
                              ' ', Color.LIGHT_GREEN, Color.BLACK)
        
        # Draw border
        draw_box(self.buffer, modal_x, modal_y, modal_width, modal_height, 
                 DOUBLE, Color.LIGHT_YELLOW)
        
        # Title
        title = " EXIT CONFIRMATION "
        title_x = modal_x + (modal_width - len(title)) // 2
        self.buffer.put_string(title_x, modal_y, title, Color.LIGHT_YELLOW)
        
        # Message
        msg1 = "Sure you want to exit?"
        msg2 = "You probably don't!"
        self.buffer.put_string(modal_x + (modal_width - len(msg1)) // 2, modal_y + 2, 
                               msg1, Color.LIGHT_GREEN)
        self.buffer.put_string(modal_x + (modal_width - len(msg2)) // 2, modal_y + 3, 
                               msg2, Color.LIGHT_RED)
        
        # Options
        options = "[Y] Yes, abandon shift    [N] No, return"
        self.buffer.put_string(modal_x + (modal_width - len(options)) // 2, modal_y + 5, 
                               options, Color.LIGHT_CYAN)
        
        # Hint
        hint = "(ESC to cancel)"
        self.buffer.put_string(modal_x + (modal_width - len(hint)) // 2, modal_y + 7, 
                               hint, Color.DARK_GRAY)