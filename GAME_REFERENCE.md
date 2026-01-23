# Keep Talking and Nobody Explodes - Complete Game Reference

## Table of Contents
1. [Game Overview](#game-overview)
2. [Core Design Philosophy](#core-design-philosophy)
3. [Game Mechanics](#game-mechanics)
4. [Bomb Structure](#bomb-structure)
5. [Standard Modules](#standard-modules)
6. [Needy Modules](#needy-modules)
7. [Bomb Metadata (Edgework)](#bomb-metadata-edgework)
8. [Difficulty Scaling](#difficulty-scaling)
9. [Game Modes](#game-modes)
10. [Platform Considerations](#platform-considerations)

---

## Game Overview

**Keep Talking and Nobody Explodes** is an asymmetric cooperative party game developed by Steel Crate Games. The game creates a unique communication challenge where information is deliberately separated between players.

### The Core Loop
1. One player (the **Defuser**) can see the bomb but has no instructions
2. Other players (the **Experts**) have access to the Bomb Defusal Manual but cannot see the bomb
3. Players must verbally communicate to identify and solve modules before time runs out

### Win Condition
- Successfully disarm ALL modules on the bomb before the countdown timer reaches 0:00

### Lose Conditions
- The countdown timer reaches 0:00
- Too many strikes are recorded (mistakes during defusal)

---

## Core Design Philosophy

### Asymmetric Information
The game's genius lies in its information asymmetry:
- **Defuser** has: Visual access to the bomb, ability to interact with modules
- **Defuser lacks**: Knowledge of how to solve any module
- **Experts** have: Complete instructions for every module type
- **Experts lack**: Any visual information about the current bomb

This creates **mandatory communication** - neither party can succeed alone.

### Communication Under Pressure
- Time pressure forces quick, clear communication
- Ambiguous descriptions lead to mistakes and strikes
- Players naturally develop shorthand and efficient communication patterns
- Mistakes are costly but recoverable (with strike system)

### Procedural Generation
- Every bomb is different - modules, layouts, and metadata vary
- Prevents memorization; requires understanding the rules
- Increases replayability dramatically

### Accessible Complexity
- Individual modules have simple interactions (press buttons, cut wires)
- Complexity comes from decision trees requiring bomb metadata
- Easy to learn basics, mastery requires practice

---

## Game Mechanics

### The Countdown Timer
- Visible on the bomb face
- Counts down from a set time (varies by difficulty)
- **Accelerates after each strike** (punishment mechanic)
- When it reaches 0:00, the bomb explodes

### The Strike System
Strikes are recorded when the Defuser makes an incorrect action on a module.

| Configuration | Strikes Allowed | Notes |
|--------------|-----------------|-------|
| With Strike Indicator | 2 (explodes on 3rd) | Standard difficulty |
| Without Strike Indicator | 0 (explodes on 1st) | Expert/hardcore mode |

**Strike Consequences:**
- Visual/audio feedback (strike indicator lights up)
- Timer begins counting down faster
- Accumulated strikes persist across all modules

### Module Completion
- Each module has an LED indicator (top-right corner)
- LED turns **green** when the module is successfully disarmed
- Modules can be solved in **any order**
- All modules must be green to defuse the bomb

---

## Bomb Structure

### Physical Layout
```
┌─────────────────────────────────────┐
│  ┌─────────┐  ┌─────────┐  ┌─────┐ │
│  │ Module  │  │ Module  │  │Timer│ │
│  │    1    │  │    2    │  │02:30│ │
│  └─────────┘  └─────────┘  └─────┘ │
│  ┌─────────┐  ┌─────────┐  ┌─────┐ │
│  │ Module  │  │ Module  │  │Strike│ │
│  │    3    │  │    4    │  │ X X │ │
│  └─────────┘  └─────────┘  └─────┘ │
└─────────────────────────────────────┘
        FRONT FACE

┌──────────┐    ┌──────────┐
│ Serial # │    │ Battery  │
│ AB3CD5   │    │ Holder   │
│ Indicator│    │ [AA][AA] │
│ [CAR] ●  │    │          │
│ Port     │    │          │
│ [Serial] │    │          │
└──────────┘    └──────────┘
    SIDE 1          SIDE 2
```

### Components
- **Front Face**: Contains modules, timer, and strike indicator
- **Sides/Edges**: Contains metadata (serial number, batteries, ports, indicators)
- **Module Slots**: Up to 11 modules per bomb

---

## Standard Modules

Standard modules are discrete puzzles that, once solved, remain solved. Each has specific rules that often depend on bomb metadata.

---

### 1. WIRES MODULE

**Visual**: 3-6 colored wires running vertically

**Interaction**: Cut one wire (the correct one)

**Wire Colors**: Red, Blue, Yellow, White, Black

**Rules by Wire Count**:

#### 3 Wires
```
IF no red wires → Cut second wire
ELSE IF last wire is white → Cut last wire  
ELSE IF more than one blue wire → Cut last blue wire
ELSE → Cut last wire
```

#### 4 Wires
```
IF more than one red wire AND serial number last digit is odd → Cut last red wire
ELSE IF last wire is yellow AND no red wires → Cut first wire
ELSE IF exactly one blue wire → Cut first wire
ELSE IF more than one yellow wire → Cut last wire
ELSE → Cut second wire
```

#### 5 Wires
```
IF last wire is black AND serial number last digit is odd → Cut fourth wire
ELSE IF exactly one red wire AND more than one yellow wire → Cut first wire
ELSE IF no black wires → Cut second wire
ELSE → Cut first wire
```

#### 6 Wires
```
IF no yellow wires AND serial number last digit is odd → Cut third wire
ELSE IF exactly one yellow wire AND more than one white wire → Cut fourth wire
ELSE IF no red wires → Cut last wire
ELSE → Cut fourth wire
```

**Design Notes**:
- Order of conditions matters (first match wins)
- Requires: wire colors, wire count, wire positions, serial number parity
- Tests: counting, color identification, position tracking

---

### 2. THE BUTTON MODULE

**Visual**: Large colored button with a text label, colored strip on the right

**Interaction**: Either tap (press and release) or hold (press, wait for specific time, release)

**Button Colors**: Red, Blue, Yellow, White

**Button Labels**: "Abort", "Detonate", "Hold", "Press"

**Decision Rules** (in order):

```
1. IF button is blue AND says "Abort" → HOLD
2. IF more than 1 battery AND says "Detonate" → TAP
3. IF button is white AND lit indicator "CAR" exists → HOLD
4. IF more than 2 batteries AND lit indicator "FRK" exists → TAP
5. IF button is yellow → HOLD
6. IF button is red AND says "Hold" → TAP
7. OTHERWISE → HOLD
```

**Releasing a Held Button**:
When holding, a colored strip lights up. Release based on strip color:

| Strip Color | Release When Timer Shows |
|-------------|-------------------------|
| Blue | Any position has a "4" |
| Yellow | Any position has a "5" |
| White | Any position has a "1" |
| Any other | Any position has a "1" |

**Design Notes**:
- Two-phase interaction (decide action, then timing)
- Requires: button color, button label, battery count, indicator labels
- Tests: rule priority, counting, timing

---

### 3. KEYPADS MODULE

**Visual**: 4 buttons with strange symbols

**Interaction**: Press buttons in the correct order

**Mechanic**:
- There are 6 predefined columns of 7 symbols each
- The 4 symbols on the keypad all appear in exactly ONE column
- Press buttons in the order they appear in that column (top to bottom)

**The 6 Columns** (symbols represented as descriptions):
```
Column 1: Q-loop, AT, Lambda, Lightning, Kitty, H-bars, Reverse-C
Column 2: Euro, Q-loop, Reverse-C, Cursive, Empty-star, H-bars, Question
Column 3: Copyright, Pumpkin, Cursive, Double-K, Meltman, Lambda, Empty-star
Column 4: Six, Paragraph, B-T, Kitty, Double-K, Question, Smiley
Column 5: Trident, Smiley, B-T, C-dot, Paragraph, Dragon, Filled-star
Column 6: Six, Euro, Puzzle, AE, Trident, N-hat, Omega
```

**Design Notes**:
- Pattern matching puzzle
- Requires: accurate symbol description/identification
- Tests: communication of abstract symbols, pattern finding

---

### 4. SIMON SAYS MODULE

**Visual**: 4 colored buttons (red, blue, green, yellow) arranged in a diamond

**Interaction**: Repeat a flashing sequence using color mapping

**Mechanic**:
1. A colored button flashes
2. Based on vowels in serial number, use mapping table to find corresponding color
3. Press the mapped color
4. Sequence grows by one each round
5. Repeat until module disarms

**Color Mapping Tables**:

#### Serial Number Contains a Vowel (A, E, I, O, U):

| Flashing Color | No Strikes | 1 Strike | 2 Strikes |
|---------------|------------|----------|-----------|
| Red | Blue | Yellow | Green |
| Blue | Red | Green | Red |
| Green | Yellow | Blue | Yellow |
| Yellow | Green | Red | Blue |

#### Serial Number Contains NO Vowel:

| Flashing Color | No Strikes | 1 Strike | 2 Strikes |
|---------------|------------|----------|-----------|
| Red | Blue | Red | Yellow |
| Blue | Yellow | Blue | Green |
| Green | Green | Yellow | Blue |
| Yellow | Red | Green | Red |

**Design Notes**:
- Memory/sequence challenge
- Mapping changes based on current strike count (dynamic difficulty)
- Requires: serial number vowel check, current strike count
- Tests: memory, table lookup, sequence retention

---

### 5. WHO'S ON FIRST MODULE

**Visual**: Display screen showing a word, 6 buttons with word labels (2x3 grid)

**Interaction**: Press the correct button

**Two-Phase Solution**:

**Phase 1 - Find which button position to look at:**
Based on the DISPLAY word, determine which button position to read:

| Display Shows | Look At Position |
|--------------|------------------|
| YES | Middle-Left |
| FIRST | Top-Right |
| DISPLAY | Bottom-Right |
| OKAY | Top-Right |
| SAYS | Bottom-Right |
| NOTHING | Middle-Left |
| (blank) | Bottom-Left |
| NO | Bottom-Right |
| LED | Middle-Left |
| LEAD | Bottom-Right |
| READ | Middle-Right |
| RED | Middle-Right |
| REED | Bottom-Left |
| LEED | Bottom-Left |
| HOLD ON | Bottom-Right |
| YOU | Middle-Right |
| YOU ARE | Bottom-Right |
| YOUR | Middle-Right |
| YOU'RE | Middle-Right |
| UR | Top-Left |
| THERE | Bottom-Right |
| THEY'RE | Bottom-Left |
| THEIR | Middle-Right |
| THEY ARE | Middle-Left |
| SEE | Bottom-Right |
| C | Top-Right |
| CEE | Bottom-Right |

**Phase 2 - Find which button to press:**
Read the word on that button position, then find that word in the lookup table. Press the FIRST button (from the list) that appears on the bomb.

*[Full lookup table has 28 words, each with a priority list of 14+ valid responses]*

Example:
- "READY" → press first of: YES, OKAY, WHAT, MIDDLE, LEFT, PRESS, RIGHT, BLANK, READY, NO, FIRST, UHHH, NOTHING, WAIT

**Design Notes**:
- Two-stage lookup puzzle
- Heavily communication-dependent
- Requires: reading comprehension, large lookup tables
- Tests: clear verbal communication, patience

---

### 6. MEMORY MODULE

**Visual**: Display showing a number (1-4), four buttons labeled 1-4

**Interaction**: Press buttons across 5 stages based on rules AND previous answers

**Rules by Stage**:

#### Stage 1
| Display | Action |
|---------|--------|
| 1 | Press button in position 2 |
| 2 | Press button in position 2 |
| 3 | Press button in position 3 |
| 4 | Press button in position 4 |

#### Stage 2
| Display | Action |
|---------|--------|
| 1 | Press button labeled "4" |
| 2 | Press same POSITION as Stage 1 |
| 3 | Press button in position 1 |
| 4 | Press same POSITION as Stage 1 |

#### Stage 3
| Display | Action |
|---------|--------|
| 1 | Press button with same LABEL as Stage 2 |
| 2 | Press button with same LABEL as Stage 1 |
| 3 | Press button in position 3 |
| 4 | Press button labeled "4" |

#### Stage 4
| Display | Action |
|---------|--------|
| 1 | Press same POSITION as Stage 1 |
| 2 | Press button in position 1 |
| 3 | Press same POSITION as Stage 2 |
| 4 | Press same POSITION as Stage 2 |

#### Stage 5
| Display | Action |
|---------|--------|
| 1 | Press button with same LABEL as Stage 1 |
| 2 | Press button with same LABEL as Stage 2 |
| 3 | Press button with same LABEL as Stage 4 |
| 4 | Press button with same LABEL as Stage 3 |

**Design Notes**:
- Requires tracking history across stages
- Experts must record both position AND label of each answer
- Tests: memory, record keeping, attention to detail

---

### 7. MORSE CODE MODULE

**Visual**: Flashing light, frequency dial/display, TX button

**Interaction**: Decode morse signal, tune to correct frequency, transmit

**Mechanic**:
1. Light flashes a word in Morse code (repeating)
2. Identify the word
3. Tune to the frequency for that word
4. Press TX to transmit

**Word-Frequency Table**:

| Word | Frequency (MHz) |
|------|-----------------|
| shell | 3.505 |
| halls | 3.515 |
| slick | 3.522 |
| trick | 3.532 |
| boxes | 3.535 |
| leaks | 3.542 |
| strobe | 3.545 |
| bistro | 3.552 |
| flick | 3.555 |
| bombs | 3.565 |
| break | 3.572 |
| brick | 3.575 |
| steak | 3.582 |
| sting | 3.592 |
| vector | 3.595 |
| beats | 3.600 |

**Morse Code Reference**:
```
A: .-      N: -.
B: -...    O: ---
C: -.-.    P: .--.
D: -..     Q: --.-
E: .       R: .-.
F: ..-.    S: ...
G: --.     T: -
H: ....    U: ..-
I: ..      V: ...-
J: .---    W: .--
K: -.-     X: -..-
L: .-..    Y: -.--
M: --      Z: --..
```

**Design Notes**:
- Audio/visual decoding challenge
- Requires: Morse code knowledge or reference
- Tests: pattern recognition, patience, communication of dots/dashes

---

### 8. COMPLICATED WIRES MODULE

**Visual**: Wires with multiple properties (color, LED, star symbol)

**Interaction**: Cut or don't cut each wire based on properties

**Wire Properties**:
- Color: Red, Blue, Red+Blue (striped), or Neither (white)
- LED: Above wire is lit or unlit
- Star: ★ symbol present or absent

**Lookup Table**:

| Wire Color | LED | Star | Instruction |
|-----------|-----|------|-------------|
| White | Off | No | C (Cut) |
| White | Off | Yes | C (Cut) |
| White | On | No | D (Don't cut) |
| White | On | Yes | B (2+ batteries) |
| Red | Off | No | S (Serial even) |
| Red | Off | Yes | C (Cut) |
| Red | On | No | B (2+ batteries) |
| Red | On | Yes | B (2+ batteries) |
| Blue | Off | No | S (Serial even) |
| Blue | Off | Yes | D (Don't cut) |
| Blue | On | No | P (Parallel port) |
| Blue | On | Yes | P (Parallel port) |
| Red+Blue | Off | No | S (Serial even) |
| Red+Blue | Off | Yes | P (Parallel port) |
| Red+Blue | On | No | S (Serial even) |
| Red+Blue | On | Yes | D (Don't cut) |

**Instruction Key**:
- **C** = Cut the wire
- **D** = Do not cut the wire
- **S** = Cut if serial number last digit is even
- **P** = Cut if bomb has a parallel port
- **B** = Cut if bomb has 2 or more batteries

**Design Notes**:
- Multi-property evaluation
- Requires: visual properties + bomb metadata
- Tests: systematic checking, metadata lookup

---

### 9. WIRE SEQUENCES MODULE

**Visual**: Panels with colored wires connected to terminals A, B, or C

**Interaction**: Cut specific wires based on occurrence count and terminal

**Mechanic**:
- Module has multiple panels (navigate with up/down buttons)
- Track occurrence number of each wire color across ALL panels
- Cut wire only if its terminal matches the table for that occurrence

**Cut Tables**:

#### Red Wires
| Occurrence | Cut if connected to: |
|------------|---------------------|
| 1st | C |
| 2nd | B |
| 3rd | A |
| 4th | A or C |
| 5th | B |
| 6th | A or C |
| 7th | A, B, or C |
| 8th | A or B |
| 9th | B |

#### Blue Wires
| Occurrence | Cut if connected to: |
|------------|---------------------|
| 1st | B |
| 2nd | A or C |
| 3rd | B |
| 4th | A |
| 5th | B |
| 6th | B or C |
| 7th | C |
| 8th | A or C |
| 9th | A |

#### Black Wires
| Occurrence | Cut if connected to: |
|------------|---------------------|
| 1st | A, B, or C |
| 2nd | A or C |
| 3rd | B |
| 4th | A or C |
| 5th | B |
| 6th | B or C |
| 7th | A or B |
| 8th | C |
| 9th | C |

**Design Notes**:
- Cumulative tracking across panels
- Do NOT advance until all correct cuts are made on current panel
- Tests: counting, record keeping, patience

---

### 10. MAZES MODULE

**Visual**: Grid with a white square (player), red triangle (goal), two circles (identifiers)

**Interaction**: Navigate using arrow buttons without crossing invisible walls

**Mechanic**:
1. Find the two green circles on the module
2. Match to one of 9 predefined maze layouts
3. Navigate from white square to red triangle
4. Walls are INVISIBLE on the bomb but shown in manual

**The 9 Mazes** (identified by circle positions):
```
Each maze is a 6x6 grid with unique wall patterns
Circle positions uniquely identify which maze layout applies
```

**Design Notes**:
- Spatial reasoning and communication
- Requires: coordinate system, direction communication
- Tests: giving/following directions, spatial memory

---

### 11. PASSWORDS MODULE

**Visual**: 5 letter slots, each with up/down buttons to cycle letters, submit button

**Interaction**: Cycle through available letters to form a valid word, submit

**Valid Passwords** (35 words):
```
about  after  again  below  could
every  first  found  great  house
large  learn  never  other  place
plant  point  right  small  sound
spell  still  study  their  there
these  thing  think  three  water
where  which  world  would  write
```

**Solving Strategy**:
1. Defuser reads available letters for each position
2. Experts narrow down possible words
3. Find the one word that matches available letters

**Design Notes**:
- Word puzzle/deduction
- Process of elimination
- Tests: vocabulary, systematic elimination

---

## Needy Modules

Needy modules **cannot be permanently disarmed**. They have their own countdown timer and require periodic attention.

**Identification**: Small 2-digit timer in the top center of the module

**Behavior**:
- Activate during bomb defusal
- Must be tended to before their timer expires
- May reactivate at any time
- Failure to attend = strike

---

### VENTING GAS

**Visual**: Computer terminal with Y/N prompts

**Interaction**: Respond to prompts with Y (Yes) or N (No)

**Prompts and Responses**:
| Prompt | Response |
|--------|----------|
| "VENT GAS?" | Y |
| "DETONATE?" | N |

**Design Notes**:
- Attention/reading check
- Simple but requires vigilance
- Easy to panic and press wrong key

---

### CAPACITOR DISCHARGE

**Visual**: Capacitor gauge filling up, lever

**Interaction**: Hold the lever to discharge before overload

**Design Notes**:
- Pure attention requirement
- No decision making, just timely intervention
- Simulates maintaining attention while solving other modules

---

### KNOBS

**Visual**: Large knob, "UP" label, 12 LEDs in 2 rows of 6

**Interaction**: Rotate knob to correct position when timer hits zero

**LED Configurations** (X = lit):
```
UP Position:
  [ ][X][ ][X][X][ ]
  [X][X][X][X][ ][X]

DOWN Position:
  [ ][X][X][ ][ ][X]
  [X][X][X][X][ ][X]

LEFT Position:
  [ ][ ][ ][ ][X][ ]
  [X][ ][ ][X][X][X]

RIGHT Position:
  [X][ ][X][X][X][X]
  [X][X][X][ ][X][ ]
```

**Note**: Positions are relative to "UP" label, which may have rotated

**Design Notes**:
- Pattern recognition
- Time-critical (must be correct when timer hits zero)
- LED pattern changes between activations

---

## Bomb Metadata (Edgework)

Many modules require information from the bomb casing. This is collectively called "edgework."

### Serial Number
- Alphanumeric code (e.g., "AB3CD5")
- Located on the bomb casing
- Common checks:
  - Last digit odd/even
  - Contains a vowel (A, E, I, O, U)

### Batteries
- Found in battery holders on bomb sides
- Types: AA (small), D (large)
- Modules check: total battery count

### Indicators
- Labeled lights on bomb casing
- Can be LIT or UNLIT
- Common labels: SND, CLR, CAR, IND, FRQ, SIG, NSA, MSA, TRN, BOB, FRK

### Ports
- Digital/analog connectors on bomb casing
- Types:
  - DVI-D
  - Parallel
  - PS/2
  - RJ-45
  - Serial
  - Stereo RCA

---

## Difficulty Scaling

The game scales difficulty through multiple mechanisms:

### Time Pressure
- Shorter countdown timers
- Timer acceleration after strikes

### Module Complexity
- More modules per bomb
- More complex module types
- Needy modules adding distraction

### Strike Tolerance
- With indicator: 3 strikes allowed
- Without indicator: 1 strike allowed (instant fail)

### Edgework Complexity
- More metadata required
- More complex cross-referencing

### Communication Load
- Larger lookup tables
- More ambiguous symbols
- Sequential dependencies (Memory module)

---

## Game Modes

### Mission Mode
- Curated progression
- New modules introduced gradually  
- Story/narrative wrapper
- Increasing difficulty curve

### Free Play Mode
- Custom bomb configuration
- Choose modules, time, strikes
- Practice specific modules
- Set personal challenges

### Party/Local Multiplayer
- Multiple experts collaborating
- Rotate defuser role between rounds
- VR option for immersive defuser experience

---

## Platform Considerations

### Input Methods
- **PC**: Mouse/keyboard
- **Console**: Controller
- **Mobile**: Touch
- **VR**: Motion controllers, gaze, hand tracking

### Expert Experience
- Web-based manual (bombmanual.com)
- Printable PDF
- Can use any device to view manual
- Only defuser needs the game

### Multiplayer Architecture
- Local play (same room, verbal communication)
- Remote play (voice chat + screen share or trust)
- Only one game copy required

---

## Design Takeaways for Our Variation

### What Makes It Work
1. **Asymmetric information** forces communication
2. **Time pressure** creates tension without being impossible
3. **Escalating consequences** (strike = faster timer) adds stakes
4. **Modular design** allows mixing difficulty and variety
5. **Procedural generation** prevents memorization
6. **Simple interactions** with complex decision trees

### Module Design Principles
1. Visual element defuser describes
2. Decision tree expert navigates
3. Single correct action to perform
4. Clear success/failure feedback
5. May require bomb metadata for added complexity

### Communication Design
1. Information should be describable verbally
2. Avoid requiring perfect recall (allow re-reading)
3. Include some time-sensitive elements
4. Balance unique identification vs. ambiguity

---

*Document Version: 1.0*
*Based on Bomb Defusal Manual v1 (Verification Code: 241)*
*Source: https://keeptalkinggame.com / https://bombmanual.com*
