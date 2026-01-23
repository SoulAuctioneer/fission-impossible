# Fission Impossible — Technical Architecture (Pygame)

## Overview

This document describes an alternative architecture using **Pygame** (specifically **pygame-ce**, the community edition) as the game framework. This approach trades Godot's visual editor and built-in features for Python's simplicity and native serial port access.

---

## Requirements Analysis

### Core Requirements
| Requirement | Pygame Solution |
|-------------|-----------------|
| 2D retro pixel graphics | Native surface rendering with integer scaling |
| Cross-platform dev/deploy | Python + Pygame works on MacOS and Windows |
| USB microcontroller support | Native `pyserial` — no bridge process needed |
| Party game performance | Pygame-ce is performant, 60fps easily achievable |
| AI-generated assets | Direct PNG/WAV import |
| Quick iteration | Python is fast to modify, no compilation |

### Advantages of Pygame Approach
| Advantage | Details |
|-----------|---------|
| **Native USB serial** | `pyserial` is a first-class Python library — no bridge needed |
| **Single codebase** | Game + USB in one Python process |
| **Python ecosystem** | Access to numpy, PIL, etc. for asset processing |
| **Simplicity** | No engine abstractions, direct control over everything |
| **Familiar language** | Python is widely known |

### Disadvantages
| Disadvantage | Mitigation |
|--------------|------------|
| No visual editor | Good code organization, hot-reload for iteration |
| No built-in shaders | Software CRT effects or optional OpenGL |
| Distribution complexity | PyInstaller with careful setup |
| Manual scene management | Implement lightweight state machine |

---

## Technology Stack

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           TECHNOLOGY STACK                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   CORE                        LIBRARIES                    TOOLS            │
│   ════                        ═════════                    ═════            │
│                                                                             │
│   Python 3.11+                pygame-ce 2.x                PyInstaller      │
│   └── Main language           └── Game framework           └── Distribution │
│                                                                             │
│                               pyserial                     Pillow           │
│                               └── USB/Serial               └── Asset proc   │
│                                                                             │
│                               numpy (optional)             pytest           │
│                               └── Array operations         └── Testing      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Why pygame-ce?

**pygame-ce** (Community Edition) is a maintained fork of pygame with:
- Better performance
- More features (better scaling, blend modes)
- Active development
- Drop-in replacement for pygame

```bash
pip install pygame-ce
```

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           FISSION IMPOSSIBLE                                │
│                           (Single Python Process)                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │                           MAIN GAME LOOP                              │ │
│  │                                                                       │ │
│  │   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐             │ │
│  │   │   INPUT     │    │   UPDATE    │    │   RENDER    │             │ │
│  │   │             │    │             │    │             │             │ │
│  │   │ • Keyboard  │───►│ • Game      │───►│ • Surfaces  │────► Screen │ │
│  │   │ • Mouse     │    │   State     │    │ • Sprites   │             │ │
│  │   │ • USB       │    │ • Modules   │    │ • Effects   │             │ │
│  │   │   Serial    │    │ • Timer     │    │ • UI        │             │ │
│  │   └─────────────┘    └─────────────┘    └─────────────┘             │ │
│  │                                                                       │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                         STATE MACHINE                                │   │
│  │                                                                      │   │
│  │  ┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐  │   │
│  │  │  START   │────►│   GAME   │────►│   END    │────►│  START   │  │   │
│  │  │  SCREEN  │     │  SCREEN  │     │  SCREEN  │     │  SCREEN  │  │   │
│  │  └──────────┘     └──────────┘     └──────────┘     └──────────┘  │   │
│  │                                                                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │                            MODULES                                    │ │
│  │                                                                       │ │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │ │
│  │  │ Coolant  │ │Emergency │ │  Vent    │ │   Rod    │ │ Pressure │  │ │
│  │  │  Valves  │ │ Override │ │  Codes   │ │Alignment │ │  Locks   │  │ │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘  │ │
│  │                     ┌──────────┐                                     │ │
│  │                     │ Security │                                     │ │
│  │                     │ Terminal │                                     │ │
│  │                     └──────────┘                                     │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │                         USB SERIAL (Native)                           │ │
│  │                                                                       │ │
│  │   ┌────────────────┐    ┌────────────────┐    ┌────────────────┐    │ │
│  │   │  SerialManager │    │   Protocol     │    │   Device       │    │ │
│  │   │                │◄──►│   Handler      │◄──►│   Abstraction  │    │ │
│  │   │  (pyserial)    │    │   (JSON)       │    │                │    │ │
│  │   └────────────────┘    └────────────────┘    └───────┬────────┘    │ │
│  │                                                        │             │ │
│  └────────────────────────────────────────────────────────│─────────────┘ │
│                                                           │               │
│                                                      USB Serial           │
│                                                           │               │
│  ┌────────────────────────────────────────────────────────▼─────────────┐ │
│  │                    MICROCONTROLLER (Future)                          │ │
│  │                    ESP32 / Teensy / Arduino                          │ │
│  └──────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Project Structure

