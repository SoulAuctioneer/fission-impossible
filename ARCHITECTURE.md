# Fission Impossible — Technical Architecture

## Requirements Analysis

### Core Requirements
| Requirement | Implication |
|-------------|-------------|
| 2D retro pixel graphics | Need excellent 2D rendering, pixel-perfect scaling, CRT shader effects |
| Cross-platform dev/deploy | Develop on MacOS, deploy on Windows |
| USB microcontroller support | Serial port communication with ESP32/Teensy/Arduino |
| Party game performance | Fast startup, responsive input, stable 60fps |
| AI-generated assets | Support for importing pixel art, audio files |
| Quick iteration | Easy to modify, add modules, tune gameplay |

### Future Requirements
| Requirement | Implication |
|-------------|-------------|
| Physical controls | Real-time bidirectional USB serial communication |
| Potential expansion | Multiplayer, networking, additional modules |
| Asset pipeline | Workflow for AI-generated → game-ready assets |

---

## Technology Options Evaluated

### Option 1: Godot 4 Engine

**Pros:**
- Excellent native 2D engine with pixel-perfect rendering
- Built-in shader language for CRT effects
- GDScript is Python-like, fast to develop
- Exports to Windows, MacOS, Linux natively
- Free, open source (MIT license)
- Active community, good documentation
- Scene system perfect for module architecture
- Built-in audio system with effects

**Cons:**
- USB serial requires GDExtension or external bridge
- Less familiar than web tech for some developers

**USB Solution:** GDExtension with libserialport, or bridge via local WebSocket/TCP to a small Rust/Python helper process.

### Option 2: Tauri + Web Canvas

**Pros:**
- Lightweight (much smaller than Electron)
- Rust backend perfect for USB serial (serialport crate)
- Web frontend familiar tech (HTML/CSS/JS/Canvas)
- Cross-platform
- Can use PixiJS or custom canvas for pixel rendering

**Cons:**
- Newer ecosystem, fewer game-specific resources
- Pixel-perfect rendering requires more manual work
- Shader effects need WebGL setup
- Less "game engine" tooling

**USB Solution:** Native in Rust backend via Tauri commands.

### Option 3: Electron + Web

**Pros:**
- Very familiar web tech
- node-serialport for USB
- Large ecosystem

**Cons:**
- Heavy resource usage (~150MB+ RAM)
- Slower startup
- Overkill for a game
- Pixel rendering still needs canvas/WebGL work

### Option 4: LÖVE (Love2D)

**Pros:**
- Purpose-built for 2D games
- Lua is simple
- Excellent pixel art support
- Fast, lightweight

**Cons:**
- USB serial is difficult (needs FFI/C extensions)
- Smaller ecosystem
- Distribution requires bundling

### Option 5: PyGame + Python

**Pros:**
- Python is very accessible
- pyserial for easy USB
- Good for prototyping

**Cons:**
- Distribution is painful (PyInstaller, etc.)
- Performance ceiling
- Not ideal for polished pixel art games

---

## Recommended Architecture: Godot 4 + Rust Bridge

After analysis, the recommended stack combines **Godot 4** for the game engine with a **Rust USB bridge** for microcontroller communication.

### Why This Combination?

