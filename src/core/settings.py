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


# Global settings instance
SETTINGS = Settings()
