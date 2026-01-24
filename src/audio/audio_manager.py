"""
Audio manager - handles sound effects and music with crossfade support.
"""
import pygame
from pathlib import Path
from typing import Dict, Optional, Tuple

from src.core.settings import SETTINGS


# Custom event for music end detection
MUSIC_END_EVENT = pygame.USEREVENT + 1


class AudioManager:
    """
    Manages game audio including sound effects and music.
    
    Features:
    - Sound effect playback with volume control
    - Background music with crossfade transitions
    - Music queue for playing tracks after current finishes
    - Automatic deduplication (won't restart same track)
    """
    
    # Crossfade duration in milliseconds
    CROSSFADE_MS = 500
    
    def __init__(self):
        self._initialized = False
        self._sounds: Dict[str, pygame.mixer.Sound] = {}
        self._music_playing = False
        self._muted = False
        self._music_enabled = True
        self._volume = 0.7
        
        # Music tracking
        self._current_music: Optional[str] = None
        self._current_music_looping: bool = True
        self._queued_music: Optional[Tuple[str, bool]] = None  # (filename, loop)
        
        # Crossfade state
        self._crossfade_pending: Optional[Tuple[str, bool]] = None  # (filename, loop)
        self._crossfade_timer: float = 0.0
        
        self._initialize()
    
    def _initialize(self):
        """Initialize audio system."""
        try:
            pygame.mixer.init()
            # Set up music end event for queue handling
            pygame.mixer.music.set_endevent(MUSIC_END_EVENT)
            self._initialized = True
        except Exception as e:
            print(f"Audio initialization failed: {e}")
            self._initialized = False
    
    def load_sound(self, name: str, filename: str = None) -> bool:
        """
        Load a sound effect.
        
        Args:
            name: The sound effect name (used as key for playback)
            filename: Optional filename. If not provided, uses {name}.mp3
        """
        if not self._initialized:
            return False
        
        if filename is None:
            filename = f"{name}.mp3"
        
        path = SETTINGS.AUDIO_DIR / "sfx" / filename
        if path.exists():
            try:
                self._sounds[name] = pygame.mixer.Sound(str(path))
                return True
            except Exception as e:
                print(f"Failed to load sound {filename}: {e}")
        return False
    
    def load_all_sounds(self) -> int:
        """
        Load all sound effects defined in SFX.ALL.
        
        Returns:
            Number of sounds successfully loaded.
        """
        loaded = 0
        for name in SFX.ALL:
            if self.load_sound(name):
                loaded += 1
        print(f"Loaded {loaded}/{len(SFX.ALL)} sound effects")
        return loaded
    
    def play_sound(self, name: str, volume: float = None):
        """Play a sound effect."""
        if not self._initialized or self._muted:
            return
        
        if name in self._sounds:
            sound = self._sounds[name]
            vol = volume if volume is not None else self._volume
            sound.set_volume(vol)
            sound.play()
    
    def play_music(self, filename: str, loop: bool = True, crossfade: bool = True):
        """
        Play background music.
        
        Args:
            filename: Music file to play (from assets/audio/music/)
            loop: Whether to loop the music
            crossfade: Whether to crossfade from current track
        """
        if not self._initialized or not self._music_enabled:
            return
        
        # Skip if already playing this track (and it's looping)
        if filename == self._current_music and self._music_playing and self._current_music_looping:
            return
        
        path = SETTINGS.AUDIO_DIR / "music" / filename
        if not path.exists():
            print(f"Music file not found: {filename}")
            return
        
        # Check file size - empty files will cause pygame errors
        file_size = path.stat().st_size
        if file_size < 1000:  # Less than 1KB is likely empty/corrupt
            print(f"Music file too small/empty ({file_size} bytes): {filename}")
            return
        
        # If crossfade enabled and music is playing, fade out first
        if crossfade and self._music_playing and self._current_music:
            pygame.mixer.music.fadeout(self.CROSSFADE_MS)
            self._crossfade_pending = (filename, loop)
            self._crossfade_timer = self.CROSSFADE_MS / 1000.0
        else:
            self._load_and_play_music(filename, loop)
    
    def _load_and_play_music(self, filename: str, loop: bool):
        """Internal: Load and immediately play a music file."""
        path = SETTINGS.AUDIO_DIR / "music" / filename
        
        # Verify file exists and has content
        if not path.exists():
            print(f"Music file not found: {filename}")
            return
        if path.stat().st_size < 1000:
            print(f"Music file empty/corrupt: {filename}")
            return
        
        try:
            pygame.mixer.music.load(str(path))
            pygame.mixer.music.set_volume(self._volume * 0.5)
            pygame.mixer.music.play(-1 if loop else 0)
            self._music_playing = True
            self._current_music = filename
            self._current_music_looping = loop
        except Exception as e:
            print(f"Failed to play music {filename}: {e}")
    
    def queue_music(self, filename: str, loop: bool = True):
        """
        Queue music to play after current track finishes.
        Useful for playing a stinger then returning to background music.
        
        Args:
            filename: Music file to queue
            loop: Whether to loop when it plays
        """
        self._queued_music = (filename, loop)
    
    def stop_music(self, fadeout: bool = True):
        """Stop background music."""
        if self._initialized and self._music_playing:
            if fadeout:
                pygame.mixer.music.fadeout(self.CROSSFADE_MS)
            else:
                pygame.mixer.music.stop()
            self._music_playing = False
            self._current_music = None
            self._current_music_looping = True
    
    def update(self, dt: float):
        """
        Update audio system. Call this each frame.
        Handles crossfade timing and music queue.
        """
        if not self._initialized:
            return
        
        # Handle crossfade timing
        if self._crossfade_pending:
            self._crossfade_timer -= dt
            if self._crossfade_timer <= 0:
                filename, loop = self._crossfade_pending
                self._crossfade_pending = None
                self._load_and_play_music(filename, loop)
    
    def handle_event(self, event: pygame.event.Event):
        """
        Handle pygame events. Call this for music end detection.
        """
        if event.type == MUSIC_END_EVENT:
            self._on_music_end()
    
    def _on_music_end(self):
        """Called when music finishes playing."""
        self._music_playing = False
        
        # Play queued music if any
        if self._queued_music:
            filename, loop = self._queued_music
            self._queued_music = None
            self.play_music(filename, loop, crossfade=False)
    
    @property
    def current_music(self) -> Optional[str]:
        """Get the currently playing music filename."""
        return self._current_music
    
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
    
    @property
    def music_enabled(self) -> bool:
        """Check if music is enabled."""
        return self._music_enabled
    
    @property
    def volume(self) -> float:
        """Get current master volume."""
        return self._volume
    
    def set_music_enabled(self, enabled: bool):
        """Enable or disable music."""
        self._music_enabled = enabled
        if not enabled and self._music_playing:
            self.stop_music()
    
    def set_sfx_enabled(self, enabled: bool):
        """Enable or disable sound effects."""
        self._muted = not enabled
    
    def cleanup(self):
        """Clean up audio resources."""
        if self._initialized:
            pygame.mixer.quit()