| Aspect | Solution |
|--------|----------|
| **Game Engine** | Godot 4 — best-in-class 2D, pixel-perfect, shaders, cross-platform |
| **USB Communication** | Rust helper process — reliable, safe, cross-platform serial |
| **Bridge Protocol** | WebSocket or local TCP — clean separation, debuggable |
| **Asset Pipeline** | AI generation → post-processing → Godot import |

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           FISSION IMPOSSIBLE                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                         GODOT 4 ENGINE                               │   │
│  │                                                                      │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │   │
│  │  │    SCENES    │  │   MODULES    │  │    AUDIO     │              │   │
│  │  │              │  │              │  │              │              │   │
│  │  │ • StartScene │  │ • Coolant    │  │ • SFX        │              │   │
│  │  │ • GameScene  │  │ • Override   │  │ • Music      │              │   │
│  │  │ • EndScene   │  │ • VentCodes  │  │ • Ambient    │              │   │
│  │  │              │  │ • Rods       │  │              │              │   │
│  │  │              │  │ • Pressure   │  │              │              │   │
│  │  │              │  │ • Terminal   │  │              │              │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘              │   │
│  │                                                                      │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │   │
│  │  │   SHADERS    │  │ GAME STATE   │  │  USB CLIENT  │              │   │
│  │  │              │  │              │  │              │              │   │
│  │  │ • CRT Effect │  │ • Timer      │  │ • WebSocket  │◄─────┐       │   │
│  │  │ • Scanlines  │  │ • Strikes    │  │   Client     │      │       │   │
│  │  │ • Glow       │  │ • Modules    │  │              │      │       │   │
│  │  │ • Vignette   │  │ • Edgework   │  │              │      │       │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘      │       │   │
│  │                                                             │       │   │
│  └─────────────────────────────────────────────────────────────│───────┘   │
│                                                                 │           │
│                                         WebSocket (localhost)   │           │
│                                                                 │           │
│  ┌──────────────────────────────────────────────────────────────▼───────┐  │
│  │                      RUST USB BRIDGE (Optional)                       │  │
│  │                                                                       │  │
│  │  ┌────────────────┐    ┌────────────────┐    ┌────────────────┐     │  │
│  │  │   WebSocket    │    │  Serial Port   │    │    Protocol    │     │  │
│  │  │    Server      │◄──►│   Manager      │◄──►│    Handler     │     │  │
│  │  │ (localhost)    │    │ (serialport)   │    │   (JSON/SLIP)  │     │  │
│  │  └────────────────┘    └────────────────┘    └────────────────┘     │  │
│  │                                                      │               │  │
│  └──────────────────────────────────────────────────────│───────────────┘  │
│                                                         │                   │
│                                                   USB Serial                │
│                                                         │                   │
│  ┌──────────────────────────────────────────────────────▼───────────────┐  │
│  │                    MICROCONTROLLER (Future)                           │  │
│  │                                                                       │  │
│  │    ESP32 / Teensy / Arduino                                          │  │
│  │    • Physical switches, buttons, knobs                               │  │
│  │    • LED indicators                                                   │  │
│  │    • Haptic feedback                                                  │  │
│  │                                                                       │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Godot 4 Project Structure

