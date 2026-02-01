#!/usr/bin/env python3
"""
Generate pad sound samples for the Resonance Chamber module.
Outputs WAV files (pad_48.wav ... pad_72.wav) to assets/audio/pads/.
Uses numpy for synthesis; no external encoder required.

Usage:
    pip install numpy
    python scripts/generate_pads.py
"""
import math
import struct
import wave
from pathlib import Path

try:
    import numpy as np
except ImportError:
    print("Please install numpy: pip install numpy")
    raise SystemExit(1)

# Output directory (repo root = parent of scripts/)
REPO_ROOT = Path(__file__).resolve().parent.parent
PADS_DIR = REPO_ROOT / "assets" / "audio" / "pads"

SAMPLE_RATE = 22050
DURATION_SEC = 0.45
# Soft pad: sine with attack/decay envelope
ATTACK_SEC = 0.05
DECAY_SEC = 0.35


def midi_to_freq(midi: int) -> float:
    """Convert MIDI note number to frequency (A4 = 440 Hz)."""
    return 440.0 * (2.0 ** ((midi - 69) / 12.0))


def generate_pad_tone(midi: int) -> bytes:
    """Generate mono 16-bit WAV bytes for a pad hit at the given MIDI note."""
    freq = midi_to_freq(midi)
    n_samples = int(SAMPLE_RATE * DURATION_SEC)
    t = np.linspace(0, DURATION_SEC, n_samples, dtype=np.float32)
    # Sine wave
    sig = np.sin(2 * math.pi * freq * t).astype(np.float32)
    # Soft envelope: attack then decay
    attack_n = int(SAMPLE_RATE * ATTACK_SEC)
    decay_n = int(SAMPLE_RATE * DECAY_SEC)
    env = np.ones(n_samples, dtype=np.float32)
    if attack_n > 0:
        env[:attack_n] = np.linspace(0, 1, attack_n)
    if decay_n > 0 and attack_n < n_samples:
        decay_start = attack_n
        decay_end = min(decay_start + decay_n, n_samples)
        decay_len = decay_end - decay_start
        env[decay_start:decay_end] = np.linspace(1, 0, decay_len)
        if decay_end < n_samples:
            env[decay_end:] = 0
    sig *= env
    # Normalize and convert to 16-bit
    peak = np.max(np.abs(sig))
    if peak > 0:
        sig = sig / peak * 0.7
    samples_int = (sig * 32767).astype(np.int16)
    return samples_int.tobytes()


def main():
    PADS_DIR.mkdir(parents=True, exist_ok=True)
    # MIDI 48 (C3) to 72 (C5) for Resonance Chamber note ranges
    for midi in range(48, 73):
        out_path = PADS_DIR / f"pad_{midi}.wav"
        data = generate_pad_tone(midi)
        with wave.open(str(out_path), "wb") as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(SAMPLE_RATE)
            wav.writeframes(data)
        print(f"Wrote {out_path}")
    print(f"Done. Generated {73 - 48} pad samples in {PADS_DIR}")


if __name__ == "__main__":
    main()
