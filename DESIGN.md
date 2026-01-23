# Fission Impossible — Game Design Document

## Overview

**Fission Impossible** is a simplified, web-based party game inspired by *Keep Talking and Nobody Explodes*. Designed for quick pickup play at parties and gatherings, the game prioritizes:

- **Instant start** — One click to begin
- **Automatic reset** — Returns to start screen after each round
- **Full immersion** — All UI elements are "in-world"
- **Widescreen layout** — Control panel fills the screen

---

## Game Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│   ┌─────────┐      ┌─────────┐      ┌─────────┐                │
│   │  START  │ ───► │  GAME   │ ───► │   END   │                │
│   │  SCREEN │      │  SCREEN │      │  SCREEN │                │
│   └─────────┘      └─────────┘      └─────────┘                │
│        ▲                                  │                     │
│        │                                  │                     │
│        └──────────── auto-reset ──────────┘                     │
│                     (3-5 seconds)                               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### States

| State | Duration | Trigger to Next |
|-------|----------|-----------------|
| **START** | Until player clicks | Click "CLOCK IN" button |
| **GAME** | Until timer expires OR all modules solved OR 3 strikes | Win or lose condition met |
| **END** | 5 seconds | Automatic transition to START |

---

## Start Screen

### Design Philosophy

The start screen is presented as a **shift clock-in terminal** — an in-world CRT computer screen that employees see when beginning their shift. This maintains immersion while delivering necessary information.

### Layout

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  ████  NUHAUS NUCLEAR — MAINTENANCE TERMINAL v2.4.1  ████                    ║
║  ═══════════════════════════════════════════════════════════                 ║
║                                                                              ║
║  ┌────────────────────────────────────────────────────────────────────────┐  ║
║  │                                                                        │  ║
║  │                      ☢  SHIFT BRIEFING  ☢                             │  ║
║  │                                                                        │  ║
║  │   ALERT: Reactor systems experiencing anomalies.                       │  ║
║  │   Maintenance Room 7-G requires immediate attention.                   │  ║
║  │                                                                        │  ║
║  │   ─────────────────────────────────────────────────                    │  ║
║  │                                                                        │  ║
║  │   TECHNICIAN: Resolve all system faults before meltdown.               │  ║
║  │   HOTLINE: Consult the Operations Manual. Guide them through.          │  ║
║  │                                                                        │  ║
║  │   ⚠ DO NOT exceed 3 operational errors.                                │  ║
║  │   ⚠ DO NOT allow the reactor to reach critical temperature.            │  ║
║  │                                                                        │  ║
║  │   ─────────────────────────────────────────────────                    │  ║
║  │                                                                        │  ║
║  │   Manual available at:  [MANUAL URL / QR CODE]                         │  ║
║  │                                                                        │  ║
║  └────────────────────────────────────────────────────────────────────────┘  ║
║                                                                              ║
║                      ╔═══════════════════════════╗                           ║
║                      ║                           ║                           ║
║                      ║      [ CLOCK IN ]         ║                           ║
║                      ║                           ║                           ║
║                      ╚═══════════════════════════╝                           ║
║                                                                              ║
║  NUHAUS NUCLEAR — "We're Glad You're Expendable"              TERMINAL 7-G  ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

### Elements

| Element | Purpose | Notes |
|---------|---------|-------|
| **Header** | Establish setting | Fake terminal version number adds authenticity |
| **Shift Briefing** | Set the scene | Brief, punchy, in-world |
| **Instructions** | Explain roles | One line each for Technician and Hotline |
| **Warnings** | Explain fail conditions | Styled as workplace safety notices |
| **Manual Link/QR** | Access for Hotline players | Opens in new tab or scannable |
| **CLOCK IN Button** | Start game | Large, obvious, satisfying to click |
| **Footer** | Atmosphere | Tagline reinforces dark humor |

### Behavior

- **Idle animation**: Subtle CRT flicker, occasional screen artifacts
- **Sound**: Ambient hum, perhaps distant alarms (muted)
- **Button hover**: Brightens, slight buzz sound
- **Button click**: Mechanical clunk, screen transition

---

## Main Game Screen (Control Panel)

### Design Philosophy

