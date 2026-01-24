#!/usr/bin/env python3
"""
Music Generator for Fission Impossible
Uses ElevenLabs API to generate dynamic music tracks for different drama levels.

The game uses a layered music system where tracks can be crossfaded based on
the current tension level:
  - CALM: Normal operation, ambient monitoring
  - TENSE: Time pressure, some modules unsolved
  - CRITICAL: Low time, multiple strikes, near failure
  - VICTORY: All modules solved, success state
  - FAILURE: Meltdown imminent or occurred

Usage:
    pip install elevenlabs python-dotenv
    export ELEVENLABS_API_KEY=your_api_key_here
    python scripts/generate_music.py
"""

import os
import sys
from pathlib import Path
from dataclasses import dataclass
from typing import Optional
from enum import Enum

try:
    from elevenlabs import ElevenLabs
except ImportError:
    print("Please install elevenlabs: pip install elevenlabs")
    sys.exit(1)

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv is optional


class DramaLevel(Enum):
    """Drama levels for dynamic music system."""
    CALM = "calm"
    TENSE = "tense"
    CRITICAL = "critical"
    VICTORY = "victory"
    FAILURE = "failure"


@dataclass
class MusicTrack:
    """Definition of a music track to generate."""
    name: str
    prompt: str
    duration_ms: int
    drama_level: DramaLevel
    instrumental: bool = True
    category: str = "gameplay"


# ═══════════════════════════════════════════════════════════════════════════════
# Music Track Definitions
# ═══════════════════════════════════════════════════════════════════════════════
#
# Design philosophy for Fission Impossible dynamic music:
#
# The music should evoke a 1980s Cold War industrial atmosphere with:
# - Analog synthesizers (Moog, ARP, Oberheim)
# - Industrial/mechanical elements
# - Tension and unease even in "calm" states
# - Retro-futuristic tones reminiscent of John Carpenter, Tangerine Dream
# - Corporate muzak undertones (dystopian workplace vibes)
#
# All tracks are designed to loop seamlessly and crossfade between each other
# as the game state changes.
# ═══════════════════════════════════════════════════════════════════════════════

