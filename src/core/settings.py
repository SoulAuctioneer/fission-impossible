"""
Game settings and configuration.
"""
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    """Immutable game settings."""
    
    # Terminal dimensions (in characters)
    COLS: int = 120           # Characters wide
    ROWS: int = 45            # Characters tall
    
    # Character cell size (in pixels)
    # IBM VGA 8x16 font is 8 pixels wide, 16 pixels tall
    CHAR_WIDTH: int = 8
    CHAR_HEIGHT: int = 16
    
    # Calculated window size
    @property
    def WINDOW_WIDTH(self) -> int:
        return self.COLS * self.CHAR_WIDTH    # 1920
    
    @property
    def WINDOW_HEIGHT(self) -> int:
        return self.ROWS * self.CHAR_HEIGHT   # 720
    
    # Game settings
    FPS: int = 60
    TITLE: str = "Fission Impossible — NuHaus Nuclear Terminal"
    
    STARTING_TIME: float = 300.0  # 5 minutes
    MAX_STRIKES: int = 3
    
    # Paths
    ASSETS_DIR: Path = Path("assets")
    FONT_PATH: Path = ASSETS_DIR / "fonts" / "PxPlus_IBM_VGA8.ttf"
    AUDIO_DIR: Path = ASSETS_DIR / "audio"
    
    # USB (future feature)
    USB_ENABLED: bool = False
    USB_BAUD_RATE: int = 115200
    
    # CRT Post-Processing Effects
    CRT_SCANLINES: bool = True
    CRT_SCANLINE_ALPHA: int = 40          # 0-255, darkness of scanlines
    CRT_VIGNETTE: bool = True
    CRT_VIGNETTE_STRENGTH: float = 0.6    # 0.0-1.0, edge darkening intensity
    CRT_REFRESH_LINE: bool = True
    CRT_REFRESH_SPEED: float = 200.0      # pixels per second
    CRT_GLOW: bool = True
    CRT_GLOW_STRENGTH: int = 30           # 0-50, phosphor glow intensity


# Global settings instance
SETTINGS = Settings()