```
fission-impossible/
├── project.godot                    # Godot project file
├── export_presets.cfg               # Export settings (Windows, MacOS)
│
├── assets/
│   ├── sprites/
│   │   ├── ui/                      # UI elements, buttons, frames
│   │   ├── modules/                 # Module-specific sprites
│   │   ├── effects/                 # Particles, animations
│   │   └── symbols/                 # Keypad symbols, indicators
│   ├── audio/
│   │   ├── sfx/                     # Sound effects
│   │   ├── music/                   # Background music/drones
│   │   └── voice/                   # Safety Salamander, announcements
│   ├── fonts/
│   │   ├── terminal.ttf             # CRT terminal font
│   │   └── display.ttf              # 7-segment display font
│   └── shaders/
│       ├── crt.gdshader             # CRT screen effect
│       ├── scanlines.gdshader       # Scanline overlay
│       └── glow.gdshader            # Indicator glow effect
│
├── scenes/
│   ├── main.tscn                    # Entry point, scene manager
│   ├── start_screen.tscn            # Clock-in terminal
│   ├── game_screen.tscn             # Main control panel
│   ├── end_screen_win.tscn          # Success screen
│   ├── end_screen_lose.tscn         # Failure screen
│   │
│   ├── modules/                     # Module scenes (instanced in game_screen)
│   │   ├── coolant_valves.tscn
│   │   ├── emergency_override.tscn
│   │   ├── vent_codes.tscn
│   │   ├── rod_alignment.tscn
│   │   ├── pressure_locks.tscn
│   │   └── security_terminal.tscn
│   │
│   └── components/                  # Reusable UI components
│       ├── reactor_status.tscn      # Timer, strikes, temp gauge
│       ├── module_frame.tscn        # Standard module container
│       ├── indicator_led.tscn       # Reusable LED indicator
│       └── seven_segment.tscn       # Digital display component
│
├── scripts/
│   ├── autoload/
│   │   ├── game_state.gd            # Global game state (autoload singleton)
│   │   ├── audio_manager.gd         # Sound effect management
│   │   └── usb_bridge.gd            # WebSocket client for USB (autoload)
│   │
│   ├── scenes/
│   │   ├── start_screen.gd
│   │   ├── game_screen.gd
│   │   └── end_screen.gd
│   │
│   ├── modules/
│   │   ├── module_base.gd           # Base class for all modules
│   │   ├── coolant_valves.gd
│   │   ├── emergency_override.gd
│   │   ├── vent_codes.gd
│   │   ├── rod_alignment.gd
│   │   ├── pressure_locks.gd
│   │   └── security_terminal.gd
│   │
│   └── utils/
│       ├── edgework_generator.gd    # Generate serial, batteries, etc.
│       └── module_solver.gd         # Validation logic for modules
│
└── docs/
    ├── GAME_REFERENCE.md
    ├── THEME.md
    ├── DESIGN.md
    └── ARCHITECTURE.md
```

---

## Module Architecture

Each module follows a consistent pattern using Godot's scene/script inheritance.

### Base Module Class

```gdscript
# scripts/modules/module_base.gd
class_name ModuleBase
extends Control

signal solved
signal strike

@export var module_name: String = "Unknown Module"
@export var solved_text: String = "COMPLETE"

var is_solved: bool = false
var is_active: bool = true

@onready var status_led: TextureRect = $StatusLED
@onready var status_label: Label = $StatusLabel

func _ready():
    _initialize_module()

# Override in subclasses
func _initialize_module():
    pass

# Override in subclasses  
func _generate_puzzle():
    pass

func mark_solved():
    if is_solved:
        return
    is_solved = true
    is_active = false
    status_led.modulate = Color.GREEN
    status_label.text = solved_text
    emit_signal("solved")
    _play_success_sound()

func record_strike():
    emit_signal("strike")
    _play_strike_sound()
    _flash_error()

func _play_success_sound():
    AudioManager.play_sfx("module_success")

func _play_strike_sound():
    AudioManager.play_sfx("strike")

func _flash_error():
    # Visual feedback for error
    var tween = create_tween()
    tween.tween_property(self, "modulate", Color.RED, 0.1)
    tween.tween_property(self, "modulate", Color.WHITE, 0.1)
    tween.set_loops(2)
```

### Example Module Implementation

```gdscript
# scripts/modules/coolant_valves.gd
extends ModuleBase

var wire_count: int
var wire_colors: Array[String]
var correct_wire: int

@onready var wires_container: VBoxContainer = $WiresContainer

func _initialize_module():
    module_name = "Coolant Valves"
    solved_text = "FLOW NOMINAL"
    _generate_puzzle()

func _generate_puzzle():
    # Randomly generate 3-6 wires
    wire_count = randi_range(3, 6)
    wire_colors = []
    
    var possible_colors = ["red", "blue", "yellow", "white", "black"]
    
    for i in range(wire_count):
        wire_colors.append(possible_colors.pick_random())
    
    correct_wire = _calculate_correct_wire()
    _create_wire_visuals()

func _calculate_correct_wire() -> int:
    var serial = GameState.edgework.serial_number
    var last_digit_odd = int(serial[-1]) % 2 == 1
    
    match wire_count:
        3:
            return _solve_three_wires(last_digit_odd)
        4:
            return _solve_four_wires(last_digit_odd)
        5:
            return _solve_five_wires(last_digit_odd)
        6:
            return _solve_six_wires(last_digit_odd)
    return 0

func _solve_three_wires(odd: bool) -> int:
    if not "red" in wire_colors:
        return 1  # Second wire (0-indexed: 1)
    elif wire_colors[-1] == "white":
        return wire_count - 1  # Last wire
    elif wire_colors.count("blue") > 1:
        return _last_index_of("blue")
    else:
        return wire_count - 1

# ... additional solving logic ...

func _on_wire_clicked(wire_index: int):
    if not is_active:
        return
    
    # Visual: "cut" the wire
    _animate_cut(wire_index)
    
    if wire_index == correct_wire:
        mark_solved()
    else:
        record_strike()
```

