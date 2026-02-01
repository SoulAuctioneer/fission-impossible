"""
Reactor Tune module (MIDI piano).
Play the displayed 3-note sequence on a connected MIDI keyboard.
"""
import random
from typing import TYPE_CHECKING, List

from src.modules.base_module import BaseModule
from src.terminal.colors import Color
from src.core.events import MIDI_NOTE_ON, MIDI_NOTE_OFF

if TYPE_CHECKING:
    from src.terminal.text_buffer import TextBuffer
    from src.core.game_state import GameState


# White keys C4–B4 (MIDI 60–71) for display names
NOTE_NAMES = {
    60: "C4", 61: "C#4", 62: "D4", 63: "D#4", 64: "E4", 65: "F4",
    66: "F#4", 67: "G4", 68: "G#4", 69: "A4", 70: "A#4", 71: "B4",
    72: "C5",
}


class PianoModule(BaseModule):
    """
    Reactor Tune module - play the correct 3-note sequence on a MIDI keyboard.
    """

    # Notes used for the puzzle (white keys C4–B4)
    PUZZLE_NOTES = [60, 62, 64, 65, 67, 69, 71]  # C4, D4, E4, F4, G4, A4, B4
    SEQUENCE_LENGTH = 3

    def _initialize(self):
        """Initialize module variables."""
        self.target_sequence: List[int] = []
        self.input_index: int = 0
        self.last_note_name: str = "---"

    def _generate_puzzle(self):
        """Generate a random 3-note sequence."""
        self.target_sequence = [
            random.choice(self.PUZZLE_NOTES) for _ in range(self.SEQUENCE_LENGTH)
        ]
        self.input_index = 0
        self.last_note_name = "---"

    def _render_content(self, buffer: "TextBuffer"):
        """Render the target sequence and input progress."""
        x, y = self.x + 2, self.y + 2
        buffer.put_string(x, y, "Play sequence:", Color.LIGHT_CYAN)
        seq_str = " ".join(NOTE_NAMES.get(n, "?") for n in self.target_sequence)
        buffer.put_string(x, y + 1, seq_str, Color.LIGHT_GREEN)
        buffer.put_string(x, y + 3, f"Progress: {self.input_index}/{self.SEQUENCE_LENGTH}", Color.DARK_GRAY)
        buffer.put_string(x, y + 4, "Use MIDI keyboard", Color.DARK_GRAY)

    def _handle_click(self, local_x: int, local_y: int) -> bool:
        """No mouse interaction; input is MIDI only."""
        return False

    def handle_event(self, event, cx: int, cy: int):
        """Handle MIDI note events; delegate mouse to base."""
        if event.type in (MIDI_NOTE_ON, MIDI_NOTE_OFF):
            if event.type == MIDI_NOTE_OFF:
                return
            velocity = getattr(event, "velocity", 127)
            if velocity == 0:
                return
            note = getattr(event, "note", -1)
            if self.solved or not self.active:
                return
            if self.input_index >= self.SEQUENCE_LENGTH:
                return
            expected = self.target_sequence[self.input_index]
            self.last_note_name = NOTE_NAMES.get(note, "?")
            if note == expected:
                self.input_index += 1
                if self.input_index >= self.SEQUENCE_LENGTH:
                    self.solve()
            else:
                self.strike()
            return
        super().handle_event(event, cx, cy)
