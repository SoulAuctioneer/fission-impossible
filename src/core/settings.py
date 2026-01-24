"""
Game settings and configuration.

SCREEN DIMENSIONS & LAYOUT OVERVIEW
═══════════════════════════════════════════════════════════════════════════════

The game uses a character-based terminal display:

    COLS × ROWS = 145 × 45 characters
    CHAR_SIZE   = 8 × 16 pixels per character
    WINDOW      = 1160 × 720 pixels

Layout regions (see game_screen.py for detailed ASCII diagram):

    ┌────────────────────────────────────────────────────────────────────┐
    │  Row 0-1:   Header / Title bar                                     │
    │  Row 2:     Divider                                                │
    │  Row 3-33:  Main content area                                      │
    │             ├─ Cols 3-98:    Module grid (2×3, each 28×15 chars)   │
    │             └─ Cols 101-141: Reactor status panel (41×31 chars)    │
    │  Row 34:    Gap                                                    │
    │  Row 35-43: Edgework panel (136×9 chars)                          │
    │  Row 44:    Bottom border                                          │
    └────────────────────────────────────────────────────────────────────┘

Module grid spacing:
    - Each module: 28 wide × 15 tall
    - Horizontal gap between modules: 4 chars
    - Vertical gap between rows: 1 char
    - Module positions: x = 3 + col*(28+4), y = 3 + row*(15+1)
"""
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    """Immutable game settings."""
    
    # ═══════════════════════════════════════════════════════════════════════════
    # Terminal Dimensions (in characters)
    # ═══════════════════════════════════════════════════════════════════════════
    # These define the character grid size for the ASCII terminal display.
    # Layout depends on these values - see game_screen.py for detailed layout.
    COLS: int = 145           # Characters wide (fits 3 modules + status panel)
    ROWS: int = 45            # Characters tall (fits 2 module rows + edgework)
    
    # Character cell size (in pixels)
    # IBM VGA 8x16 font is 8 pixels wide, 16 pixels tall
    CHAR_WIDTH: int = 8
    CHAR_HEIGHT: int = 16
    
    # Calculated window size (pixels = chars × char_size)
    @property
    def WINDOW_WIDTH(self) -> int:
        return self.COLS * self.CHAR_WIDTH    # 145 * 8 = 1160 pixels
    
    @property
    def WINDOW_HEIGHT(self) -> int:
        return self.ROWS * self.CHAR_HEIGHT   # 45 * 16 = 720 pixels
    
    # Display settings
    FPS: int = 60
    TITLE: str = "Fission Impossible — Nüclear Solutions Terminal"
    FULLSCREEN: bool = True                   # Start in fullscreen (F11 to toggle)
    KIOSK_MODE: bool = False                  # Kiosk mode - prevents game exit (F12 to toggle)
    
    # Game settings
    STARTING_TIME: float = 300.0  # 5 minutes
    MAX_STRIKES: int = 3
    
    # Paths
    ASSETS_DIR: Path = Path("assets")
    FONT_PATH: Path = ASSETS_DIR / "fonts" / "PxPlus_IBM_VGA8.ttf"
    AUDIO_DIR: Path = ASSETS_DIR / "audio"
    
    # USB (future feature)
    USB_ENABLED: bool = False
    USB_BAUD_RATE: int = 115200
    
    # CRT Post-Processing Effects (pixel-level, applied to pygame Surface)
    CRT_SCANLINES: bool = True
    CRT_SCANLINE_ALPHA: int = 40          # 0-255, darkness of scanlines
    CRT_VIGNETTE: bool = True
    CRT_VIGNETTE_STRENGTH: float = 0.6    # 0.0-1.0, edge darkening intensity
    CRT_REFRESH_LINE: bool = True
    CRT_REFRESH_SPEED: float = 200.0      # pixels per second
    CRT_GLOW: bool = True
    CRT_GLOW_STRENGTH: int = 30           # 0-50, phosphor glow intensity
    CRT_INDICATOR_GLOW_STRENGTH: int = 100 # 0-100, extra glow for lit indicators (LEDs, filled gauges)
    
    # Text Buffer Effects (character-level, applied to TextBuffer)
    EFFECT_FLICKER: bool = True
    # Flicker intensity per strike count (0.0-0.1, fraction of chars to flicker)
    EFFECT_FLICKER_0_STRIKES: float = 0.0       # No flicker at 0 strikes
    EFFECT_FLICKER_1_STRIKE: float = 0.0015     # Light flicker at 1 strike
    EFFECT_FLICKER_2_STRIKES: float = 0.007    # More flicker at 2+ strikes
    EFFECT_FLICKER_FAILURE: float = 0.015      # Heavy flicker on failure screen
    EFFECT_STATIC_NOISE: bool = True
    EFFECT_STATIC_INTENSITY: float = 0.15      # 0.0-0.3, fraction of chars during static burst
    EFFECT_STATIC_DURATION: float = 0.4      # Duration of static burst on strike (seconds)
    EFFECT_TEXT_SCANLINES: bool = False        # Character-level scanlines (dims every 4th row)
    EFFECT_TEXT_SCANLINES_SPEED: float = 2.0  # Rows per second (0 = static, higher = faster scroll)


# Global settings instance
SETTINGS = Settings()