---

## Game State Management

```gdscript
# scripts/autoload/game_state.gd
extends Node

signal game_started
signal game_ended(success: bool)
signal strike_recorded(total_strikes: int)
signal module_solved(remaining: int)
signal time_updated(seconds_remaining: float)

# Game configuration
const STARTING_TIME: float = 300.0  # 5 minutes
const MAX_STRIKES: int = 3
const TIME_PENALTY_MULTIPLIER: float = 0.9  # Timer speeds up 10% per strike

# Current game state
var is_game_active: bool = false
var time_remaining: float = STARTING_TIME
var current_strikes: int = 0
var modules_remaining: int = 6
var time_multiplier: float = 1.0

# Edgework (bomb metadata)
var edgework: Dictionary = {
    "serial_number": "",
    "batteries": 0,
    "indicators": {},  # {"CAR": true, "FRK": false, ...}
    "has_parallel_port": false
}

func start_game():
    _reset_state()
    _generate_edgework()
    is_game_active = true
    emit_signal("game_started")

func _reset_state():
    time_remaining = STARTING_TIME
    current_strikes = 0
    modules_remaining = 6
    time_multiplier = 1.0
    is_game_active = false

func _generate_edgework():
    # Serial number: 2 letters, 1 digit, 2 letters, 1 digit
    var letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    var digits = "0123456789"
    
    edgework.serial_number = ""
    edgework.serial_number += letters[randi() % 26]
    edgework.serial_number += letters[randi() % 26]
    edgework.serial_number += digits[randi() % 10]
    edgework.serial_number += letters[randi() % 26]
    edgework.serial_number += letters[randi() % 26]
    edgework.serial_number += digits[randi() % 10]
    
    edgework.batteries = randi_range(0, 4)
    
    edgework.indicators = {
        "CAR": randf() > 0.5,
        "FRK": randf() > 0.5,
        "SIG": randf() > 0.5,
        "BOB": randf() > 0.5
    }
    
    edgework.has_parallel_port = randf() > 0.5

func _process(delta):
    if is_game_active:
        time_remaining -= delta * time_multiplier
        emit_signal("time_updated", time_remaining)
        
        if time_remaining <= 0:
            _game_over(false)

func record_strike():
    current_strikes += 1
    time_multiplier *= TIME_PENALTY_MULTIPLIER  # Speed up timer
    emit_signal("strike_recorded", current_strikes)
    
    if current_strikes >= MAX_STRIKES:
        _game_over(false)

func module_completed():
    modules_remaining -= 1
    emit_signal("module_solved", modules_remaining)
    
    if modules_remaining <= 0:
        _game_over(true)

func _game_over(success: bool):
    is_game_active = false
    emit_signal("game_ended", success)
```

---

## USB Bridge Architecture (Future)

The USB bridge is a separate Rust process that handles serial communication with microcontrollers.

### Bridge Project Structure

```
usb-bridge/
├── Cargo.toml
├── src/
│   ├── main.rs              # Entry point, CLI
│   ├── serial.rs            # Serial port management
│   ├── websocket.rs         # WebSocket server
│   ├── protocol.rs          # Message protocol (JSON)
│   └── device.rs            # Device abstraction
└── README.md
```