```
fission-impossible/
├── main.py                      # Entry point
├── requirements.txt             # Python dependencies
├── pyproject.toml              # Project metadata
│
├── src/
│   ├── __init__.py
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── game.py              # Main game class, loop
│   │   ├── settings.py          # Constants, configuration
│   │   ├── state_machine.py     # Scene/state management
│   │   └── events.py            # Custom event definitions
│   │
│   ├── states/
│   │   ├── __init__.py
│   │   ├── base_state.py        # Abstract base state
│   │   ├── start_screen.py      # Clock-in terminal
│   │   ├── game_screen.py       # Main control panel
│   │   └── end_screen.py        # Win/lose screens
│   │
│   ├── modules/
│   │   ├── __init__.py
│   │   ├── base_module.py       # Abstract base module
│   │   ├── coolant_valves.py
│   │   ├── emergency_override.py
│   │   ├── vent_codes.py
│   │   ├── rod_alignment.py
│   │   ├── pressure_locks.py
│   │   └── security_terminal.py
│   │
│   ├── components/
│   │   ├── __init__.py
│   │   ├── timer_display.py     # Countdown timer widget
│   │   ├── strike_indicator.py  # Error lights
│   │   ├── status_panel.py      # Reactor status
│   │   └── button.py            # Clickable button component
│   │
│   ├── graphics/
│   │   ├── __init__.py
│   │   ├── sprite_sheet.py      # Sprite sheet handling
│   │   ├── animation.py         # Animation system
│   │   ├── effects.py           # CRT, scanlines, glow
│   │   └── text.py              # Pixel font rendering
│   │
│   ├── audio/
│   │   ├── __init__.py
│   │   └── audio_manager.py     # Sound effect management
│   │
│   ├── usb/
│   │   ├── __init__.py
│   │   ├── serial_manager.py    # Serial port handling
│   │   ├── protocol.py          # Message protocol
│   │   └── devices.py           # Device abstractions
│   │
│   └── utils/
│       ├── __init__.py
│       ├── edgework.py          # Generate serial, batteries, etc.
│       └── helpers.py           # Utility functions
│
├── assets/
│   ├── sprites/
│   │   ├── ui/
│   │   ├── modules/
│   │   └── effects/
│   ├── audio/
│   │   ├── sfx/
│   │   └── music/
│   └── fonts/
│
├── docs/
│   ├── GAME_REFERENCE.md
│   ├── THEME.md
│   ├── DESIGN.md
│   └── ARCHITECTURE_PYGAME.md
│
└── tools/
    ├── build.py                 # PyInstaller build script
    └── asset_processor.py       # AI asset post-processing
```

---

## Core Implementation

### Main Entry Point

```python
# main.py
import pygame
from src.core.game import Game
from src.core.settings import Settings

def main():
    pygame.init()
    pygame.mixer.init()
    
    game = Game()
    game.run()
    
    pygame.quit()

if __name__ == "__main__":
    main()
```

### Settings / Configuration

```python
# src/core/settings.py
from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class Settings:
    # Display
    INTERNAL_WIDTH: int = 640      # Pixel art resolution
    INTERNAL_HEIGHT: int = 360
    SCALE: int = 3                  # 640x360 * 3 = 1920x1080
    WINDOW_WIDTH: int = INTERNAL_WIDTH * SCALE
    WINDOW_HEIGHT: int = INTERNAL_HEIGHT * SCALE
    FPS: int = 60
    TITLE: str = "Fission Impossible — NuHaus Nuclear"
    
    # Game settings
    STARTING_TIME: float = 300.0   # 5 minutes
    MAX_STRIKES: int = 3
    TIME_PENALTY: float = 0.9      # Timer speeds up 10% per strike
    MODULE_COUNT: int = 6
    END_SCREEN_DURATION: float = 5.0
    
    # Paths
    ASSETS_DIR: Path = Path("assets")
    SPRITES_DIR: Path = ASSETS_DIR / "sprites"
    AUDIO_DIR: Path = ASSETS_DIR / "audio"
    FONTS_DIR: Path = ASSETS_DIR / "fonts"
    
    # Colors (retro CRT palette)
    COLOR_BG: tuple = (20, 25, 20)
    COLOR_GREEN: tuple = (0, 255, 100)
    COLOR_AMBER: tuple = (255, 176, 0)
    COLOR_RED: tuple = (255, 50, 50)
    COLOR_PANEL: tuple = (45, 55, 45)
    
    # USB (future)
    USB_ENABLED: bool = False
    USB_BAUD_RATE: int = 115200

SETTINGS = Settings()
```

