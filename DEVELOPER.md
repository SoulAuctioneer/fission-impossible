# Fission Impossible — Developer Guide

A "Keep Talking and Nobody Explodes"-style cooperative bomb defusal game with a 1980s nuclear power plant terminal aesthetic. Built with Pygame-CE using ASCII/ANSI text-based graphics.

## Quick Start

```bash
# Create and activate virtual environment
python -m venv venv

# On Windows (PowerShell):
.\venv\Scripts\Activate.ps1

# On Windows (Command Prompt):
# venv\Scripts\activate.bat

# On macOS/Linux:
# source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the game
python main.py
```

## Project Structure

```
fission-impossible/
├── main.py                      # Entry point
├── requirements.txt             # Python dependencies
│
├── src/
│   ├── core/                    # Game engine
│   │   ├── game.py              # Main game class, game loop
│   │   ├── settings.py          # Configuration constants
│   │   ├── state_machine.py     # Scene/state management
│   │   ├── input.py             # Input handling, pixel↔char conversion
│   │   └── game_state.py        # Runtime game state (timer, strikes)
│   │
│   ├── terminal/                # ASCII rendering system (core of the engine)
│   │   ├── text_buffer.py       # 2D character grid data structure
│   │   ├── font_renderer.py     # Renders buffer to pygame surface
│   │   ├── colors.py            # 16-color ANSI palette
│   │   └── box_drawing.py       # Box-drawing character helpers
│   │
│   ├── ui/                      # Reusable UI components
│   │   ├── button.py            # Clickable ASCII button
│   │   ├── progress_bar.py      # Block-based progress bar
│   │   ├── seven_segment.py     # Digital number display
│   │   ├── reactor_status.py    # Status panel component
│   │   └── edgework_panel.py    # Serial/indicators display
│   │
│   ├── states/                  # Game screens
│   │   ├── base_state.py        # State interface
│   │   ├── start_screen.py      # Clock-in terminal
│   │   ├── briefing_screen.py   # Pre-game briefing
│   │   ├── game_screen.py       # Main gameplay
│   │   └── end_screen.py        # Win/lose screen
│   │
│   ├── modules/                 # Puzzle modules
│   │   ├── base_module.py       # Base class for all modules
│   │   ├── coolant_valves.py    # Wire-cutting puzzle
│   │   ├── emergency_override.py # Button-holding puzzle
│   │   ├── vent_codes.py        # Symbol matching puzzle
│   │   ├── rod_alignment.py     # Maze navigation puzzle
│   │   ├── pressure_locks.py    # Grid navigation puzzle
│   │   └── security_terminal.py # Word puzzle
│   │
│   ├── audio/                   # Sound system
│   │   └── audio_manager.py     # SFX playback
│   │
│   ├── effects/                 # Visual effects
│   │   ├── crt.py               # CRT screen effects
│   │   └── flicker.py           # Screen flicker/glitch
│   │
│   └── utils/
│       └── edgework.py          # Serial number, battery, indicator generation
│
├── assets/
│   ├── fonts/
│   │   └── PxPlus_IBM_VGA8.ttf  # DOS-style monospace font
│   └── audio/sfx/               # Sound effects
│
└── manual/
    └── index.html               # Bomb defusal manual (for the "expert")
```

## Core Concepts

### The Terminal Buffer System

All rendering goes through a `TextBuffer` — a 120×45 character grid where each cell has:
- A character (Unicode)
- A foreground color (0-15)
- A background color (0-15)

```python
# Writing to the buffer
buffer.put_char(x, y, '█', fg=Color.LIGHT_GREEN)
buffer.put_string(10, 5, "Hello", fg=Color.LIGHT_CYAN)
buffer.put_string_centered(y=20, "Centered Text", fg=Color.WHITE)
```

The `FontRenderer` converts this buffer to pixels each frame.

### Color Palette

Standard 16-color ANSI palette in `src/terminal/colors.py`:

| Index | Name | Usage |
|-------|------|-------|
| 0 | Black | Background |
| 8 | Dark Gray | Dim/disabled text |
| 9 | Light Red | Errors, warnings |
| 10 | Light Green | Primary terminal text |
| 11 | Light Yellow | Caution indicators |
| 14 | Light Cyan | Highlights, titles |
| 15 | White | Emphasis |

Use semantic aliases: `Color.TERMINAL`, `Color.ERROR`, `Color.WARNING`, `Color.HIGHLIGHT`

### Box Drawing

Use `box_drawing.py` helpers for borders:

```python
from src.terminal.box_drawing import draw_box, draw_titled_box, SINGLE, DOUBLE

draw_box(buffer, x=0, y=0, w=20, h=10, style=SINGLE, fg=Color.GREEN)
draw_titled_box(buffer, x=0, y=0, w=20, h=10, title="PANEL", style=DOUBLE)
```

Available styles: `SINGLE`, `DOUBLE`, `HEAVY`, `ROUND`

### Input Handling

Mouse coordinates are converted to character positions:

```python
# In event handling
char_x, char_y = event.char_pos  # Character grid coordinates
```

### State Machine

Game screens are managed via a state stack:

```python
class MyState(BaseState):
    def handle_event(self, event): ...
    def update(self, dt): ...
    def render(self, buffer): ...
```

## Creating a New Module

1. Create `src/modules/my_module.py`:

```python
from src.modules.base_module import BaseModule

class MyModule(BaseModule):
    def _initialize(self):
        self.name = "MY MODULE"
        # Set up puzzle state
    
    def _render_content(self, buffer, x, y, w, h):
        # Draw module contents (inside the border)
        buffer.put_string(x + 2, y + 2, "Content here", Color.LIGHT_GREEN)
    
    def handle_event(self, event, char_x, char_y):
        # Handle clicks within module bounds
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Check if click is on interactive element
            pass
    
    def _check_solution(self):
        # Return True if puzzle is solved
        return False
```

2. Add to `src/modules/__init__.py`
3. Instantiate in `game_screen.py`

## Common Patterns

### Drawing a button

```python
from src.ui.button import ASCIIButton

btn = ASCIIButton(x=10, y=5, text="SUBMIT", width=12)
btn.render(buffer)

# In event handler
if btn.contains_char(char_x, char_y):
    btn.hovered = True
```

### Progress bar

```python
from src.ui.progress_bar import ASCIIProgressBar

bar = ASCIIProgressBar(x=5, y=10, width=20)
bar.set_value(0.75)  # 75%
bar.render(buffer)
```

### Playing audio

```python
self.game.audio.play_sfx("button_click")
```

## Build for Distribution

```bash
pyinstaller --onefile --windowed --name=FissionImpossible \
    --add-data="assets:assets" --add-data="manual:manual" main.py
```

## Key Files to Read First

1. `src/core/game.py` — Main loop, how everything connects
2. `src/terminal/text_buffer.py` — The core rendering abstraction
3. `src/modules/base_module.py` — How puzzles are structured
4. `src/states/game_screen.py` — How modules are laid out and orchestrated