MUSIC_TRACKS = [
    # ═══════════════════════════════════════════════════════════════════════════
    # Main Gameplay Loops (60 seconds each for seamless looping)
    # ═══════════════════════════════════════════════════════════════════════════
    MusicTrack(
        name="gameplay_calm",
        prompt="""
        Atmospheric 1980s industrial ambient music with a slow tempo around 70 BPM.
        Features analog synthesizer pads with subtle pulsing and a deep bass drone.
        Incorporates sparse mechanical clicking and humming sounds integrated musically.
        Evokes late night monitoring atmosphere in an industrial facility.
        Steady, hypnotic, slightly unsettling but not urgent.
        Includes corporate muzak undertones and fluorescent light ambiance.
        Retro-futuristic vibe blending analog warmth with digital coldness.
        Inspired by pioneering electronic music with lush synth textures and immersive soundscapes.
        """,
        duration_ms=60000,  # 60 seconds
        drama_level=DramaLevel.CALM,
        category="gameplay",
    ),
    MusicTrack(
        name="gameplay_tense",
        prompt="""
        Tense 1980s synthwave industrial music. Medium tempo around 100 BPM.
        Driving analog synthesizer arpeggios, pulsing bass line.
        Building tension with layered synth pads, occasional stabs.
        Cold War thriller atmosphere, time pressure feeling.
        Influenced by John Carpenter's Escape from New York and The Thing.
        Mechanical percussion elements, industrial rhythm.
        Urgency building but still controlled, focused intensity.
        Retro analog synthesizers, Moog and ARP textures.
        """,
        duration_ms=60000,  # 60 seconds
        drama_level=DramaLevel.TENSE,
        category="gameplay",
    ),
    MusicTrack(
        name="gameplay_critical",
        prompt="""
        Intense 1980s industrial synth music with a fast tempo around 130 BPM.
        Aggressive analog synthesizer sequences and driving bass pulses.
        Creates an urgent, relentless atmosphere of high stakes action.
        Musical alarms evoke an emergency scenario requiring immediate action.
        Heavy industrial percussion and mechanical chaos throughout.
        Dissonant synth stabs build rising tension without resolution.
        Retro analog warmth blends with harsh digital edges.
        Rhythmically urgent yet still musical, reminiscent of classic 1980s thriller
        soundtracks with a focus on atmospheric and suspenseful electronic textures.
        """,
        duration_ms=60000,  # 60 seconds
        drama_level=DramaLevel.CRITICAL,
        category="gameplay",
    ),

    # Additional gameplay variation - training mode
    MusicTrack(
        name="gameplay_training",
        prompt="""
        Light 1980s tutorial music. Gentle tempo around 80 BPM.
        Friendly analog synthesizer melody, educational video vibes.
        Encouraging but slightly quirky, corporate training aesthetic.
        Simple patterns, not threatening, learning atmosphere.
        Warm synth pads, gentle arpeggios, no urgency.
        Like a nuclear safety training video from the 80s.
        Mildly unsettling undertone but mostly reassuring.
        Influenced by educational films and workplace orientation videos.
        """,
        duration_ms=60000,  # 60 seconds
        drama_level=DramaLevel.CALM,
        category="gameplay",
    ),
    
    # Longer gameplay loops for variety (90 seconds each)
    MusicTrack(
        name="gameplay_calm_alt",
        prompt="""
        Alternative calm 1980s ambient industrial. Slow tempo around 65 BPM.
        Different melodic motifs from main calm track.
        Deeper bass drones, more spacious arrangement.
        Night shift at the reactor, quiet monitoring.
        Influenced by Boards of Canada and early ambient electronica.
        Analog warmth, tape hiss texture, gentle pulsing.
        Peaceful but aware, something could happen any moment.
        Retro synthesizers, FM bell tones, soft percussion.
        """,
        duration_ms=90000,  # 90 seconds
        drama_level=DramaLevel.CALM,
        category="gameplay",
    ),
    MusicTrack(
        name="gameplay_tense_alt",
        prompt="""
        Alternative tense 1980s synthwave. Medium-fast tempo around 110 BPM.
        Different rhythmic pattern from main tense track.
        More melodic elements, synth lead lines.
        Chase sequence feeling, racing against time.
        Influenced by Kavinsky and modern synthwave.
        Driving bassline, crisp drums, soaring pads.
        Urgent but heroic, you can still do this.
        Retro arcade energy mixed with film score drama.
        """,
        duration_ms=90000,  # 90 seconds
        drama_level=DramaLevel.TENSE,
        category="gameplay",
    ),
    
    # Final countdown track for last 30 seconds
    MusicTrack(
        name="gameplay_final_countdown",
        prompt="""
        Extreme tension 1980s synth countdown. Very fast tempo around 140 BPM.
        Relentless ticking synthesizer patterns, heartbeat bass.
        Last moments before disaster, maximum intensity.
        Clock running out, every second counts.
        Influenced by action movie climaxes and thriller scores.
        Aggressive arpeggios, stabbing chords, rising pitch.
        No escape, pure adrenaline, do or die moment.
        Industrial chaos with melodic desperation.
        """,
        duration_ms=45000,  # 45 seconds
        drama_level=DramaLevel.CRITICAL,
        category="gameplay",
    ),

    # ═══════════════════════════════════════════════════════════════════════════
    # Outcome Stingers (One-shots for game end states)
    # ═══════════════════════════════════════════════════════════════════════════
    MusicTrack(
        name="victory_fanfare",
        prompt="""
        Triumphant 1980s synth victory music. Medium tempo around 90 BPM.
        Relieved, celebratory analog synthesizer melody.
        Major key resolution after tension, satisfying conclusion.
        Retro video game victory vibes mixed with corporate achievement jingle.
        Warm analog pads, bright arpeggios, gentle resolution.
        Like surviving a shift at a dangerous job, exhausted relief.
        Slightly ironic corporate success tone, muzak victory.
        Influenced by 80s movie endings and retro game completion themes.
        """,
        duration_ms=15000,  # 15 seconds
        drama_level=DramaLevel.VICTORY,
        category="stinger",
    ),
    MusicTrack(
        name="failure_doom",
        prompt="""
        Catastrophic 1980s industrial doom music. Slow descent, no set tempo.
        Nuclear meltdown in musical form, everything falling apart.
        Deep bass rumble, dissonant synthesizer collapse.
        Descending chromatic lines, inevitable doom atmosphere.
        Influenced by horror movie endings and industrial noise.
        Analog synthesizer death rattle, system failure sounds.
        Brief moment of silence then corporate jingle mockingly plays.
        Dark humor in catastrophe, ironic corporate optimism at the end.
        """,
        duration_ms=20000,  # 20 seconds
        drama_level=DramaLevel.FAILURE,
        category="stinger",
    ),

    # ═══════════════════════════════════════════════════════════════════════════
    # Menu / UI Music
    # ═══════════════════════════════════════════════════════════════════════════
    MusicTrack(
        name="menu_theme",
        prompt="""
        1980s corporate training video music. Medium tempo around 85 BPM.
        Cheesy synthesizer melody, faux-optimistic corporate jingle.
        Slightly unsettling undertone beneath the cheerfulness.
        Nuclear power plant promotional video aesthetic.
        Warm analog synth pads, simple arpeggios, gentle drums.
        "Welcome to NuHaus Nuclear" corporate branding vibes.
        Muzak meets John Carpenter, mundane horror.
        Retro-futuristic optimism masking workplace danger.
        Influenced by 80s educational videos and corporate training films.
        """,
        duration_ms=45000,  # 45 seconds
        drama_level=DramaLevel.CALM,
        category="menu",
    ),
    MusicTrack(
        name="briefing_music",
        prompt="""
        Serious 1980s briefing room music. Slow tempo around 60 BPM.
        Military industrial complex atmosphere, classified documents feeling.
        Deep analog synth pads, occasional radar ping sounds.
        Cold War tension, important mission ahead.
        Influenced by spy movie briefing scenes, WarGames aesthetic.
        Steady, ominous, building anticipation.
        Typewriter rhythms, computer terminal beeps integrated musically.
        Retro government facility ambiance, something important is happening.
        """,
        duration_ms=30000,  # 30 seconds
        drama_level=DramaLevel.CALM,
        category="menu",
    ),

    # ═══════════════════════════════════════════════════════════════════════════
    # Transition Stingers (Short musical phrases for state changes)
    # ═══════════════════════════════════════════════════════════════════════════
    MusicTrack(
        name="tension_rise",
        prompt="""
        Short 1980s synth tension riser. Building intensity over duration.
        Analog synthesizer sweep upward, increasing urgency.
        Like an alarm beginning, situation escalating.
        Industrial warning tone becoming musical.
        Quick transition from calm to tense state.
        Retro analog filter sweep, rising pitch.
        """,
        duration_ms=5000,  # 5 seconds
        drama_level=DramaLevel.TENSE,
        category="transition",
    ),
    MusicTrack(
        name="critical_alarm",
        prompt="""
        Short 1980s synth critical alert. Immediate high intensity.
        Aggressive analog synthesizer stab, urgent warning.
        Musical alarm, situation is now critical.
        Industrial klaxon made musical, panic trigger.
        Quick transition to emergency state.
        Retro analog aggression, harsh but musical.
        """,
        duration_ms=5000,  # 5 seconds
        drama_level=DramaLevel.CRITICAL,
        category="transition",
    ),
    MusicTrack(
        name="module_complete",
        prompt="""
        Short 1980s synth success chime. Positive resolution.
        Analog synthesizer ascending arpeggio, satisfying completion.
        Retro video game level complete sound, but industrial.
        Brief moment of relief, one step closer to safety.
        Quick positive feedback stinger.
        Warm analog tones, major key resolution.
        """,
        duration_ms=3000,  # 3 seconds
        drama_level=DramaLevel.CALM,
        category="transition",
    ),
    MusicTrack(
        name="strike_warning",
        prompt="""
        Short 1980s synth error tone. Negative feedback.
        Analog synthesizer descending dissonance, mistake made.
        Retro video game error sound, industrial warning.
        Brief moment of dread, things are getting worse.
        Quick negative feedback stinger.
        Harsh analog tones, minor key descent.
        """,
        duration_ms=3000,  # 3 seconds
        drama_level=DramaLevel.TENSE,
        category="transition",
    ),
    MusicTrack(
        name="tension_drop",
        prompt="""
        Short 1980s synth relief. Tension release.
        Analog synthesizer sweep downward, pressure releasing.
        Situation stabilizing, crisis averted for now.
        Filter closing, energy dissipating.
        Quick transition from tense to calmer state.
        Warm resolution, minor to major shift.
        """,
        duration_ms=4000,  # 4 seconds
        drama_level=DramaLevel.CALM,
        category="transition",
    ),
    MusicTrack(
        name="phase_transition",
        prompt="""
        Dramatic 1980s synth transition. Scene change.
        Industrial machinery powering up, systems activating.
        Like entering a new area in a video game.
        Brief build then release, new section beginning.
        Influenced by level transition sounds from 80s games.
        Synth whoosh, digital sparkle, mechanical clunk.
        """,
        duration_ms=3000,  # 3 seconds
        drama_level=DramaLevel.TENSE,
        category="transition",
    ),

    # ═══════════════════════════════════════════════════════════════════════════
    # Ambient Layers (For mixing with main tracks)
    # ═══════════════════════════════════════════════════════════════════════════
    MusicTrack(
        name="ambient_reactor_hum",
        prompt="""
        Deep industrial ambient drone. No tempo, continuous texture.
        Nuclear reactor room ambiance made musical.
        Low frequency synthesizer drone, subtle pulsing.
        Mechanical humming, electrical buzzing, processed musically.
        Background layer to mix under other tracks.
        Ominous but not overwhelming, constant presence.
        Analog warmth with industrial coldness.
        """,
        duration_ms=120000,  # 120 seconds (2 minutes for longer loop)
        drama_level=DramaLevel.CALM,
        category="ambient",
    ),
    MusicTrack(
        name="ambient_tension_bed",
        prompt="""
        Subtle tension ambient layer. No clear tempo, textural.
        Anxiety-inducing synthesizer textures, subliminal unease.
        Background layer to add tension to calm music.
        Processed industrial sounds, distant machinery.
        Barely perceptible but affects mood significantly.
        Analog synth textures, filtered noise, subtle movement.
        """,
        duration_ms=120000,  # 120 seconds (2 minutes for longer loop)
        drama_level=DramaLevel.TENSE,
        category="ambient",
    ),
]