### Main Game Class

```python
# src/core/game.py
import pygame
from src.core.settings import SETTINGS
from src.core.state_machine import StateMachine
from src.states.start_screen import StartScreen
from src.graphics.effects import CRTEffect
from src.audio.audio_manager import AudioManager
from src.usb.serial_manager import SerialManager

class Game:
    def __init__(self):
        # Create the actual window at scaled resolution
        self.screen = pygame.display.set_mode(
            (SETTINGS.WINDOW_WIDTH, SETTINGS.WINDOW_HEIGHT)
        )
        pygame.display.set_caption(SETTINGS.TITLE)
        
        # Internal render surface (pixel art resolution)
        self.render_surface = pygame.Surface(
            (SETTINGS.INTERNAL_WIDTH, SETTINGS.INTERNAL_HEIGHT)
        )
        
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Systems
        self.audio = AudioManager()
        self.crt_effect = CRTEffect()
        self.serial = SerialManager() if SETTINGS.USB_ENABLED else None
        
        # State machine
        self.state_machine = StateMachine()
        self.state_machine.push(StartScreen(self))
    
    def run(self):
        while self.running:
            dt = self.clock.tick(SETTINGS.FPS) / 1000.0
            
            self._handle_events()
            self._update(dt)
            self._render()
    
    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            # Pass to current state
            self.state_machine.handle_event(event)
            
            # Handle USB events if enabled
            if self.serial:
                self.serial.process_events()
    
    def _update(self, dt: float):
        self.state_machine.update(dt)
        
        # Poll USB serial
        if self.serial:
            self.serial.update()
    
    def _render(self):
        # Clear internal surface
        self.render_surface.fill(SETTINGS.COLOR_BG)
        
        # Render current state to internal surface
        self.state_machine.render(self.render_surface)
        
        # Apply CRT effect and scale up
        final_surface = self.crt_effect.apply(self.render_surface)
        
        # Scale to window (nearest neighbor for pixel-perfect)
        scaled = pygame.transform.scale(
            final_surface, 
            (SETTINGS.WINDOW_WIDTH, SETTINGS.WINDOW_HEIGHT)
        )
        
        # Blit to screen
        self.screen.blit(scaled, (0, 0))
        pygame.display.flip()
    
    def quit(self):
        self.running = False
```

### State Machine

```python
# src/core/state_machine.py
from typing import Optional
from abc import ABC, abstractmethod
import pygame

class State(ABC):
    def __init__(self, game):
        self.game = game
    
    @abstractmethod
    def enter(self):
        """Called when state becomes active."""
        pass
    
    @abstractmethod
    def exit(self):
        """Called when state is removed."""
        pass
    
    @abstractmethod
    def handle_event(self, event: pygame.event.Event):
        """Handle pygame events."""
        pass
    
    @abstractmethod
    def update(self, dt: float):
        """Update game logic."""
        pass
    
    @abstractmethod
    def render(self, surface: pygame.Surface):
        """Render to surface."""
        pass


class StateMachine:
    def __init__(self):
        self._states: list[State] = []
    
    @property
    def current(self) -> Optional[State]:
        return self._states[-1] if self._states else None
    
    def push(self, state: State):
        """Push new state onto stack."""
        if self.current:
            self.current.exit()
        self._states.append(state)
        state.enter()
    
    def pop(self):
        """Remove current state."""
        if self.current:
            self.current.exit()
            self._states.pop()
        if self.current:
            self.current.enter()
    
    def switch(self, state: State):
        """Replace current state."""
        if self.current:
            self.current.exit()
            self._states.pop()
        self._states.append(state)
        state.enter()
    
    def handle_event(self, event: pygame.event.Event):
        if self.current:
            self.current.handle_event(event)
    
    def update(self, dt: float):
        if self.current:
            self.current.update(dt)
    
    def render(self, surface: pygame.Surface):
        if self.current:
            self.current.render(surface)
```

---

## Module System

### Base Module Class