### Communication Protocol

```json
// Godot → Bridge: Request physical state
{
    "type": "get_state",
    "device": "control_panel"
}

// Bridge → Godot: Physical input event
{
    "type": "input",
    "device": "control_panel",
    "event": "button_press",
    "data": {
        "button_id": 3,
        "state": "pressed"
    }
}

// Godot → Bridge: Set physical output
{
    "type": "output",
    "device": "control_panel",
    "command": "set_led",
    "data": {
        "led_id": 0,
        "color": [255, 0, 0],
        "brightness": 1.0
    }
}

// Bridge → Godot: Device connected/disconnected
{
    "type": "device_status",
    "device": "control_panel",
    "connected": true,
    "port": "COM3"
}
```

### Godot USB Client

```gdscript
# scripts/autoload/usb_bridge.gd
extends Node

signal device_connected(device_name: String)
signal device_disconnected(device_name: String)
signal input_received(device: String, event: String, data: Dictionary)

var _socket: WebSocketPeer
var _connected: bool = false

const BRIDGE_URL = "ws://localhost:9876"

func _ready():
    _socket = WebSocketPeer.new()

func connect_to_bridge():
    var err = _socket.connect_to_url(BRIDGE_URL)
    if err != OK:
        push_warning("USB Bridge not available - running without physical controls")

func _process(_delta):
    if _socket.get_ready_state() == WebSocketPeer.STATE_OPEN:
        _socket.poll()
        while _socket.get_available_packet_count() > 0:
            var packet = _socket.get_packet()
            _handle_message(packet.get_string_from_utf8())

func _handle_message(json_string: String):
    var data = JSON.parse_string(json_string)
    if data == null:
        return
    
    match data.get("type"):
        "input":
            emit_signal("input_received", 
                data.get("device"), 
                data.get("event"), 
                data.get("data", {}))
        "device_status":
            if data.get("connected"):
                emit_signal("device_connected", data.get("device"))
            else:
                emit_signal("device_disconnected", data.get("device"))

func send_output(device: String, command: String, data: Dictionary):
    if _socket.get_ready_state() != WebSocketPeer.STATE_OPEN:
        return
    
    var message = {
        "type": "output",
        "device": device,
        "command": command,
        "data": data
    }
    _socket.send_text(JSON.stringify(message))
```

---

## Asset Pipeline

### AI-Generated Assets Workflow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           ASSET PIPELINE                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   ┌─────────────┐      ┌─────────────┐      ┌─────────────┐               │
│   │   PROMPT    │      │  AI TOOL    │      │  RAW OUTPUT │               │
│   │  CREATION   │ ───► │  GENERATION │ ───► │             │               │
│   └─────────────┘      └─────────────┘      └─────────────┘               │
│         │                                          │                       │
│         │              SPRITES                     │                       │
│         │              ════════                    ▼                       │
│         │                              ┌─────────────────┐                │
│         │                              │  POST-PROCESS   │                │
│         │                              │                 │                │
│         │                              │ • Downscale to  │                │
│         │                              │   pixel art     │                │
│         │                              │ • Color palette │                │
│         │                              │   reduction     │                │
│         │                              │ • Manual        │                │
│         │                              │   touch-up      │                │
│         │                              └────────┬────────┘                │
│         │                                       │                          │
│         │                                       ▼                          │
│         │                              ┌─────────────────┐                │
│         │                              │  GODOT IMPORT   │                │
│         │                              │                 │                │
│         │                              │ • .import file  │                │
│         │                              │ • Texture flags │                │
│         │                              │ • Atlas setup   │                │
│         │                              └─────────────────┘                │
│         │                                                                  │
│         │              AUDIO                                               │
│         │              ═════                                               │
│         │                                                                  │
│         │   ┌─────────────┐      ┌─────────────┐      ┌─────────────┐    │
│         └──►│ ELEVENLABS  │ ───► │  NORMALIZE  │ ───► │    GODOT    │    │
│             │ / SUNO      │      │  & PROCESS  │      │   IMPORT    │    │
│             │             │      │             │      │             │    │
│             │ • SFX       │      │ • Audacity  │      │ • .wav/.ogg │    │
│             │ • Music     │      │ • Level     │      │ • Bus setup │    │
│             │ • Voice     │      │ • Trim      │      │             │    │
│             └─────────────┘      └─────────────┘      └─────────────┘    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Sprite Specifications