The control panel IS the game. It fills the entire screen in widescreen format (16:9 or 21:9). The Technician sees a wall of analog instruments, switches, and indicators. Everything is interactive or provides critical information.

### Layout Structure

```
╔═════════════════════════════════════════════════════════════════════════════════════╗
║                           NUHAUS NUCLEAR — MAINTENANCE ROOM 7-G                     ║
╠═════════════════════════════════════════════════════════════════════════════════════╣
║                                                                                     ║
║   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐   ┌──────────────────────┐    ║
║   │             │   │             │   │             │   │                      │    ║
║   │   MODULE    │   │   MODULE    │   │   MODULE    │   │   REACTOR STATUS     │    ║
║   │     1       │   │     2       │   │     3       │   │                      │    ║
║   │             │   │             │   │             │   │   ╔══════════════╗   │    ║
║   │  (varies)   │   │  (varies)   │   │  (varies)   │   │   ║   05:00      ║   │    ║
║   │             │   │             │   │             │   │   ║   COUNTDOWN  ║   │    ║
║   └─────────────┘   └─────────────┘   └─────────────┘   │   ╚══════════════╝   │    ║
║                                                         │                      │    ║
║   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐   │   ERRORS: ○ ○ ○      │    ║
║   │             │   │             │   │             │   │                      │    ║
║   │   MODULE    │   │   MODULE    │   │   MODULE    │   │   TEMP: ▓▓▓▓░░░░     │    ║
║   │     4       │   │     5       │   │     6       │   │                      │    ║
║   │             │   │             │   │             │   │   [STATUS TEXT]      │    ║
║   │  (varies)   │   │  (varies)   │   │  (varies)   │   │                      │    ║
║   │             │   │             │   │             │   └──────────────────────┘    ║
║   └─────────────┘   └─────────────┘   └─────────────┘                               ║
║                                                                                     ║
╚═════════════════════════════════════════════════════════════════════════════════════╝
```

### Panel Sections

#### Module Grid (Left ~75% of screen)
- **6 module slots** arranged in 2 rows × 3 columns
- Each module is a self-contained panel with its own frame/border
- Modules have a **status indicator** (LED) showing solved/unsolved
- Active modules have visual "active" state (lit up, humming)
- Solved modules dim slightly, LED turns green

#### Reactor Status Panel (Right ~25% of screen)
- **Countdown Timer**: Large digital display, counts down from 5:00
- **Error Indicators**: Three circles/lights (strikes), fill red on error
- **Temperature Gauge**: Visual representation of urgency (rises with time/errors)
- **Status Text**: Scrolling messages, warnings, corporate announcements

### Visual Design

**Color Palette:**
- Panel background: Dark gray metallic
- Module frames: Institutional green, beige, or orange
- Active elements: Amber/orange indicators
- Warning states: Red
- Success states: Green
- Text: Phosphor green or amber (CRT style)

**Textures:**
- Brushed metal panels
- Bakelite switches
- Glass gauge covers
- Faded warning labels
- Screw heads in corners

**Lighting:**
- Modules have subtle internal glow when active
- Indicator lights have bloom effect
- Overall slight vignette (darker edges)

---

## Modules (Simplified Set)

For the initial simple version, we include **6 modules** selected for:
- Clear visual communication
- Distinct interaction types
- Varying difficulty
- Good party game pacing

### Module Selection

| # | Module Name | Based On | Difficulty | Interaction |
|---|-------------|----------|------------|-------------|
| 1 | **Coolant Valves** | Wires | Easy | Click to cut |
| 2 | **Emergency Override** | The Button | Medium | Click/hold + timing |
| 3 | **Vent Codes** | Keypads | Medium | Click in sequence |
| 4 | **Rod Alignment** | Simon Says | Hard | Memory sequence |
| 5 | **Pressure Locks** | Maze | Medium | Directional navigation |
| 6 | **Security Terminal** | Password | Easy | Cycle + submit |

---

### Module 1: Coolant Valves

**Original:** Wires

**Visual:** 3-6 colored pipes/tubes running vertically with valve handles

**Interaction:** Click a valve handle to "close" it (equivalent to cutting wire)