```python
# src/modules/base_module.py
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum, auto
import pygame

class ModuleStatus(Enum):
    ACTIVE = auto()
    SOLVED = auto()
    DISABLED = auto()

@dataclass
class ModuleResult:
    correct: bool
    message: str = ""

class BaseModule(ABC):
    """Abstract base class for all game modules."""
    
    def __init__(self, rect: pygame.Rect, game_state):
        self.rect = rect
        self.game_state = game_state
        self.status = ModuleStatus.ACTIVE
        self.name = "Unknown Module"
        self.solved_text = "COMPLETE"
        
        # Visual elements
        self.surface = pygame.Surface((rect.width, rect.height))
        self.led_color = (100, 100, 100)  # Gray = unsolved
        
        self._initialize()
        self._generate_puzzle()
    
    @abstractmethod
    def _initialize(self):
        """Set up module-specific properties."""
        pass
    
    @abstractmethod
    def _generate_puzzle(self):
        """Generate random puzzle state."""
        pass
    
    @abstractmethod
    def _check_solution(self, action: dict) -> ModuleResult:
        """Check if an action solves or strikes."""
        pass
    
    @abstractmethod
    def _render_module(self, surface: pygame.Surface):
        """Render module-specific content."""
        pass
    
    def handle_event(self, event: pygame.event.Event) -> Optional[ModuleResult]:
        """Handle input events. Returns result if action taken."""
        if self.status != ModuleStatus.ACTIVE:
            return None
        
        # Convert screen coords to module-local coords
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                local_pos = (
                    event.pos[0] - self.rect.x,
                    event.pos[1] - self.rect.y
                )
                return self._handle_click(local_pos)
        
        return None
    
    @abstractmethod
    def _handle_click(self, pos: tuple[int, int]) -> Optional[ModuleResult]:
        """Handle click at module-local coordinates."""
        pass
    
    def mark_solved(self):
        """Mark module as solved."""
        self.status = ModuleStatus.SOLVED
        self.led_color = (0, 255, 100)  # Green
    
    def update(self, dt: float):
        """Update module state (for animations, etc.)."""
        pass
    
    def render(self, target_surface: pygame.Surface):
        """Render module to target surface."""
        # Clear module surface
        self.surface.fill((45, 55, 45))
        
        # Draw frame
        pygame.draw.rect(
            self.surface, 
            (80, 90, 80), 
            (0, 0, self.rect.width, self.rect.height), 
            3
        )
        
        # Draw LED indicator
        pygame.draw.circle(
            self.surface,
            self.led_color,
            (self.rect.width - 15, 15),
            8
        )
        
        # Render module-specific content
        self._render_module(self.surface)
        
        # Blit to target
        target_surface.blit(self.surface, self.rect.topleft)
```

### Example Module: Coolant Valves