| Asset Type | Resolution | Format | Notes |
|------------|------------|--------|-------|
| Module backgrounds | 256×256 | PNG | Pixel art, indexed color |
| UI buttons | 64×64 | PNG | Multiple states (normal, hover, pressed) |
| Symbols/icons | 32×32 | PNG | Crisp edges, limited palette |
| Wire sprites | 16×256 | PNG | Tileable, color variants |
| LED indicators | 16×16 | PNG | Glow effect in shader |
| Fonts | Vector→Bitmap | TTF/BMFont | Convert to bitmap for pixel look |

### Pixel Art Import Settings (Godot)

```gdscript
# Typical .import settings for pixel art
[remap]
importer="texture"
type="CompressedTexture2D"

[params]
compress/mode=0          # Lossless
mipmaps/generate=false   # No mipmaps for pixel art
roughness/mode=0
process/fix_alpha_border=false
process/premult_alpha=false
process/normal_map_invert_y=false
flags/repeat=0
flags/filter=false       # CRITICAL: Nearest neighbor filtering
```

### Audio Specifications

| Asset Type | Format | Sample Rate | Notes |
|------------|--------|-------------|-------|
| SFX (short) | WAV | 44.1kHz | Mono, 16-bit |
| SFX (loops) | OGG | 44.1kHz | Seamless loop points |
| Music | OGG | 44.1kHz | Stereo, loopable |
| Voice lines | WAV | 22.05kHz | Mono, slight lo-fi process |

---

## Shader Effects

### CRT Screen Effect

```glsl
// assets/shaders/crt.gdshader
shader_type canvas_item;

uniform float scanline_intensity: hint_range(0.0, 1.0) = 0.3;
uniform float curvature: hint_range(0.0, 0.1) = 0.02;
uniform float vignette_intensity: hint_range(0.0, 1.0) = 0.4;
uniform float noise_intensity: hint_range(0.0, 0.1) = 0.02;
uniform float chromatic_aberration: hint_range(0.0, 0.01) = 0.002;

vec2 curve(vec2 uv) {
    uv = uv * 2.0 - 1.0;
    vec2 offset = abs(uv.yx) / vec2(6.0, 4.0);
    uv = uv + uv * offset * offset * curvature;
    uv = uv * 0.5 + 0.5;
    return uv;
}

float random(vec2 co) {
    return fract(sin(dot(co.xy, vec2(12.9898, 78.233))) * 43758.5453);
}

void fragment() {
    vec2 uv = curve(UV);
    
    // Out of bounds check
    if (uv.x < 0.0 || uv.x > 1.0 || uv.y < 0.0 || uv.y > 1.0) {
        COLOR = vec4(0.0, 0.0, 0.0, 1.0);
        return;
    }
    
    // Chromatic aberration
    float r = texture(TEXTURE, uv + vec2(chromatic_aberration, 0.0)).r;
    float g = texture(TEXTURE, uv).g;
    float b = texture(TEXTURE, uv - vec2(chromatic_aberration, 0.0)).b;
    vec3 col = vec3(r, g, b);
    
    // Scanlines
    float scanline = sin(uv.y * 800.0) * scanline_intensity;
    col -= scanline;
    
    // Vignette
    float vignette = uv.x * uv.y * (1.0 - uv.x) * (1.0 - uv.y);
    vignette = clamp(pow(vignette * 16.0, vignette_intensity), 0.0, 1.0);
    col *= vignette;
    
    // Noise
    float noise = random(uv + vec2(TIME * 0.01, 0.0)) * noise_intensity;
    col += noise;
    
    COLOR = vec4(col, 1.0);
}
```