**Rules:** Identical logic to original Wires module, re-themed:
- Colors: Red, Blue, Yellow, White, Black pipes
- References serial number from Reactor Status panel

**Status Indicator:** Gauge showing "FLOW NOMINAL" when solved

---

### Module 2: Emergency Override

**Original:** The Button

**Visual:** Large illuminated button with text label, status strip on side

**Interaction:** 
- Click = quick press
- Click and hold = hold (strip illuminates with color)
- Release based on timer digit

**Rules:** Same decision tree as original, references:
- Button color and label
- Battery count (shown on panel somewhere)
- Indicator lights (shown on panel)

**Status Indicator:** "OVERRIDE COMPLETE" display

---

### Module 3: Vent Codes

**Original:** Keypads

**Visual:** 4 buttons with strange symbols (hazard/technical symbols)

**Interaction:** Click buttons in correct order

**Rules:** Same column-matching logic
- Symbols themed as: biohazard variants, radiation symbols, warning pictograms
- Must match all 4 to one column, press in column order

**Status Indicator:** "ACCESS GRANTED" display

---

### Module 4: Rod Alignment

**Original:** Simon Says

**Visual:** 4 colored indicator lights arranged in diamond, with corresponding buttons

**Interaction:** Watch sequence, press corresponding buttons (with color mapping)

**Rules:** Same mapping tables based on:
- Serial number vowel check
- Current strike count affects mapping

**Status Indicator:** "RODS ALIGNED" display

---

### Module 5: Pressure Locks

**Original:** Maze

**Visual:** Grid display showing position marker and target, directional buttons

**Interaction:** Use arrow buttons to navigate marker to target

**Rules:** 
- Invisible walls (shown in manual)
- Two reference markers identify which maze layout
- Hit wall = strike

**Status Indicator:** "PRESSURE EQUALIZED" display

---

### Module 6: Security Terminal

**Original:** Password

**Visual:** 5-character display with up/down buttons for each position, SUBMIT button

**Interaction:** Cycle through available letters, submit when word formed

**Rules:** Same word list (or new themed word list):
- Technician reads available letters per position
- Hotline finds the matching word
- Submit correct word to solve

**Possible themed words:**
```
ALARM  ATOMS  BADGE  BURNS  CHAIN
CLEAN  CLOCK  CODES  CORES  DECAY
DRAIN  FUSED  GAUGE  GEARS  GUARD
HAZED  LEAKS  METER  NUKED  PLANT
POWER  RODS   SHIFT  SIREN  SMOKE
SPLIT  STEAM  TIMER  VALVE  VAULT
WASTE  WATTS
```

**Status Indicator:** "TERMINAL UNLOCKED" display

---

## Reactor Status Panel Details

### Countdown Timer

**Display:** Large 7-segment display showing MM:SS

**Behavior:**
- Starts at **5:00** (adjustable)
- Counts down in real-time
- Accelerates slightly after each strike (speeds up 10%)
- Final 60 seconds: display flashes/pulses red
- Final 10 seconds: rapid flash, alarm sound

**Visual:** 
- Green digits normally
- Yellow under 2:00
- Red under 1:00

### Error Indicators (Strikes)

**Display:** Three circular lights labeled "ERROR 1", "ERROR 2", "ERROR 3"

**Behavior:**
- Start unlit
- Light up red sequentially on strikes
- Third light = game over
- Strike triggers: brief alarm, screen shake, timer speedup

### Temperature Gauge

**Display:** Analog meter or bar graph

**Purpose:** Visual tension indicator (cosmetic, tied to timer)

**Behavior:**
- Rises as timer decreases
- Jumps on strikes
- "CRITICAL" zone in red at top

### Status Text

**Display:** Single-line scrolling text display

**Content:** Random corporate messages, warnings, dark humor

**Examples:**
- "REMEMBER: Safety is YOUR responsibility."
- "Tip: Refer to manual section 7.4.2 — Oh wait, that's classified."
- "The vending machine in break room 3 has been restocked."
- "NOTICE: Tuesday's evacuation drill has been postponed indefinitely."
- "Gary would have solved this by now."

---

## End Screens

