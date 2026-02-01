"""
MIDI input layer: polls a connected MIDI keyboard and posts pygame events
for note_on / note_off so the game loop can consume them like other input.
"""
from typing import Optional

import pygame

from src.core.events import MIDI_NOTE_ON, MIDI_NOTE_OFF


class MidiInput:
    """
    Opens a MIDI input port (e.g. USB piano keyboard) and polls each frame.
    Converts note_on/note_off messages into custom pygame events so they
    are processed in the same pass as mouse/keyboard.
    """

    def __init__(self, device_name: Optional[str] = None):
        """
        Open a MIDI input. If device_name is given, use the first port whose
        name contains it; otherwise use the first available port. If no
        device is found, no port is opened and poll() is a no-op.
        """
        self._inport = None
        try:
            import mido
            names = mido.get_input_names()
            if not names:
                return
            if device_name:
                for name in names:
                    if device_name.lower() in name.lower():
                        self._inport = mido.open_input(name)
                        return
            self._inport = mido.open_input(names[0])
        except Exception:
            # mido/rtmidi not installed or no device; leave _inport None
            pass

    def poll(self) -> None:
        """
        Read all pending MIDI messages and post corresponding pygame events.
        Call once per frame at the start of the event loop (before
        pygame.event.get()). Note-on with velocity 0 is treated as note_off.
        """
        if self._inport is None:
            return
        try:
            import mido
            while True:
                msg = self._inport.poll()
                if msg is None:
                    break
                if msg.type == "note_on":
                    if getattr(msg, "velocity", 0) == 0:
                        ev = pygame.event.Event(MIDI_NOTE_OFF, note=msg.note, velocity=0)
                    else:
                        ev = pygame.event.Event(
                            MIDI_NOTE_ON, note=msg.note, velocity=getattr(msg, "velocity", 127)
                        )
                    pygame.event.post(ev)
                elif msg.type == "note_off":
                    ev = pygame.event.Event(
                        MIDI_NOTE_OFF, note=msg.note, velocity=getattr(msg, "velocity", 0)
                    )
                    pygame.event.post(ev)
        except Exception:
            # Port may have been disconnected
            pass

    def close(self) -> None:
        """Close the MIDI input port. Safe to call if never opened."""
        if self._inport is not None:
            try:
                self._inport.close()
            except Exception:
                pass
            self._inport = None

    @property
    def is_connected(self) -> bool:
        """True if a MIDI input port is open."""
        return self._inport is not None