```python
# src/modules/coolant_valves.py
import pygame
import random
from src.modules.base_module import BaseModule, ModuleResult, ModuleStatus

class CoolantValves(BaseModule):
    COLORS = ["red", "blue", "yellow", "white", "black"]
    COLOR_MAP = {
        "red": (220, 60, 60),
        "blue": (60, 100, 220),
        "yellow": (220, 200, 60),
        "white": (220, 220, 220),
        "black": (40, 40, 40),
    }
    
    def _initialize(self):
        self.name = "Coolant Valves"
        self.solved_text = "FLOW NOMINAL"
        self.wire_count = 0
        self.wire_colors: list[str] = []
        self.correct_wire = 0
        self.cut_wires: set[int] = set()
        
        # Visual layout
        self.wire_rects: list[pygame.Rect] = []
    
    def _generate_puzzle(self):
        # Random 3-6 wires
        self.wire_count = random.randint(3, 6)
        self.wire_colors = [random.choice(self.COLORS) for _ in range(self.wire_count)]
        self.correct_wire = self._calculate_correct_wire()
        self.cut_wires = set()
        
        # Create clickable areas for wires
        wire_height = 30
        wire_spacing = 10
        start_y = 50
        
        self.wire_rects = []
        for i in range(self.wire_count):
            rect = pygame.Rect(
                20,
                start_y + i * (wire_height + wire_spacing),
                self.rect.width - 40,
                wire_height
            )
            self.wire_rects.append(rect)
    
    def _calculate_correct_wire(self) -> int:
        serial = self.game_state.edgework["serial_number"]
        last_digit = int(serial[-1])
        last_digit_odd = last_digit % 2 == 1
        
        colors = self.wire_colors
        
        if self.wire_count == 3:
            if "red" not in colors:
                return 1  # Second wire
            elif colors[-1] == "white":
                return self.wire_count - 1
            elif colors.count("blue") > 1:
                return self._last_index_of("blue")
            else:
                return self.wire_count - 1
        
        elif self.wire_count == 4:
            if colors.count("red") > 1 and last_digit_odd:
                return self._last_index_of("red")
            elif colors[-1] == "yellow" and "red" not in colors:
                return 0
            elif colors.count("blue") == 1:
                return 0
            elif colors.count("yellow") > 1:
                return self.wire_count - 1
            else:
                return 1
        
        elif self.wire_count == 5:
            if colors[-1] == "black" and last_digit_odd:
                return 3
            elif colors.count("red") == 1 and colors.count("yellow") > 1:
                return 0
            elif "black" not in colors:
                return 1
            else:
                return 0
        
        elif self.wire_count == 6:
            if "yellow" not in colors and last_digit_odd:
                return 2
            elif colors.count("yellow") == 1 and colors.count("white") > 1:
                return 3
            elif "red" not in colors:
                return self.wire_count - 1
            else:
                return 3
        
        return 0
    
    def _last_index_of(self, color: str) -> int:
        for i in range(len(self.wire_colors) - 1, -1, -1):
            if self.wire_colors[i] == color:
                return i
        return 0
    
    def _handle_click(self, pos: tuple[int, int]) -> Optional[ModuleResult]:
        for i, rect in enumerate(self.wire_rects):
            if rect.collidepoint(pos) and i not in self.cut_wires:
                self.cut_wires.add(i)
                
                if i == self.correct_wire:
                    self.mark_solved()
                    return ModuleResult(correct=True, message="Valve closed correctly")
                else:
                    return ModuleResult(correct=False, message="Wrong valve!")
        
        return None
    
    def _render_module(self, surface: pygame.Surface):
        # Title
        font = pygame.font.Font(None, 20)
        title = font.render("COOLANT BYPASS", True, (0, 200, 100))
        surface.blit(title, (10, 10))
        
        # Draw wires
        for i, (rect, color) in enumerate(zip(self.wire_rects, self.wire_colors)):
            wire_color = self.COLOR_MAP[color]
            
            if i in self.cut_wires:
                # Draw cut wire (two segments with gap)
                mid_x = rect.centerx
                pygame.draw.line(
                    surface, wire_color,
                    (rect.left, rect.centery),
                    (mid_x - 10, rect.centery),
                    8
                )
                pygame.draw.line(
                    surface, wire_color,
                    (mid_x + 10, rect.centery),
                    (rect.right, rect.centery),
                    8
                )
            else:
                # Draw intact wire
                pygame.draw.line(
                    surface, wire_color,
                    (rect.left, rect.centery),
                    (rect.right, rect.centery),
                    8
                )
                
                # Wire connectors
                pygame.draw.circle(surface, (100, 100, 100), (rect.left, rect.centery), 10)
                pygame.draw.circle(surface, (100, 100, 100), (rect.right, rect.centery), 10)
```

---

## Graphics & Effects

### CRT Effect (Software Rendering)

```python
# src/graphics/effects.py
import pygame
import math
import random

class CRTEffect:
    """Software-based CRT screen effect."""
    
    def __init__(self):
        self.scanline_surface = None
        self.vignette_surface = None
        self.time = 0
        
    def apply(self, surface: pygame.Surface) -> pygame.Surface:
        """Apply CRT effects to surface."""
        width, height = surface.get_size()
        
        # Create output surface
        output = surface.copy()
        
        # Apply scanlines
        self._apply_scanlines(output)
        
        # Apply vignette
        self._apply_vignette(output)
        
        # Apply noise (subtle)
        self._apply_noise(output)
        
        self.time += 1
        
        return output
    
    def _apply_scanlines(self, surface: pygame.Surface):
        """Draw horizontal scanlines."""
        width, height = surface.get_size()
        
        # Create scanline overlay if not exists or size changed
        if (self.scanline_surface is None or 
            self.scanline_surface.get_size() != (width, height)):
            self.scanline_surface = pygame.Surface((width, height), pygame.SRCALPHA)
            for y in range(0, height, 2):
                pygame.draw.line(
                    self.scanline_surface,
                    (0, 0, 0, 50),  # Semi-transparent black
                    (0, y),
                    (width, y)
                )
        
        surface.blit(self.scanline_surface, (0, 0))
    
    def _apply_vignette(self, surface: pygame.Surface):
        """Apply vignette (darker edges)."""
        width, height = surface.get_size()
        
        if (self.vignette_surface is None or
            self.vignette_surface.get_size() != (width, height)):
            self.vignette_surface = pygame.Surface((width, height), pygame.SRCALPHA)
            
            cx, cy = width // 2, height // 2
            max_dist = math.sqrt(cx**2 + cy**2)
            
            for y in range(height):
                for x in range(width):
                    dist = math.sqrt((x - cx)**2 + (y - cy)**2)
                    # Vignette intensity increases toward edges
                    intensity = (dist / max_dist) ** 2
                    alpha = int(min(100, intensity * 150))
                    self.vignette_surface.set_at((x, y), (0, 0, 0, alpha))
        
        surface.blit(self.vignette_surface, (0, 0))
    
    def _apply_noise(self, surface: pygame.Surface):
        """Apply subtle noise/static."""
        width, height = surface.get_size()
        
        # Only apply to a few random pixels for performance
        for _ in range(100):
            x = random.randint(0, width - 1)
            y = random.randint(0, height - 1)
            
            # Get current pixel and slightly modify
            color = surface.get_at((x, y))
            noise = random.randint(-15, 15)
            
            new_color = (
                max(0, min(255, color.r + noise)),
                max(0, min(255, color.g + noise)),
                max(0, min(255, color.b + noise)),
            )
            surface.set_at((x, y), new_color)


class ScreenFlash:
    """Full-screen flash effect."""
    
    def __init__(self):
        self.active = False
        self.color = (255, 255, 255)
        self.duration = 0
        self.elapsed = 0
    
    def trigger(self, color: tuple = (255, 255, 255), duration: float = 0.1):
        self.active = True
        self.color = color
        self.duration = duration
        self.elapsed = 0
    
    def update(self, dt: float):
        if self.active:
            self.elapsed += dt
            if self.elapsed >= self.duration:
                self.active = False
    
    def render(self, surface: pygame.Surface):
        if self.active:
            alpha = int(255 * (1 - self.elapsed / self.duration))
            flash = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
            flash.fill((*self.color, alpha))
            surface.blit(flash, (0, 0))
```