def generate_music_tracks_list(
    tracks: list,
    output_dir: Path,
    api_key: Optional[str] = None,
    dry_run: bool = False,
    only_missing: bool = True,
    output_format: str = "mp3_44100_128",
):
    """
    Generate specified music tracks using ElevenLabs API.

    Args:
        tracks: List of MusicTrack objects to generate
        output_dir: Directory to save music files
        api_key: ElevenLabs API key (or use ELEVENLABS_API_KEY env var)
        dry_run: If True, just print what would be generated
        only_missing: If True, skip files that already exist
        output_format: Audio output format (default: mp3_44100_128)
    """
    api_key = api_key or os.getenv("ELEVENLABS_API_KEY")

    if not api_key and not dry_run:
        print("Error: ELEVENLABS_API_KEY environment variable not set")
        print("Set it with: export ELEVENLABS_API_KEY=your_key_here")
        sys.exit(1)

    output_dir.mkdir(parents=True, exist_ok=True)

    if not dry_run:
        client = ElevenLabs(api_key=api_key)

    print(f"{'='*70}")
    print(f"  Fission Impossible - Music Track Generator")
    print(f"{'='*70}")
    print(f"  Output directory: {output_dir}")
    print(f"  Total tracks: {len(tracks)}")
    print(f"  Output format: {output_format}")
    print(f"  Mode: {'DRY RUN' if dry_run else 'GENERATING'}")
    print(f"{'='*70}\n")

    # Calculate total duration
    total_duration_ms = sum(track.duration_ms for track in tracks)
    total_duration_min = total_duration_ms / 60000
    print(f"  Total music duration: {total_duration_min:.1f} minutes")
    print(f"{'='*70}\n")

    generated = 0
    skipped = 0
    failed = 0

    for i, track in enumerate(tracks, 1):
        # Determine file extension from output format
        ext = output_format.split("_")[0]
        output_path = output_dir / f"{track.name}.{ext}"

        # Skip if file exists with valid content and only_missing is True
        # Files under 1KB are considered empty/corrupt and will be regenerated
        if only_missing and output_path.exists():
            file_size = output_path.stat().st_size
            if file_size >= 1000:  # Valid file (at least 1KB)
                print(f"[{i:2}/{len(tracks)}] SKIP (exists): {track.name}")
                skipped += 1
                continue
            else:
                print(f"[{i:2}/{len(tracks)}] REGENERATE (empty/corrupt {file_size}B): {track.name}")

        duration_sec = track.duration_ms / 1000
        print(f"[{i:2}/{len(tracks)}] Generating: {track.name}")
        print(f"           Drama Level: {track.drama_level.value}")
        print(f"           Duration: {duration_sec:.0f}s | Category: {track.category}")
        print(f"           Prompt preview: {track.prompt[:60].strip()}...")

        if dry_run:
            print(f"           -> Would save to: {output_path}\n")
            generated += 1
            continue

        try:
            # Clean up the prompt (remove extra whitespace from multi-line strings)
            clean_prompt = " ".join(track.prompt.split())

            # Generate the music track
            audio_data = client.music.compose(
                prompt=clean_prompt,
                music_length_ms=track.duration_ms,
                model_id="music_v1",
                force_instrumental=track.instrumental,
                output_format=output_format,
            )

            # Write to file
            with open(output_path, "wb") as f:
                # Handle both generator and bytes response
                if hasattr(audio_data, '__iter__') and not isinstance(audio_data, bytes):
                    for chunk in audio_data:
                        f.write(chunk)
                else:
                    f.write(audio_data)

            print(f"           -> Saved: {output_path}\n")
            generated += 1

        except Exception as e:
            print(f"           -> FAILED: {e}\n")
            failed += 1

    print(f"{'='*70}")
    print(f"  Summary:")
    print(f"    Generated: {generated}")
    print(f"    Skipped:   {skipped}")
    print(f"    Failed:    {failed}")
    print(f"{'='*70}")


