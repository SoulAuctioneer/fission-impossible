#!/usr/bin/env python3
"""
Sound Effect Generator for Fission Impossible
Uses ElevenLabs API to generate retro terminal/nuclear themed sound effects.

Usage:
    pip install elevenlabs python-dotenv
    export ELEVENLABS_API_KEY=your_api_key_here
    python scripts/generate_sfx.py
"""

import os
import sys
from pathlib import Path
from dataclasses import dataclass
from typing import Optional

try:
    from elevenlabs.client import ElevenLabs
except ImportError:
    print("Please install elevenlabs: pip install elevenlabs")
    sys.exit(1)

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv is optional


@dataclass
class SoundEffect:
    """Definition of a sound effect to generate."""
    name: str
    prompt: str
    duration: float
    category: str
    loop: bool = False
    prompt_influence: float = 0.3


# All sound effects for the game
SOUND_EFFECTS = [
    # ═══════════════════════════════════════════════════════════════════════════
    # UI / Terminal Sounds
    # ═══════════════════════════════════════════════════════════════════════════
    SoundEffect(
        name="button_click",
        prompt="Retro computer keyboard key press, mechanical click, 1980s terminal, crisp",
        duration=0.5,
        category="ui",
    ),
    SoundEffect(
        name="button_hover",
        prompt="Soft electronic blip, subtle UI hover sound, vintage computer, gentle beep",
        duration=0.5,
        category="ui",
    ),
    SoundEffect(
        name="button_error",
        prompt="Error buzzer, wrong answer buzz, retro computer error beep, harsh",
        duration=0.5,
        category="ui",
    ),
    SoundEffect(
        name="terminal_boot",
        prompt="Old CRT monitor powering on, electrical hum building up, vintage computer startup, 1980s",
        duration=2.0,
        category="ui",
    ),
    SoundEffect(
        name="terminal_hum",
        prompt="CRT monitor electrical hum, steady ambient drone, old computer fan, subtle buzz",
        duration=5.0,
        category="ambient",
        loop=True,
    ),
    SoundEffect(
        name="keyboard_type",
        prompt="Single mechanical keyboard keystroke, IBM Model M style, clicky, vintage",
        duration=0.5,
        category="ui",
    ),
    SoundEffect(
        name="text_print",
        prompt="Dot matrix printer single character, old terminal text appearing, electronic chirp",
        duration=0.5,
        category="ui",
    ),
    SoundEffect(
        name="screen_static",
        prompt="TV static burst, CRT interference, white noise glitch, brief",
        duration=0.5,
        category="ui",
    ),
    SoundEffect(
        name="screen_flicker",
        prompt="Electrical flicker, fluorescent light buzz, power fluctuation, subtle crackle",
        duration=0.5,
        category="ui",
    ),

    # ═══════════════════════════════════════════════════════════════════════════
    # Game State Sounds
    # ═══════════════════════════════════════════════════════════════════════════
    SoundEffect(
        name="clock_in",
        prompt="Industrial time clock punch, mechanical stamp, factory clock in, satisfying click",
        duration=1.0,
        category="game",
    ),
    SoundEffect(
        name="module_solved",
        prompt="Positive chime, success sound, retro video game level complete, triumphant beep sequence",
        duration=1.5,
        category="game",
    ),
    SoundEffect(
        name="strike",
        prompt="Harsh alarm buzzer, wrong answer, industrial warning horn, error alert, tense",
        duration=1.0,
        category="game",
    ),
    SoundEffect(
        name="timer_tick",
        prompt="Clock tick, mechanical timer click, single tick sound, precise",
        duration=0.5,
        category="game",
    ),
    SoundEffect(
        name="timer_warning",
        prompt="Urgent beeping, low time warning, accelerating alarm beeps, tense countdown",
        duration=1.0,
        category="game",
    ),
    SoundEffect(
        name="timer_critical",
        prompt="Critical alarm, fast urgent beeping, emergency countdown, panic inducing beeps",
        duration=1.5,
        category="game",
    ),
    SoundEffect(
        name="reactor_stable",
        prompt="Triumphant success fanfare, reactor powering down safely, relieved tone, retro victory jingle",
        duration=3.0,
        category="game",
    ),
    SoundEffect(
        name="meltdown",
        prompt="Nuclear meltdown explosion, catastrophic failure, reactor core breach, massive boom, alarm sirens",
        duration=4.0,
        category="game",
    ),

    # ═══════════════════════════════════════════════════════════════════════════
    # Coolant Valves Module
    # ═══════════════════════════════════════════════════════════════════════════
    SoundEffect(
        name="wire_cut",
        prompt="Wire snipping sound, cable cutter cutting wire, electrical snap, crisp cut",
        duration=0.5,
        category="modules",
    ),
    SoundEffect(
        name="wire_correct",
        prompt="Correct wire confirmation, positive electronic chirp, success beep, relieving tone",
        duration=0.5,
        category="modules",
    ),

    # ═══════════════════════════════════════════════════════════════════════════
    # Emergency Override Module
    # ═══════════════════════════════════════════════════════════════════════════
    SoundEffect(
        name="button_hold",
        prompt="Button held down, sustained electronic tone, holding pressure, building charge sound",
        duration=2.0,
        category="modules",
    ),
    SoundEffect(
        name="button_release",
        prompt="Button released, spring mechanism release, pressure release click",
        duration=0.5,
        category="modules",
    ),
    SoundEffect(
        name="strip_fill",
        prompt="Progress bar filling, energy charging up, power meter rising, electronic buildup",
        duration=1.5,
        category="modules",
    ),
    SoundEffect(
        name="override_complete",
        prompt="Override sequence complete, system accepted, positive confirmation tone, mechanical lock engaging",
        duration=1.0,
        category="modules",
    ),

    # ═══════════════════════════════════════════════════════════════════════════
    # Vent Codes Module
    # ═══════════════════════════════════════════════════════════════════════════
    SoundEffect(
        name="symbol_select",
        prompt="Symbol selected, electronic blip, UI selection sound, digital click",
        duration=0.5,
        category="modules",
    ),
    SoundEffect(
        name="code_submit",
        prompt="Code submitted, enter key pressed, command sent, electronic whoosh",
        duration=0.5,
        category="modules",
    ),

    # ═══════════════════════════════════════════════════════════════════════════
    # Rod Alignment Module
    # ═══════════════════════════════════════════════════════════════════════════
    SoundEffect(
        name="rod_move",
        prompt="Soft mechanical slide, gentle servo motor, smooth hydraulic movement, quiet precision",
        duration=0.8,
        category="modules",
    ),
    SoundEffect(
        name="rod_lock",
        prompt="Positive confirmation click, satisfying lock-in sound, gentle success chime, soft mechanical snap",
        duration=0.5,
        category="modules",
    ),
    # Simon Says tones - ascending pitch (red=lowest, yellow=highest)
    SoundEffect(
        name="simon_tone_red",
        prompt="Electronic tone, Simon Says game sound, E3 note synthesizer beep, retro game tone, clean sine wave",
        duration=0.5,
        category="modules",
        prompt_influence=0.4,
    ),
    SoundEffect(
        name="simon_tone_blue",
        prompt="Electronic tone, Simon Says game sound, A3 note synthesizer beep, retro game tone, clean sine wave",
        duration=0.5,
        category="modules",
        prompt_influence=0.4,
    ),
    SoundEffect(
        name="simon_tone_green",
        prompt="Medium-high electronic tone, Simon Says game sound, C#4 note synthesizer beep, retro game tone, clean sine wave",
        duration=0.5,
        category="modules",
        prompt_influence=0.4,
    ),
    SoundEffect(
        name="simon_tone_yellow",
        prompt="High electronic tone, Simon Says game sound, E4 note synthesizer beep, retro game tone, clean sine wave",
        duration=0.5,
        category="modules",
        prompt_influence=0.4,
    ),

    # ═══════════════════════════════════════════════════════════════════════════
    # Pressure Locks Module
    # ═══════════════════════════════════════════════════════════════════════════
    SoundEffect(
        name="grid_move",
        prompt="Cursor moving on grid, light electronic beep, navigation sound, subtle blip",
        duration=0.5,
        category="modules",
    ),
    SoundEffect(
        name="marker_place",
        prompt="Marker placed, stamp sound, position confirmed, electronic thunk",
        duration=0.5,
        category="modules",
    ),
    SoundEffect(
        name="path_complete",
        prompt="Path traced successfully, sequence complete chime, positive confirmation melody",
        duration=1.0,
        category="modules",
    ),

    # ═══════════════════════════════════════════════════════════════════════════
    # Security Terminal Module
    # ═══════════════════════════════════════════════════════════════════════════
    SoundEffect(
        name="letter_scroll",
        prompt="Letter scrolling, mechanical dial turning, clicking through options, rotary encoder",
        duration=0.5,
        category="modules",
    ),
    SoundEffect(
        name="letter_lock",
        prompt="Letter locked in place, tumbler clicking, combination lock digit set",
        duration=0.5,
        category="modules",
    ),
    SoundEffect(
        name="word_submit",
        prompt="Word submitted for verification, access code entered, terminal processing",
        duration=0.5,
        category="modules",
    ),

    # ═══════════════════════════════════════════════════════════════════════════
    # Ambient / Atmosphere
    # ═══════════════════════════════════════════════════════════════════════════
    SoundEffect(
        name="reactor_hum",
        prompt="Nuclear reactor ambient hum, deep industrial drone, power plant background, ominous",
        duration=10.0,
        category="ambient",
        loop=True,
    ),
    SoundEffect(
        name="steam_release",
        prompt="Steam venting, pressure release valve, industrial hiss, pipe steam burst",
        duration=1.5,
        category="ambient",
    ),
    SoundEffect(
        name="geiger_click",
        prompt="Geiger counter clicking, radiation detector, sporadic clicks, ominous",
        duration=3.0,
        category="ambient",
    ),
    SoundEffect(
        name="alarm_siren",
        prompt="Nuclear plant warning siren, emergency klaxon, rotating alarm, industrial warning, but SLOW and mellow, not too loud or urgent",
        duration=3.0,
        category="ambient",
    ),
    SoundEffect(
        name="emergency_klaxon",
        prompt="Nuclear emergency klaxon alarm, loud pulsing siren, catastrophic warning horn, industrial disaster alert, continuous wailing alarm, Red Alert klaxon",
        duration=7.0,
        category="game",
        prompt_influence=0.4,
    ),
    SoundEffect(
        name="coolant_flow",
        prompt="Liquid coolant flowing through pipes, water rushing, industrial plumbing, steady flow",
        duration=5.0,
        category="ambient",
        loop=True,
    ),
]