### Pixel Text Rendering

```python
# src/graphics/text.py
import pygame
from src.core.settings import SETTINGS

class PixelFont:
    """Bitmap font rendering for pixel-perfect text."""
    
    _cache: dict[str, pygame.font.Font] = {}
    
    @classmethod
    def get_font(cls, size: int) -> pygame.font.Font:
        """Get or create a font at the specified size."""
        key = f"default_{size}"
        if key not in cls._cache:
            # Try to load custom pixel font, fall back to system
            try:
                font_path = SETTINGS.FONTS_DIR / "pixel.ttf"
                cls._cache[key] = pygame.font.Font(str(font_path), size)
            except:
                cls._cache[key] = pygame.font.Font(None, size)
        return cls._cache[key]
    
    @classmethod
    def render(
        cls,
        text: str,
        size: int,
        color: tuple = (0, 255, 100),
        antialias: bool = False
    ) -> pygame.Surface:
        """Render text to a surface."""
        font = cls.get_font(size)
        return font.render(text, antialias, color)
    
    @classmethod
    def render_outlined(
        cls,
        text: str,
        size: int,
        color: tuple = (0, 255, 100),
        outline_color: tuple = (0, 0, 0)
    ) -> pygame.Surface:
        """Render text with outline."""
        font = cls.get_font(size)
        
        # Render outline
        outline = font.render(text, False, outline_color)
        main = font.render(text, False, color)
        
        # Create surface with padding for outline
        width = main.get_width() + 2
        height = main.get_height() + 2
        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # Blit outline in all directions
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            surface.blit(outline, (1 + dx, 1 + dy))
        
        # Blit main text
        surface.blit(main, (1, 1))
        
        return surface
```

---

## USB Serial Integration

### Serial Manager