def generate_music_tracks(
    output_dir: Path,
    api_key: Optional[str] = None,
    dry_run: bool = False,
    only_missing: bool = True,
    output_format: str = "mp3_44100_128",
):
    """
    Generate all music tracks using ElevenLabs API.

    Args:
        output_dir: Directory to save music files
        api_key: ElevenLabs API key (or use ELEVENLABS_API_KEY env var)
        dry_run: If True, just print what would be generated
        only_missing: If True, skip files that already exist
        output_format: Audio output format (default: mp3_44100_128)
    """
    generate_music_tracks_list(
        tracks=MUSIC_TRACKS,
        output_dir=output_dir,
        api_key=api_key,
        dry_run=dry_run,
        only_missing=only_missing,
        output_format=output_format,
    )


def list_tracks():
    """Print a formatted list of all music tracks."""
    print(f"\n{'='*70}")
    print(f"  Music Tracks for Fission Impossible ({len(MUSIC_TRACKS)} total)")
    print(f"{'='*70}\n")

    # Group by category
    categories = {}
    for track in MUSIC_TRACKS:
        if track.category not in categories:
            categories[track.category] = []
        categories[track.category].append(track)

    # Calculate totals
    total_duration_ms = sum(track.duration_ms for track in MUSIC_TRACKS)

    for category, tracks in categories.items():
        cat_duration = sum(t.duration_ms for t in tracks)
        print(f"  {category.upper()} ({len(tracks)} tracks, {cat_duration/1000:.0f}s total)")
        print(f"  {'-'*60}")
        for track in tracks:
            duration_sec = track.duration_ms / 1000
            level = track.drama_level.value
            print(f"    {track.name:<25} {duration_sec:>5.0f}s  [{level:<8}]")
        print()

    print(f"  {'='*60}")
    print(f"  Total duration: {total_duration_ms/1000:.0f}s ({total_duration_ms/60000:.1f} minutes)")
    print(f"  {'='*60}\n")


