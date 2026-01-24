"""
Settings screen - Modal overlay for game settings.
Accessible via F7 from any screen.
"""
import pygame
from typing import TYPE_CHECKING, List, Callable

from src.states.base_state import BaseState
from src.terminal.box_drawing import draw_box, DOUBLE, SINGLE
from src.terminal.colors import Color
from src.core.input import pixel_to_char
from src.audio.audio_manager import SFX

if TYPE_CHECKING:
    from src.core.game import Game
    from src.terminal.text_buffer import TextBuffer


class SettingItem:
    """Represents a single setting that can be toggled or adjusted."""
    
    def __init__(
        self,
        name: str,
        description: str,
        get_value: Callable[[], bool],
        set_value: Callable[[bool], None],
        key_hint: str = "ENTER"
    ):
        self.name = name
        self.description = description
        self.get_value = get_value
        self.set_value = set_value
        self.key_hint = key_hint
    
    @property
    def value(self) -> bool:
        return self.get_value()
    
    def toggle(self):
        self.set_value(not self.value)


class SettingsScreen(BaseState):
    """
    Settings modal overlay.
    Displays audio and visual settings that can be toggled.
    """
    
    def __init__(self, game: "Game"):
        super().__init__(game)
        
        self.selected_index = 0
        self.blink_timer = 0.0
        self.blink_state = True
        
        # Build settings list
        self.settings: List[SettingItem] = self._build_settings_list()
    
    def _build_settings_list(self) -> List[SettingItem]:
        """Build the list of configurable settings."""
        return [
            # Display settings
            SettingItem(
                name="Fullscreen",
                description="Toggle fullscreen mode (also: F10/F11)",
                get_value=lambda: self.game._fullscreen,
                set_value=lambda v: self.game._toggle_fullscreen() if v != self.game._fullscreen else None,
            ),
            SettingItem(
                name="Kiosk Mode",
                description="Prevent game exit - for public displays (also: F12)",
                get_value=lambda: self.game._kiosk_mode,
                set_value=lambda v: setattr(self.game, '_kiosk_mode', v),
            ),
            # Audio settings
            SettingItem(
                name="Music",
                description="Enable background music during gameplay",
                get_value=lambda: self.game.audio.music_enabled,
                set_value=lambda v: self.game.audio.set_music_enabled(v),
            ),
            SettingItem(
                name="Sound Effects",
                description="Enable sound effects",
                get_value=lambda: not self.game.audio.is_muted,
                set_value=lambda v: self.game.audio.set_sfx_enabled(v),
            ),
            SettingItem(
                name="Master Volume",
                description="Adjust master volume (←/→ to change)",
                get_value=lambda: self.game.audio.volume > 0,
                set_value=lambda v: None,  # Volume is adjusted with arrows
                key_hint="←/→",
            ),
            # Visual settings
            SettingItem(
                name="CRT Scanlines",
                description="Enable CRT scanline effect",
                get_value=lambda: self.game.crt_processor.scanlines_enabled,
                set_value=lambda v: setattr(self.game.crt_processor, 'scanlines_enabled', v),
            ),
            SettingItem(
                name="CRT Vignette",
                description="Enable screen edge darkening",
                get_value=lambda: self.game.crt_processor.vignette_enabled,
                set_value=lambda v: setattr(self.game.crt_processor, 'vignette_enabled', v),
            ),
            SettingItem(
                name="Screen Flicker",
                description="Enable random character flicker effect",
                get_value=lambda: self.game.screen_flicker.active,
                set_value=lambda v: setattr(self.game.screen_flicker, 'active', v),
            ),
            SettingItem(
                name="Phosphor Glow",
                description="Enable CRT phosphor glow effect",
                get_value=lambda: self.game.crt_processor.glow_enabled,
                set_value=lambda v: setattr(self.game.crt_processor, 'glow_enabled', v),
            ),
        ]
    
    def enter(self):
        """Called when settings screen opens."""
        self.game.audio.play_sound(SFX.BUTTON_CLICK)
    
    def exit(self):
        """Called when settings screen closes."""
        pass
    
    def update(self, dt: float):
        """Update settings screen."""
        # Update blink timer for cursor
        self.blink_timer += dt
        if self.blink_timer >= 0.4:
            self.blink_timer = 0.0
            self.blink_state = not self.blink_state
    
    def handle_event(self, event: pygame.event.Event):
        """Handle input events."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE or event.key == pygame.K_F7:
                # Close settings
                self.game.close_settings()
            
            elif event.key == pygame.K_UP:
                self.selected_index = (self.selected_index - 1) % len(self.settings)
                self.game.audio.play_sound(SFX.BUTTON_HOVER, volume=0.3)
            
            elif event.key == pygame.K_DOWN:
                self.selected_index = (self.selected_index + 1) % len(self.settings)
                self.game.audio.play_sound(SFX.BUTTON_HOVER, volume=0.3)
            
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                # Toggle selected setting
                setting = self.settings[self.selected_index]
                if setting.name != "Master Volume":
                    setting.toggle()
                    self.game.audio.play_sound(SFX.BUTTON_CLICK)
            
            elif event.key == pygame.K_LEFT:
                # Decrease volume
                if self.settings[self.selected_index].name == "Master Volume":
                    new_vol = max(0.0, self.game.audio.volume - 0.1)
                    self.game.audio.set_volume(new_vol)
                    self.game.audio.play_sound(SFX.BUTTON_HOVER, volume=0.5)
            
            elif event.key == pygame.K_RIGHT:
                # Increase volume
                if self.settings[self.selected_index].name == "Master Volume":
                    new_vol = min(1.0, self.game.audio.volume + 0.1)
                    self.game.audio.set_volume(new_vol)
                    self.game.audio.play_sound(SFX.BUTTON_HOVER, volume=0.5)
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                cx, cy = pixel_to_char(*event.pos)
                self._handle_click(cx, cy)
    
    def _handle_click(self, cx: int, cy: int):
        """Handle mouse click at character position."""
        # Calculate modal bounds
        modal_width = 70
        modal_height = 5 + len(self.settings) * 2 + 4
        modal_x = (self.buffer.width - modal_width) // 2
        modal_y = (self.buffer.height - modal_height) // 2
        
        # Check if click is inside modal
        if not (modal_x <= cx < modal_x + modal_width and 
                modal_y <= cy < modal_y + modal_height):
            # Click outside modal - close it
            self.game.close_settings()
            return
        
        # Check which setting was clicked
        settings_start_y = modal_y + 4
        for i, setting in enumerate(self.settings):
            item_y = settings_start_y + i * 2
            if item_y <= cy < item_y + 2:
                self.selected_index = i
                if setting.name != "Master Volume":
                    setting.toggle()
                self.game.audio.play_sound(SFX.BUTTON_CLICK)
                break
    
    def render(self, buffer: "TextBuffer"):
        """Render settings modal overlay."""
        # Note: The underlying state is rendered first by the game,
        # we just render the modal on top
        
        # Modal dimensions
        modal_width = 70
        modal_height = 5 + len(self.settings) * 2 + 4
        modal_x = (buffer.width - modal_width) // 2
        modal_y = (buffer.height - modal_height) // 2
        
        # Semi-transparent background
        buffer.fill_rect(
            modal_x - 2, modal_y - 1,
            modal_width + 4, modal_height + 2,
            '░', Color.DARK_GRAY, Color.BLACK
        )
        
        # Modal background
        buffer.fill_rect(
            modal_x, modal_y,
            modal_width, modal_height,
            ' ', Color.LIGHT_GREEN, Color.BLACK
        )
        
        # Border
        draw_box(buffer, modal_x, modal_y, modal_width, modal_height, DOUBLE, Color.LIGHT_CYAN)
        
        # Title
        title = " ⚙ SETTINGS "
        title_x = modal_x + (modal_width - len(title)) // 2
        buffer.put_string(title_x, modal_y, title, Color.LIGHT_CYAN)
        
        # Subtitle
        subtitle = "Use ↑↓ to navigate, ENTER to toggle, ESC/F7 to close"
        buffer.put_string(
            modal_x + (modal_width - len(subtitle)) // 2,
            modal_y + 2,
            subtitle,
            Color.DARK_GRAY
        )
        
        # Settings list
        settings_start_y = modal_y + 4
        
        for i, setting in enumerate(self.settings):
            y = settings_start_y + i * 2
            is_selected = (i == self.selected_index)
            
            # Selection indicator
            if is_selected:
                indicator = "▶" if self.blink_state else "▷"
                buffer.put_char(modal_x + 2, y, indicator, Color.LIGHT_YELLOW)
            
            # Setting name
            name_color = Color.LIGHT_YELLOW if is_selected else Color.LIGHT_GREEN
            buffer.put_string(modal_x + 4, y, setting.name, name_color)
            
            # Value indicator
            value_x = modal_x + modal_width - 15
            if setting.name == "Master Volume":
                # Volume bar
                vol_percent = int(self.game.audio.volume * 10)
                vol_bar = "█" * vol_percent + "░" * (10 - vol_percent)
                buffer.put_string(value_x, y, f"[{vol_bar}]", Color.LIGHT_GREEN)
            else:
                # Toggle indicator
                if setting.value:
                    buffer.put_string(value_x, y, "[●] ON ", Color.LIGHT_GREEN)
                else:
                    buffer.put_string(value_x, y, "[○] OFF", Color.DARK_GRAY)
            
            # Description (for selected item)
            if is_selected:
                desc_y = settings_start_y + len(self.settings) * 2 + 1
                buffer.put_string(
                    modal_x + 4, desc_y,
                    setting.description[:modal_width - 8],
                    Color.DARK_GRAY
                )
        
        # Footer hint
        footer_y = modal_y + modal_height - 2
        hint = "F7 or ESC to close"
        buffer.put_string(
            modal_x + (modal_width - len(hint)) // 2,
            footer_y,
            hint,
            Color.DARK_GRAY
        )
