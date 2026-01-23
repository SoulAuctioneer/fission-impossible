# Fission Impossible

**A cooperative party game for NuHaus Nuclear employees.**

*"We're Glad You're Expendable."*

## Overview

Fission Impossible is a local multiplayer communication game inspired by *Keep Talking and Nobody Explodes*. One player (the **Technician**) operates a nuclear maintenance terminal while other players (the **Hotline**) read from the Operations Manual to guide them through disarming system malfunctions before the reactor melts down.

## Features

- **Authentic 1980s terminal aesthetic** - ASCII/ANSI graphics with CRT-style rendering
- **6 unique puzzle modules** - Each requiring different skills and communication
- **Procedurally generated puzzles** - Every game is different
- **5-minute timer** - Fast-paced tension
- **3 strikes system** - Make too many mistakes and it's game over
- **Auto-reset** - Perfect for party play, automatically returns to start screen
- **Web-based Operations Manual** - Hotline players can use any device

## Screenshots

```
╔═══════════════════════════════════════════════════════════════════════╗
║  ████  NUHAUS NUCLEAR — MAINTENANCE ROOM 7-G  ████                   ║
╠═══════════════════════════════════════════════════════════════════════╣
║  ╔═══════════════════════╗  ╔═══════════════════════╗  ╔═══════════╗ ║
║  ║    COOLANT BYPASS     ║  ║  EMERGENCY OVERRIDE   ║  ║  REACTOR  ║ ║
║  ║  [R] ═══════════════  ║  ║    ╔═══════════╗      ║  ║  STATUS   ║ ║
║  ║  [B] ═══════════════  ║  ║    ║   HOLD    ║      ║  ║           ║ ║
║  ║  [Y] ═══╳═══════════  ║  ║    ╚═══════════╝      ║  ║  04:32    ║ ║
║  ║  STATUS: [○]          ║  ║  STATUS: [○]          ║  ║  [●][○][○]║ ║
║  ╚═══════════════════════╝  ╚═══════════════════════╝  ╚═══════════╝ ║
╚═══════════════════════════════════════════════════════════════════════╝
```

## Installation

### Requirements

- Python 3.11+
- pygame-ce 2.4+
- numpy 1.24+

### Setup

```bash
# Clone or download the repository
cd fission-impossible

# Install dependencies
pip install -r requirements.txt

# Run the game
python main.py
```

## How to Play

### The Technician (Game Player)

1. Launch the game and click **CLOCK IN**
2. You'll see the maintenance terminal with 6 malfunctioning modules
3. Describe what you see to the Hotline
4. Follow their instructions to solve each module
5. Solve all modules before time runs out!

### The Hotline (Manual Readers)

1. Open the Operations Manual (`manual/index.html`) in a web browser
2. Listen to the Technician's descriptions
3. Look up the correct procedures in the manual
4. Guide them through solving each module
5. Be quick and accurate - lives depend on it!

## Modules

| Module | Based On | Description |
|--------|----------|-------------|
| **Coolant Bypass** | Wires | Close the correct colored valve |
| **Emergency Override** | Button | Press or hold based on rules |
| **Vent Codes** | Keypads | Press symbols in order |
| **Rod Alignment** | Simon Says | Repeat color sequences |
| **Pressure Locks** | Maze | Navigate to the target |
| **Security Terminal** | Password | Cycle letters to form a word |

## Controls

- **Mouse** - Click to interact with modules
- **ESC** - Quit game

## Project Structure

```
fission-impossible/
├── main.py                 # Entry point
├── requirements.txt        # Dependencies
├── manual/                 # Operations Manual (HTML)
│   └── index.html
├── src/
│   ├── core/              # Game engine
│   ├── terminal/          # ASCII rendering
│   ├── ui/                # UI components
│   ├── states/            # Game screens
│   ├── modules/           # Puzzle modules
│   ├── effects/           # Visual effects
│   └── audio/             # Sound system
└── assets/
    └── fonts/             # DOS-style font
```

## Development

Built with:
- **pygame-ce** - Game framework
- **numpy** - Efficient character grid handling
- **PxPlus IBM VGA8** - Authentic DOS font

The game uses a terminal-style rendering system where all graphics are ASCII characters rendered to a 120x45 character grid.

## Credits

- Inspired by *Keep Talking and Nobody Explodes* by Steel Crate Games
- Font from [int10h.org](https://int10h.org/oldschool-pc-fonts/)

## License

This is a fan project for educational purposes.

---

*NUHAUS NUCLEAR — "Powering Tomorrow, Today... Eventually"*

*Remember: Reading is fundamental. So is not exploding.*