---

## Build & Distribution

### Development Workflow

```bash
# MacOS Development
# ─────────────────

# Install Godot 4 (via Homebrew or direct download)
brew install --cask godot

# Open project
godot --editor project.godot

# Run game (from CLI)
godot --path . --debug

# USB Bridge (when ready)
cd usb-bridge
cargo run
```

### Export Configuration

**Windows Export (from MacOS):**
1. Download Windows export templates in Godot
2. Configure export preset for Windows Desktop
3. Enable executable signing (optional, prevents AV false positives)

```ini
# export_presets.cfg
[preset.0]
name="Windows Desktop"
platform="Windows Desktop"
runnable=true
export_filter="all_resources"
include_filter=""
exclude_filter=""
export_path="builds/windows/FissionImpossible.exe"

[preset.0.options]
binary_format/embed_pck=true
texture_format/bptc=true
texture_format/s3tc=true
texture_format/etc=false
texture_format/etc2=false
application/icon="res://assets/icon.ico"
application/console_wrapper=false
```

### Distribution Package

```
FissionImpossible-v1.0-win64/
├── FissionImpossible.exe        # Main executable (includes .pck)
├── usb-bridge.exe               # Optional: USB bridge process
├── README.txt                   # Basic instructions
└── manual/
    └── index.html               # Operations manual (offline copy)
```

---

## Development Phases

### Phase 1: Core Game (MVP)
- [ ] Project setup, folder structure
- [ ] Start screen (terminal aesthetic)
- [ ] Game screen layout (control panel)
- [ ] Timer and strike system
- [ ] 2 simple modules (Coolant Valves, Security Terminal)
- [ ] End screens (win/lose)
- [ ] Basic audio (SFX only)
- [ ] CRT shader effect

### Phase 2: Full Module Set
- [ ] Remaining 4 modules
- [ ] Edgework display (serial, batteries, indicators)
- [ ] Module randomization
- [ ] Visual polish (animations, transitions)
- [ ] Full audio (music, ambient, voice)
- [ ] Operations Manual (web version)

### Phase 3: Polish & Effects
- [ ] All pixel art assets finalized
- [ ] Screen shake, particles
- [ ] Status messages system
- [ ] Difficulty settings
- [ ] QR code for manual

### Phase 4: USB Integration
- [ ] Rust USB bridge
- [ ] WebSocket communication
- [ ] Physical control mapping
- [ ] LED feedback
- [ ] Testing with ESP32/Teensy

### Phase 5: Distribution
- [ ] Windows build testing
- [ ] Installer/packaging
- [ ] Documentation
- [ ] Party testing

---

## Summary

| Component | Technology | Rationale |
|-----------|------------|-----------|
| **Game Engine** | Godot 4 | Best 2D engine, cross-platform, free |
| **Language** | GDScript | Fast iteration, Python-like |
| **Graphics** | Pixel art + shaders | Retro aesthetic with CRT effects |
| **Audio** | Godot AudioStreamPlayer | Built-in, supports buses/effects |
| **USB Bridge** | Rust + WebSocket | Safe, fast, cross-platform serial |
| **Assets** | DALL-E 3, ElevenLabs | AI-generated, post-processed |
| **Manual** | HTML (static) | Accessible on any device |
| **Distribution** | Godot export | Single .exe with embedded assets |

This architecture provides:
- **Fast development** with GDScript
- **Beautiful pixel graphics** with native 2D rendering
- **Authentic retro feel** with CRT shaders
- **Future-proof USB support** via bridge process
- **Easy cross-platform** builds

---

*Document Version: 1.0*
*Classification: INTERNAL — Development Team*