### Success Screen (Meltdown Averted)

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║                        ✓ SHIFT COMPLETE ✓                                    ║
║                                                                              ║
║              All systems stabilized. Meltdown averted.                       ║
║                                                                              ║
║              Time remaining: 02:34                                           ║
║              Errors logged: 1                                                ║
║                                                                              ║
║              ─────────────────────────────────────────                       ║
║                                                                              ║
║              This incident has been classified as:                           ║
║              "MINOR FLUCTUATION - NO FURTHER ACTION"                         ║
║                                                                              ║
║              Your performance review has been updated.                       ║
║                                                                              ║
║              ─────────────────────────────────────────                       ║
║                                                                              ║
║                      Returning to clock-in terminal...                       ║
║                                                                              ║
║  NUHAUS NUCLEAR — "Powering Tomorrow, Today... Eventually"                   ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

**Behavior:**
- Display for 5 seconds
- Subtle triumphant synth jingle
- Auto-transition to Start Screen

### Failure Screen (Meltdown)

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║                                                                              ║
║                                                                              ║
║                        ████████████████████████                              ║
║                        ████████████████████████                              ║
║                        ████  SIGNAL LOST  ████                               ║
║                        ████████████████████████                              ║
║                        ████████████████████████                              ║
║                                                                              ║
║                                                                              ║
║                                                                              ║
║              ─────────────────────────────────────────                       ║
║                                                                              ║
║              "NuHaus Nuclear extends its condolences                         ║
║               to the family of [EMPLOYEE NAME REDACTED]."                    ║
║                                                                              ║
║              Please direct all inquiries to our Legal department.            ║
║                                                                              ║
║              ─────────────────────────────────────────                       ║
║                                                                              ║
║                      Resetting terminal for next shift...                    ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

**Behavior:**
- Screen flashes white briefly (meltdown flash)
- Then displays message
- Ominous tone or static
- 5 second display
- Auto-transition to Start Screen

---

## Edgework (Bomb Metadata)

The control panel includes "ambient" information that some modules reference:

### Serial Number
**Location:** Plate on Reactor Status panel
**Format:** 2 letters, 1 number, 2 letters, 1 number (e.g., "AB3CD5")
**Used by:** Coolant Valves, Rod Alignment

### Battery Count
**Location:** Small battery backup display on panel
**Visual:** Icon showing 0-4 batteries
**Used by:** Emergency Override

### Indicator Lights
**Location:** Row of labeled indicator lights on panel
**Labels:** CAR, FRK, SIG, BOB, etc.
**States:** Lit or unlit
**Used by:** Emergency Override

### Port Panel (Simplified)
**Location:** Small connector panel section
**Shows:** Whether parallel port exists (yes/no)
**Used by:** (Could add Complicated Wires later)

---

## Operations Manual (For Hotline)

A separate web page / PDF that Hotline players access. Themed as an official NuHaus Nuclear employee manual.

### Format

**Web-based** (ideal for phones/tablets) with sections for each module.

**Structure:**
1. Cover page (NuHaus branding)
2. Table of Contents
3. Module instructions (one page each)
4. Reference appendices (symbols, etc.)

### Sample Page: Coolant Valves

```
═══════════════════════════════════════════════════════════════
NUHAUS NUCLEAR — OPERATIONS MANUAL
Section 4.2: Coolant Bypass Valve Emergency Procedures
═══════════════════════════════════════════════════════════════

IMPORTANT: Only ONE valve must be closed to restore nominal flow.
Closing incorrect valves may result in catastrophic backpressure.

Valve colors: RED, BLUE, YELLOW, WHITE, BLACK
Valves are numbered from TOP (1) to BOTTOM (3-6).

────────────────────────────────────────────────────────────────

3 VALVES:
• If no RED valves present: Close valve 2.
• Otherwise, if valve 3 is WHITE: Close valve 3.
• Otherwise, if more than one BLUE valve: Close last BLUE valve.
• Otherwise: Close valve 3.

4 VALVES:
• If more than one RED valve AND serial number ends in ODD digit: 
  Close last RED valve.
• Otherwise, if valve 4 is YELLOW and no RED valves: Close valve 1.
• Otherwise, if exactly one BLUE valve: Close valve 1.
• Otherwise, if more than one YELLOW valve: Close valve 4.
• Otherwise: Close valve 2.

[... continues for 5 and 6 valves ...]

────────────────────────────────────────────────────────────────
NOTE: Color coding system was updated in 1976. Some valves may
still display legacy colors. This is a known issue (Ticket #4,721).
═══════════════════════════════════════════════════════════════
```