```python
# src/usb/serial_manager.py
import serial
import serial.tools.list_ports
import json
import threading
from queue import Queue, Empty
from typing import Optional, Callable
from dataclasses import dataclass

@dataclass
class USBEvent:
    device: str
    event_type: str
    data: dict

class SerialManager:
    """Manages USB serial communication with microcontrollers."""
    
    def __init__(self, baud_rate: int = 115200):
        self.baud_rate = baud_rate
        self.connection: Optional[serial.Serial] = None
        self.device_name: str = ""
        
        self._read_thread: Optional[threading.Thread] = None
        self._running = False
        self._event_queue: Queue[USBEvent] = Queue()
        self._callbacks: list[Callable[[USBEvent], None]] = []
    
    def list_ports(self) -> list[str]:
        """List available serial ports."""
        ports = serial.tools.list_ports.comports()
        return [port.device for port in ports]
    
    def connect(self, port: str, device_name: str = "control_panel") -> bool:
        """Connect to a serial port."""
        try:
            self.connection = serial.Serial(
                port=port,
                baudrate=self.baud_rate,
                timeout=0.1
            )
            self.device_name = device_name
            self._running = True
            
            # Start read thread
            self._read_thread = threading.Thread(target=self._read_loop, daemon=True)
            self._read_thread.start()
            
            print(f"Connected to {port} as {device_name}")
            return True
            
        except serial.SerialException as e:
            print(f"Failed to connect to {port}: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from serial port."""
        self._running = False
        if self._read_thread:
            self._read_thread.join(timeout=1.0)
        if self.connection:
            self.connection.close()
            self.connection = None
    
    def send(self, command: str, data: dict = None):
        """Send a command to the microcontroller."""
        if not self.connection:
            return
        
        message = {
            "cmd": command,
            "data": data or {}
        }
        
        try:
            json_str = json.dumps(message) + "\n"
            self.connection.write(json_str.encode())
        except serial.SerialException as e:
            print(f"Failed to send: {e}")
    
    def set_led(self, led_id: int, color: tuple[int, int, int], brightness: float = 1.0):
        """Convenience method to set an LED."""
        self.send("set_led", {
            "id": led_id,
            "r": color[0],
            "g": color[1],
            "b": color[2],
            "brightness": brightness
        })
    
    def on_event(self, callback: Callable[[USBEvent], None]):
        """Register callback for USB events."""
        self._callbacks.append(callback)
    
    def update(self):
        """Process queued events (call from main thread)."""
        while True:
            try:
                event = self._event_queue.get_nowait()
                for callback in self._callbacks:
                    callback(event)
            except Empty:
                break
    
    def _read_loop(self):
        """Background thread to read serial data."""
        buffer = ""
        
        while self._running and self.connection:
            try:
                if self.connection.in_waiting > 0:
                    data = self.connection.read(self.connection.in_waiting)
                    buffer += data.decode('utf-8', errors='ignore')
                    
                    # Process complete lines
                    while '\n' in buffer:
                        line, buffer = buffer.split('\n', 1)
                        self._process_line(line.strip())
                        
            except serial.SerialException:
                break
    
    def _process_line(self, line: str):
        """Process a received line of JSON."""
        if not line:
            return
        
        try:
            data = json.loads(line)
            event = USBEvent(
                device=self.device_name,
                event_type=data.get("event", "unknown"),
                data=data.get("data", {})
            )
            self._event_queue.put(event)
            
        except json.JSONDecodeError:
            print(f"Invalid JSON received: {line}")
```

### Usage in Game

```python
# In game setup
from src.usb.serial_manager import SerialManager, USBEvent

serial = SerialManager()

# List available ports
ports = serial.list_ports()
print(f"Available ports: {ports}")

# Connect (e.g., to first available port)
if ports:
    serial.connect(ports[0], "control_panel")

# Register event handler
def handle_usb_event(event: USBEvent):
    if event.event_type == "button_press":
        button_id = event.data.get("id")
        print(f"Physical button {button_id} pressed!")
        # Forward to current game state

serial.on_event(handle_usb_event)

# In game loop
serial.update()  # Process events

# Send LED update
serial.set_led(0, (255, 0, 0))  # Red LED
```

---

## Audio System

```python
# src/audio/audio_manager.py
import pygame
from pathlib import Path
from src.core.settings import SETTINGS

class AudioManager:
    """Manages sound effects and music."""
    
    def __init__(self):
        self._sounds: dict[str, pygame.mixer.Sound] = {}
        self._music_volume = 0.5
        self._sfx_volume = 0.7
        
        self._load_sounds()
    
    def _load_sounds(self):
        """Load all sound effects."""
        sfx_dir = SETTINGS.AUDIO_DIR / "sfx"
        
        sound_files = {
            "click": "click.wav",
            "success": "success.wav",
            "strike": "strike.wav",
            "alarm": "alarm.wav",
            "tick": "tick.wav",
            "meltdown": "meltdown.wav",
        }
        
        for name, filename in sound_files.items():
            path = sfx_dir / filename
            if path.exists():
                self._sounds[name] = pygame.mixer.Sound(str(path))
                self._sounds[name].set_volume(self._sfx_volume)
    
    def play_sfx(self, name: str):
        """Play a sound effect."""
        if name in self._sounds:
            self._sounds[name].play()
    
    def play_music(self, filename: str, loop: bool = True):
        """Play background music."""
        path = SETTINGS.AUDIO_DIR / "music" / filename
        if path.exists():
            pygame.mixer.music.load(str(path))
            pygame.mixer.music.set_volume(self._music_volume)
            pygame.mixer.music.play(-1 if loop else 0)
    
    def stop_music(self):
        """Stop background music."""
        pygame.mixer.music.stop()
    
    def set_sfx_volume(self, volume: float):
        """Set SFX volume (0.0 - 1.0)."""
        self._sfx_volume = max(0.0, min(1.0, volume))
        for sound in self._sounds.values():
            sound.set_volume(self._sfx_volume)
    
    def set_music_volume(self, volume: float):
        """Set music volume (0.0 - 1.0)."""
        self._music_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self._music_volume)
```