def list_by_drama_level():
    """Print tracks organized by drama level."""
    print(f"\n{'='*70}")
    print(f"  Music Tracks by Drama Level")
    print(f"{'='*70}\n")

    for level in DramaLevel:
        tracks = [t for t in MUSIC_TRACKS if t.drama_level == level]
        if tracks:
            print(f"  {level.value.upper()}")
            print(f"  {'-'*50}")
            for track in tracks:
                duration_sec = track.duration_ms / 1000
                print(f"    {track.name:<25} {duration_sec:>5.0f}s  ({track.category})")
            print()


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate music tracks for Fission Impossible using ElevenLabs"
    )
    parser.add_argument(
        "--output", "-o",
        type=Path,
        default=Path("assets/audio/music"),
        help="Output directory for music files"
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
        help="List all music tracks"
    )
    parser.add_argument(
        "--by-level",
        action="store_true",
        help="List tracks organized by drama level"
    )
    parser.add_argument(
        "--single", "-s",
        type=str,
        help="Generate only a single track by name"
    )
    parser.add_argument(
        "--category", "-c",
        type=str,
        choices=["gameplay", "stinger", "menu", "transition", "ambient"],
        help="Generate only tracks in a specific category"
    )
    parser.add_argument(
        "--drama-level", "-d",
        type=str,
        choices=["calm", "tense", "critical", "victory", "failure"],
        help="Generate only tracks for a specific drama level"
    )
    parser.add_argument(
        "--format", "-f",
        type=str,
        default="mp3_44100_128",
        help="Output format (default: mp3_44100_128)"
    )

    args = parser.parse_args()

    if args.list:
        list_tracks()
        return

    if args.by_level:
        list_by_drama_level()
        return

    # Filter tracks based on arguments
    tracks_to_generate = MUSIC_TRACKS.copy()

    if args.single:
        tracks_to_generate = [t for t in tracks_to_generate if t.name == args.single]
        if not tracks_to_generate:
            print(f"Error: No music track named '{args.single}'")
            print("Use --list to see all available tracks")
            sys.exit(1)

    if args.category:
        tracks_to_generate = [t for t in tracks_to_generate if t.category == args.category]
        if not tracks_to_generate:
            print(f"Error: No tracks in category '{args.category}'")
            sys.exit(1)

    if args.drama_level:
        level = DramaLevel(args.drama_level)
        tracks_to_generate = [t for t in tracks_to_generate if t.drama_level == level]
        if not tracks_to_generate:
            print(f"Error: No tracks for drama level '{args.drama_level}'")
            sys.exit(1)

    generate_music_tracks_list(
        tracks=tracks_to_generate,
        output_dir=args.output,
        dry_run=args.dry_run,
        only_missing=not args.all,
        output_format=args.format,
    )


if __name__ == "__main__":
    main()