---

## Technical Specifications

### Platform
- **Web-based** (HTML5 + CSS + JavaScript)
- Works in modern browsers (Chrome, Firefox, Safari, Edge)
- Responsive to different screen sizes (optimized for 16:9)
- No installation required

### Hosting
- Static hosting (GitHub Pages, Netlify, Vercel)
- Manual can be same domain or separate
- QR code on start screen links to manual

### Audio
- Web Audio API for sound effects
- Ambient drone/hum (looping)
- UI interaction sounds (clicks, buzzes)
- Alert sounds (strikes, warnings)
- Jingles (win/lose)
- All audio should be toggleable (mute button)

### State Management
- Game state in memory (no persistence needed)
- Procedural generation on each start:
  - Random module configuration
  - Random serial number
  - Random battery/indicator setup
  - Random module parameters (wire colors, etc.)

### Performance
- Target 60fps
- Lightweight (< 5MB total)
- Fast initial load (< 2 seconds)
- No framework dependencies (vanilla JS) OR lightweight framework (Svelte, etc.)

---

## Accessibility Considerations

### Visual
- High contrast mode option
- Color-blind friendly indicators (shapes + colors)
- Scalable UI elements

### Audio
- Visual indicators for all audio cues
- Subtitles for any speech
- Mute option that doesn't break gameplay

### Motor
- Large click targets
- No required rapid clicking
- Keyboard navigation support

---

## Future Expansion Possibilities

### Additional Modules
- Complicated Wires → Circuit Breakers
- Memory → Shift Log Verification
- Morse Code → Emergency Radio
- Wire Sequences → Fuel Rod Assembly

### Difficulty Modes
- **Training Shift:** 4 modules, 7:00 timer, 5 strikes
- **Standard Shift:** 6 modules, 5:00 timer, 3 strikes
- **Emergency Shift:** 6 modules, 4:00 timer, 2 strikes
- **Meltdown Mode:** 6 modules, 3:00 timer, 1 strike

### Needy Modules
- Atmosphere Control (Venting Gas equivalent)
- Pressure Release (Capacitor Discharge equivalent)

### Multiplayer Features
- Room codes for remote play
- Spectator mode
- Leaderboards (fastest times)

---

## File Structure (Proposed)

```
fission-impossible/
├── index.html              # Main game
├── manual/
│   └── index.html          # Operations manual
├── css/
│   ├── main.css            # Core styles
│   ├── terminal.css        # CRT/terminal effects
│   └── modules.css         # Module-specific styles
├── js/
│   ├── game.js             # Main game logic
│   ├── modules/
│   │   ├── coolant.js      # Coolant Valves
│   │   ├── override.js     # Emergency Override
│   │   ├── vents.js        # Vent Codes
│   │   ├── rods.js         # Rod Alignment
│   │   ├── pressure.js     # Pressure Locks
│   │   └── terminal.js     # Security Terminal
│   ├── audio.js            # Sound management
│   └── utils.js            # Utilities, RNG, etc.
├── assets/
│   ├── images/             # Textures, symbols
│   ├── audio/              # Sound effects, music
│   └── fonts/              # CRT/terminal fonts
└── docs/
    ├── GAME_REFERENCE.md
    ├── THEME.md
    └── DESIGN.md
```

---

## Summary

**Fission Impossible** is designed to be:

1. **Immediately playable** — One click to start, auto-reset after
2. **Fully immersive** — All UI is in-world, CRT terminal aesthetic
3. **Party-friendly** — 5-minute rounds, simple to explain, fun to watch
4. **Faithful adaptation** — Core mechanics preserved, theme transformed
5. **Technically simple** — Web-based, no installation, lightweight

The game captures the frantic communication gameplay of the original while wrapping it in the dark corporate comedy of NuHaus Nuclear.

*"Clock in. Don't clock out permanently."*

---

*Document Version: 1.0*
*Classification: INTERNAL — Game Design Team*