---

## Build & Distribution

### Requirements File

```txt
# requirements.txt
pygame-ce>=2.4.0
pyserial>=3.5
pillow>=10.0.0  # For asset processing
```

### PyInstaller Build Script

```python
# tools/build.py
import PyInstaller.__main__
import shutil
from pathlib import Path

def build_windows():
    """Build Windows executable."""
    
    # Clean previous builds
    for folder in ["build", "dist"]:
        if Path(folder).exists():
            shutil.rmtree(folder)
    
    PyInstaller.__main__.run([
        "main.py",
        "--name=FissionImpossible",
        "--onefile",
        "--windowed",
        "--icon=assets/icon.ico",
        "--add-data=assets:assets",
        "--hidden-import=pygame",
        "--hidden-import=serial",
    ])
    
    print("Build complete! Executable in dist/")

if __name__ == "__main__":
    build_windows()
```

### Build Commands

```bash
# Development (MacOS)
# ───────────────────

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run game
python main.py

# ───────────────────
# Build for Windows
# ───────────────────

# Install PyInstaller
pip install pyinstaller

# Build
python tools/build.py

# Or manually:
pyinstaller --onefile --windowed --name=FissionImpossible \
    --add-data="assets:assets" main.py

# Output: dist/FissionImpossible.exe
```

---

## Comparison: Pygame vs Godot

| Aspect | Pygame | Godot |
|--------|--------|-------|
| **Learning curve** | Moderate (Python) | Moderate (GDScript) |
| **2D rendering** | Manual but flexible | Built-in, excellent |
| **Pixel art** | Manual scaling, easy | Built-in, trivial |
| **Shaders** | Software or OpenGL | Built-in GLSL |
| **USB serial** | Native (pyserial) | Requires bridge |
| **Distribution** | PyInstaller (complex) | One-click export |
| **Editor** | None (code only) | Full visual editor |
| **Scene system** | Manual state machine | Built-in |
| **Hot reload** | Possible with extra work | Built-in |
| **File size** | ~50MB (with Python) | ~30MB |
| **Startup time** | ~1-2 seconds | ~0.5 seconds |

### When to Choose Pygame

✅ **Choose Pygame if:**
- USB serial integration is critical and you want it native
- Team is very comfortable with Python
- You prefer code-only development
- You want full control over everything
- The game is simple enough to not need an editor

❌ **Avoid Pygame if:**
- Fast iteration on visuals is important
- You want easy cross-platform builds
- The project may grow complex
- Startup time matters (party game context)

---

## Development Phases (Pygame)

### Phase 1: Foundation
- [ ] Project setup, virtual environment
- [ ] Main game loop, state machine
- [ ] Settings and configuration
- [ ] Basic rendering pipeline with scaling

### Phase 2: Core Screens
- [ ] Start screen (terminal aesthetic)
- [ ] Game screen layout
- [ ] End screens
- [ ] Screen transitions

### Phase 3: Game Logic
- [ ] Timer and strike system
- [ ] Edgework generation
- [ ] Module base class
- [ ] 2 simple modules (Coolant, Terminal)

### Phase 4: Visual Polish
- [ ] CRT effect implementation
- [ ] Pixel font rendering
- [ ] Animations and transitions
- [ ] All 6 modules

### Phase 5: Audio
- [ ] Audio manager
- [ ] Sound effects integration
- [ ] Background ambient/music

### Phase 6: USB Integration
- [ ] Serial manager
- [ ] Protocol definition
- [ ] Input mapping
- [ ] LED output

### Phase 7: Distribution
- [ ] PyInstaller configuration
- [ ] Windows testing
- [ ] Final packaging

---

## Summary

The Pygame architecture offers:

| Benefit | Details |
|---------|---------|
| **Native USB** | pyserial in same process, no bridge |
| **Python ecosystem** | Access to any Python library |
| **Full control** | No engine abstractions |
| **Familiar language** | Python is widely known |

At the cost of:

| Tradeoff | Details |
|----------|---------|
| **More boilerplate** | Must implement state machine, effects, etc. |
| **Harder distribution** | PyInstaller requires careful setup |
| **No visual editor** | All layout done in code |
| **Manual effects** | CRT shader is software-only or needs OpenGL |

This is a viable alternative to Godot, especially if USB integration simplicity is the top priority.

---

*Document Version: 1.0*
*Alternative Architecture — Pygame Edition*