def generate_sound_effects(
    output_dir: Path,
    api_key: Optional[str] = None,
    dry_run: bool = False,
    only_missing: bool = True,
):
    """
    Generate all sound effects using ElevenLabs API.
    
    Args:
        output_dir: Directory to save sound files
        api_key: ElevenLabs API key (or use ELEVENLABS_API_KEY env var)
        dry_run: If True, just print what would be generated
        only_missing: If True, skip files that already exist
    """
    api_key = api_key or os.getenv("ELEVENLABS_API_KEY")
    
    if not api_key and not dry_run:
        print("Error: ELEVENLABS_API_KEY environment variable not set")
        print("Set it with: export ELEVENLABS_API_KEY=your_key_here")
        sys.exit(1)
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    if not dry_run:
        client = ElevenLabs(api_key=api_key)
    
    print(f"{'='*60}")
    print(f"  Fission Impossible - Sound Effect Generator")
    print(f"{'='*60}")
    print(f"  Output directory: {output_dir}")
    print(f"  Total effects: {len(SOUND_EFFECTS)}")
    print(f"  Mode: {'DRY RUN' if dry_run else 'GENERATING'}")
    print(f"{'='*60}\n")
    
    generated = 0
    skipped = 0
    failed = 0
    
    for i, sfx in enumerate(SOUND_EFFECTS, 1):
        output_path = output_dir / f"{sfx.name}.mp3"
        
        # Skip if file exists and only_missing is True
        if only_missing and output_path.exists():
            print(f"[{i:2}/{len(SOUND_EFFECTS)}] SKIP (exists): {sfx.name}")
            skipped += 1
            continue
        
        print(f"[{i:2}/{len(SOUND_EFFECTS)}] Generating: {sfx.name}")
        print(f"           Prompt: {sfx.prompt[:60]}...")
        print(f"           Duration: {sfx.duration}s | Category: {sfx.category}")
        
        if dry_run:
            print(f"           -> Would save to: {output_path}\n")
            generated += 1
            continue
        
        try:
            # Generate the sound effect
            audio_generator = client.text_to_sound_effects.convert(
                text=sfx.prompt,
                duration_seconds=sfx.duration,
                prompt_influence=sfx.prompt_influence,
            )
            
            # Write to file (generator yields chunks)
            with open(output_path, "wb") as f:
                for chunk in audio_generator:
                    f.write(chunk)
            
            print(f"           -> Saved: {output_path}\n")
            generated += 1
            
        except Exception as e:
            print(f"           -> FAILED: {e}\n")
            failed += 1
    
    print(f"{'='*60}")
    print(f"  Summary:")
    print(f"    Generated: {generated}")
    print(f"    Skipped:   {skipped}")
    print(f"    Failed:    {failed}")
    print(f"{'='*60}")


