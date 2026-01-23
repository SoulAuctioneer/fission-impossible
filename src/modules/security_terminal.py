"""
Security Terminal module (Password).
Player must cycle through letters to form the correct word.
"""
import random
from typing import TYPE_CHECKING, List, Set

from src.modules.base_module import BaseModule
from src.terminal.box_drawing import draw_box, SINGLE
from src.terminal.colors import Color
from src.ui.button import ASCIIButton

if TYPE_CHECKING:
    from src.terminal.text_buffer import TextBuffer
    from src.core.game_state import GameState


class SecurityTerminalModule(BaseModule):
    """
    Security Terminal module - equivalent to Password.
    Cycle through letters at each position to form a valid word.
    """
    
    # Valid words
    WORDS = [
        "ALARM", "ATOMS", "BADGE", "BURNS", "CHAIN",
        "CLEAN", "CLOCK", "CODES", "CORES", "DECAY",
        "DRAIN", "FUSED", "GAUGE", "GEARS", "GUARD",
        "HAZED", "LEAKS", "METER", "NUKED", "PLANT",
        "POWER", "SHIFT", "SIREN", "SMOKE", "SPLIT",
        "STEAM", "TIMER", "VALVE", "VAULT", "WASTE",
        "WATTS"
    ]
    
    def _initialize(self):
        """Initialize module variables."""
        self.target_word = ""
        self.letter_options: List[List[str]] = []  # Available letters per position
        self.current_indices: List[int] = [0, 0, 0, 0, 0]  # Current selection per position
    
    def _generate_puzzle(self):
        """Generate password puzzle."""
        # Pick a random target word
        self.target_word = random.choice(self.WORDS)
        
        # Generate letter options for each position
        self.letter_options = []
        
        for i in range(5):
            correct_letter = self.target_word[i]
            
            # Start with the correct letter
            options = {correct_letter}
            
            # Add 4-5 random wrong letters
            alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
            while len(options) < 6:
                random_letter = random.choice(alphabet)
                # Only add if it wouldn't complete a different valid word
                options.add(random_letter)
            
            # Convert to sorted list and randomize order
            options_list = list(options)
            random.shuffle(options_list)
            self.letter_options.append(options_list)
        
        # Start at random positions
        self.current_indices = [random.randint(0, len(opts) - 1) 
                                for opts in self.letter_options]
    
    def get_current_word(self) -> str:
        """Get the currently displayed word."""
        return "".join(
            self.letter_options[i][self.current_indices[i]]
            for i in range(5)
        )
    
    def _handle_click(self, local_x: int, local_y: int) -> bool:
        """Handle click on up/down buttons or submit."""
        # Letter display starts at local_x=3, each slot is 4 chars wide
        # Up arrows are at local_y=3
        # Letters are at local_y=5
        # Down arrows are at local_y=7
        # Submit button is at local_y=10
        
        # Check up arrows (y=3)
        if local_y == 3:
            slot = (local_x - 3) // 4
            if 0 <= slot < 5:
                self._cycle_up(slot)
                return True
        
        # Check down arrows (y=7)
        elif local_y == 7:
            slot = (local_x - 3) // 4
            if 0 <= slot < 5:
                self._cycle_down(slot)
                return True
        
        # Check submit button (y=9-11, x=6-20)
        elif 9 <= local_y <= 11 and 6 <= local_x <= 20:
            self._submit()
            return True
        
        return False
    
    def _cycle_up(self, slot: int):
        """Cycle letter up at given slot."""
        if 0 <= slot < 5:
            options = self.letter_options[slot]
            self.current_indices[slot] = (self.current_indices[slot] - 1) % len(options)
    
    def _cycle_down(self, slot: int):
        """Cycle letter down at given slot."""
        if 0 <= slot < 5:
            options = self.letter_options[slot]
            self.current_indices[slot] = (self.current_indices[slot] + 1) % len(options)
    
    def _submit(self):
        """Submit the current word."""
        current_word = self.get_current_word()
        
        if current_word == self.target_word:
            self.solve()
        elif current_word in self.WORDS:
            # Valid word but wrong - this shouldn't happen with proper generation
            # but handle it gracefully
            self.solve()
        else:
            self.strike()
    
    def _render_content(self, buffer: "TextBuffer"):
        """Render the password terminal."""
        # Up arrows
        arrow_y = self.y + 3
        for i in range(5):
            x = self.x + 3 + i * 4
            buffer.put_string(x, arrow_y, "[▲]", Color.LIGHT_GREEN)
        
        # Letter boxes
        letter_y = self.y + 5
        for i in range(5):
            x = self.x + 3 + i * 4
            letter = self.letter_options[i][self.current_indices[i]]
            buffer.put_char(x, letter_y, '[', Color.LIGHT_CYAN)
            buffer.put_char(x + 1, letter_y, letter, Color.WHITE)
            buffer.put_char(x + 2, letter_y, ']', Color.LIGHT_CYAN)
        
        # Down arrows
        arrow_y = self.y + 7
        for i in range(5):
            x = self.x + 3 + i * 4
            buffer.put_string(x, arrow_y, "[▼]", Color.LIGHT_GREEN)
        
        # Submit button
        submit_y = self.y + 9
        draw_box(buffer, self.x + 6, submit_y, 14, 3, SINGLE, Color.LIGHT_GREEN)
        buffer.put_string(self.x + 8, submit_y + 1, "[ SUBMIT ]", Color.LIGHT_GREEN)
