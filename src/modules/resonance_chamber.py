"""
Resonance Chamber module (MIDI).
Match key presses to a two- or four-note pattern that plays and loops.
Four rounds; each round adds a bar that layers with the previous. Lower octaves first,
harmonics added each round until all four bars form a layered rhythm.
"""
import random
from typing import TYPE_CHECKING, List, Optional

from src.modules.base_module import BaseModule
from src.terminal.colors import Color
from src.core.events import MIDI_NOTE_ON, MIDI_NOTE_OFF

if TYPE_CHECKING:
    from src.terminal.text_buffer import TextBuffer
    from src.core.game_state import GameState


# Note names for display (MIDI 48 = C3, 60 = C4)
NOTE_NAMES: dict[int, str] = {}
for midi in range(24, 85):
    names = "C C# D D# E F F# G G# A A# B".split()
    octave = midi // 12 - 1  # 48 -> C3, 60 -> C4
    note = names[midi % 12]
    NOTE_NAMES[midi] = f"{note}{octave}"

BAR_LENGTH = 2.0  # seconds per bar loop
NUM_ROUNDS = 4
# Round 0: C3–B3 (48–59); rounds 1–3: add C4–B4 (60–71) for harmonics
ROUND_NOTE_RANGES = [
    list(range(48, 60)),   # C3–B3
    list(range(48, 72)),   # C3–B4
    list(range(48, 72)),
    list(range(48, 72)),
]


class ResonanceChamberModule(BaseModule):
    """
    Resonance Chamber - match the played pattern on MIDI for each of four bars.
    Each bar (2 or 4 notes) plays and loops; completed bars keep looping while you match the next.
    """

    def _initialize(self):
        """Initialize module state."""
        self.bars: List[List[int]] = []  # per-round pattern (MIDI notes)
        self.current_round = 0
        self.input_index = 0
        self._bar_timer = 0.0
        self._last_slot_per_bar: List[int] = []  # last triggered note slot per bar
        self._note_interval_per_bar: List[float] = []  # BAR_LENGTH / len(bar)
        self._last_played_note: Optional[int] = None  # last note pressed by player (for display)

    def _generate_puzzle(self):
        """Generate four bars of 2- or 4-note patterns."""
        self.bars = []
        self._last_slot_per_bar = []
        self._note_interval_per_bar = []
        for r in range(NUM_ROUNDS):
            length = random.choice([2, 4])
            notes = ROUND_NOTE_RANGES[r]
            pattern = [random.choice(notes) for _ in range(length)]
            self.bars.append(pattern)
            self._last_slot_per_bar.append(-1)
            self._note_interval_per_bar.append(BAR_LENGTH / length)
        self.current_round = 0
        self.input_index = 0
        self._bar_timer = 0.0
        self._last_played_note = None

    def _get_playing_bars(self) -> List[int]:
        """Bars that should be playing (completed + current)."""
        return list(range(self.current_round + 1))

    def update(self, dt: float):
        """Advance bar timer and trigger pad notes for playing bars."""
        if self.solved:
            return
        self._bar_timer += dt
        while self._bar_timer >= BAR_LENGTH:
            self._bar_timer -= BAR_LENGTH
        playing = self._get_playing_bars()
        for bi in playing:
            pattern = self.bars[bi]
            n = len(pattern)
            note_interval = self._note_interval_per_bar[bi]
            slot = int(self._bar_timer / note_interval) % n
            if slot != self._last_slot_per_bar[bi]:
                self._last_slot_per_bar[bi] = slot
                midi_note = pattern[slot]
                if self.audio:
                    self.audio.play_pad(midi_note)

    def _render_content(self, buffer: "TextBuffer"):
        """Render round progress, current pattern hint, and bar indicators."""
        x, y = self.x + 2, self.y + 2
        buffer.put_string(x, y, "RESONANCE CHAMBER", Color.LIGHT_CYAN)
        buffer.put_string(x, y + 1, f"Round {self.current_round + 1}/{NUM_ROUNDS}", Color.LIGHT_GREEN)
        if self.current_round < NUM_ROUNDS:
            pattern = self.bars[self.current_round]
            names = " ".join(NOTE_NAMES.get(n, "?") for n in pattern)
            buffer.put_string(x, y + 3, "Pattern:", Color.DARK_GRAY)
            buffer.put_string(x, y + 4, names, Color.LIGHT_GREEN)
            buffer.put_string(x, y + 5, f"Match: {self.input_index}/{len(pattern)}", Color.DARK_GRAY)
        last_note_str = NOTE_NAMES.get(self._last_played_note, "---") if self._last_played_note is not None else "---"
        buffer.put_string(x, y + 6, f"Playing: {last_note_str}", Color.LIGHT_YELLOW)
        buffer.put_string(x, y + 7, "Bars: [1][2][3][4]", Color.DARK_GRAY)
        for i in range(4):
            cx = x + 7 + i * 4
            if i < self.current_round:
                buffer.put_string(cx, y + 7, "X", Color.LIGHT_GREEN)
            elif i == self.current_round:
                buffer.put_string(cx, y + 7, "*", Color.LIGHT_YELLOW)
            else:
                buffer.put_string(cx, y + 7, "-", Color.DARK_GRAY)
        buffer.put_string(x, y + 9, "Match on MIDI", Color.DARK_GRAY)

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
            self._last_played_note = note  # show what the player is playing
            if self.solved or not self.active:
                return
            if self.current_round >= NUM_ROUNDS:
                return
            pattern = self.bars[self.current_round]
            if self.input_index >= len(pattern):
                return
            expected = pattern[self.input_index]
            if note == expected:
                self.input_index += 1
                if self.input_index >= len(pattern):
                    self.current_round += 1
                    self.input_index = 0
                    if self.current_round >= NUM_ROUNDS:
                        self.solve()
            else:
                self.strike()
            return
        super().handle_event(event, cx, cy)