def list_effects():
    """Print a formatted list of all sound effects."""
    print(f"\n{'='*70}")
    print(f"  Sound Effects for Fission Impossible ({len(SOUND_EFFECTS)} total)")
    print(f"{'='*70}\n")
    
    categories = {}
    for sfx in SOUND_EFFECTS:
        if sfx.category not in categories:
            categories[sfx.category] = []
        categories[sfx.category].append(sfx)
    
    for category, effects in categories.items():
        print(f"  {category.upper()} ({len(effects)} effects)")
        print(f"  {'-'*50}")
        for sfx in effects:
            loop_marker = " [LOOP]" if sfx.loop else ""
            print(f"    {sfx.name:<20} {sfx.duration:>4.1f}s{loop_marker}")
        print()


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Generate sound effects for Fission Impossible using ElevenLabs"
    )
    parser.add_argument(
        "--output", "-o",
        type=Path,
        default=Path("assets/audio/sfx"),
        help="Output directory for sound files"
    )
    parser.add_argument(
        "--dry-run", "-n",
        action="store_true",
        help="Don't generate, just show what would be done"
    )
    parser.add_argument(
        "--all", "-a",
        action="store_true",
        help="Regenerate all files, even if they exist"
    )
    parser.add_argument(
        "--list", "-l",
        action="store_true",
        help="Just list all sound effects"
    )
    parser.add_argument(
        "--single", "-s",
        type=str,
        help="Generate only a single effect by name"
    )
    
    args = parser.parse_args()
    
    if args.list:
        list_effects()
        return
    
    # Handle single effect generation
    if args.single:
        global SOUND_EFFECTS
        matching = [sfx for sfx in SOUND_EFFECTS if sfx.name == args.single]
        if not matching:
            print(f"Error: No sound effect named '{args.single}'")
            print("Use --list to see all available effects")
            sys.exit(1)
        SOUND_EFFECTS = matching
    
    generate_sound_effects(
        output_dir=args.output,
        dry_run=args.dry_run,
        only_missing=not args.all,
    )


if __name__ == "__main__":
    main()
