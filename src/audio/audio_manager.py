"""
Audio manager - handles sound effects and music.
"""
import pygame
from pathlib import Path
from typing import Dict, Optional

from src.core.settings import SETTINGS


class AudioManager:
    """
    Manages game audio including sound effects and music.
    """
    
    def __init__(self):
        self._initialized = False
        self._sounds: Dict[str, pygame.mixer.Sound] = {}
        self._music_playing = False
        self._muted = False
        self._volume = 0.7
        
        self._initialize()
    
    def _initialize(self):
        """Initialize audio system."""
        try:
            pygame.mixer.init()
            self._initialized = True
        except Exception as e:
            print(f"Audio initialization failed: {e}")
            self._initialized = False
    
    def load_sound(self, name: str, filename: str) -> bool:
        """Load a sound effect."""
        if not self._initialized:
            return False
        
        path = SETTINGS.AUDIO_DIR / "sfx" / filename
        if path.exists():
            try:
                self._sounds[name] = pygame.mixer.Sound(str(path))
                return True
            except Exception as e:
                print(f"Failed to load sound {filename}: {e}")
        return False
    
    def play_sound(self, name: str, volume: float = None):
        """Play a sound effect."""
        if not self._initialized or self._muted:
            return
        
        if name in self._sounds:
            sound = self._sounds[name]
            vol = volume if volume is not None else self._volume
            sound.set_volume(vol)
            sound.play()
    
    def play_music(self, filename: str, loop: bool = True):
        """Play background music."""
        if not self._initialized or self._muted:
            return
        
        path = SETTINGS.AUDIO_DIR / "music" / filename
        if path.exists():
            try:
                pygame.mixer.music.load(str(path))
                pygame.mixer.music.set_volume(self._volume * 0.5)
                pygame.mixer.music.play(-1 if loop else 0)
                self._music_playing = True
            except Exception as e:
                print(f"Failed to play music {filename}: {e}")
    
    def stop_music(self):
        """Stop background music."""
        if self._initialized and self._music_playing:
            pygame.mixer.music.stop()
            self._music_playing = False
    
    def set_volume(self, volume: float):
        """Set master volume (0.0 to 1.0)."""
        self._volume = max(0.0, min(1.0, volume))
        if self._initialized and self._music_playing:
            pygame.mixer.music.set_volume(self._volume * 0.5)
    
    def toggle_mute(self):
        """Toggle mute state."""
        self._muted = not self._muted
        if self._muted:
            pygame.mixer.music.set_volume(0)
        else:
            pygame.mixer.music.set_volume(self._volume * 0.5)
    
    @property
    def is_muted(self) -> bool:
        return self._muted
    
    def cleanup(self):
        """Clean up audio resources."""
        if self._initialized:
            pygame.mixer.quit()


# Sound effect names for consistent usage
class SFX:
    CLICK = "click"
    SUCCESS = "success"
    STRIKE = "strike"
    ALARM = "alarm"
    TIMER_TICK = "tick"
    BUTTON_HOVER = "hover"