# Sound effect names for consistent usage throughout the game
class SFX:
    """
    Sound effect name constants.
    Use these instead of string literals to avoid typos.
    """
    # UI / Terminal
    BUTTON_CLICK = "button_click"
    BUTTON_HOVER = "button_hover"
    BUTTON_ERROR = "button_error"
    TERMINAL_BOOT = "terminal_boot"
    TERMINAL_HUM = "terminal_hum"
    KEYBOARD_TYPE = "keyboard_type"
    TEXT_PRINT = "text_print"
    SCREEN_STATIC = "screen_static"
    SCREEN_FLICKER = "screen_flicker"
    
    # Game State
    CLOCK_IN = "clock_in"
    MODULE_SOLVED = "module_solved"
    STRIKE = "strike"
    TIMER_TICK = "timer_tick"
    TIMER_WARNING = "timer_warning"
    TIMER_CRITICAL = "timer_critical"
    REACTOR_STABLE = "reactor_stable"
    MELTDOWN = "meltdown"
    
    # Coolant Valves Module
    WIRE_CUT = "wire_cut"
    WIRE_CORRECT = "wire_correct"
    
    # Emergency Override Module
    BUTTON_HOLD = "button_hold"
    BUTTON_RELEASE = "button_release"
    STRIP_FILL = "strip_fill"
    OVERRIDE_COMPLETE = "override_complete"
    
    # Vent Codes Module
    SYMBOL_SELECT = "symbol_select"
    CODE_SUBMIT = "code_submit"
    
    # Rod Alignment Module
    ROD_MOVE = "rod_move"
    ROD_LOCK = "rod_lock"
    SIMON_TONE_RED = "simon_tone_red"
    SIMON_TONE_BLUE = "simon_tone_blue"
    SIMON_TONE_GREEN = "simon_tone_green"
    SIMON_TONE_YELLOW = "simon_tone_yellow"
    
    # Pressure Locks Module
    GRID_MOVE = "grid_move"
    MARKER_PLACE = "marker_place"
    PATH_COMPLETE = "path_complete"
    
    # Security Terminal Module
    LETTER_SCROLL = "letter_scroll"
    LETTER_LOCK = "letter_lock"
    WORD_SUBMIT = "word_submit"
    
    # Ambient / Atmosphere
    REACTOR_HUM = "reactor_hum"
    STEAM_RELEASE = "steam_release"
    GEIGER_CLICK = "geiger_click"
    ALARM_SIREN = "alarm_siren"
    COOLANT_FLOW = "coolant_flow"
    EMERGENCY_KLAXON = "emergency_klaxon"
    
    # List of all sound effects for bulk loading
    ALL = [
        BUTTON_CLICK, BUTTON_HOVER, BUTTON_ERROR, TERMINAL_BOOT, TERMINAL_HUM,
        KEYBOARD_TYPE, TEXT_PRINT, SCREEN_STATIC, SCREEN_FLICKER,
        CLOCK_IN, MODULE_SOLVED, STRIKE, TIMER_TICK, TIMER_WARNING,
        TIMER_CRITICAL, REACTOR_STABLE, MELTDOWN,
        WIRE_CUT, WIRE_CORRECT,
        BUTTON_HOLD, BUTTON_RELEASE, STRIP_FILL, OVERRIDE_COMPLETE,
        SYMBOL_SELECT, CODE_SUBMIT,
        ROD_MOVE, ROD_LOCK, SIMON_TONE_RED, SIMON_TONE_BLUE, SIMON_TONE_GREEN, SIMON_TONE_YELLOW,
        GRID_MOVE, MARKER_PLACE, PATH_COMPLETE,
        LETTER_SCROLL, LETTER_LOCK, WORD_SUBMIT,
        REACTOR_HUM, STEAM_RELEASE, GEIGER_CLICK, ALARM_SIREN, COOLANT_FLOW,
        EMERGENCY_KLAXON,
    ]
