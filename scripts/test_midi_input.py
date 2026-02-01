#!/usr/bin/env python3
"""
Quick MIDI input test: prints MIDI note number and name when you press keys.
Run: pip install mido python-rtmidi && python scripts/test_midi_input.py
Press keys on your MIDI keyboard; Ctrl+C to quit.
"""
import sys

try:
    import mido
except ImportError:
    print("Install mido and python-rtmidi: pip install mido python-rtmidi")
    sys.exit(1)

NOTE_NAMES = "C C# D D# E F F# G G# A A# B".split()


def midi_note_to_name(midi: int) -> str:
    octave = midi // 12 - 1
    return f"{NOTE_NAMES[midi % 12]}{octave}"


def main():
    names = mido.get_input_names()
    if not names:
        print("No MIDI input devices found. Connect a keyboard and try again.")
        sys.exit(1)
    print("MIDI inputs:", names)
    port_name = names[0]
    print(f"Using: {port_name}")
    print("Press keys on your MIDI keyboard (Ctrl+C to quit)\n")

    with mido.open_input(port_name) as inport:
        for msg in inport:
            if msg.type == "note_on":
                vel = getattr(msg, "velocity", 0)
                if vel == 0:
                    print(f"  note_off  {midi_note_to_name(msg.note)}  ({msg.note})")
                else:
                    print(f"  note_on   {midi_note_to_name(msg.note)}  ({msg.note})  velocity {vel}")
            elif msg.type == "note_off":
                print(f"  note_off  {midi_note_to_name(msg.note)}  ({msg.note})")


if __name__ == "__main__":
    main()
