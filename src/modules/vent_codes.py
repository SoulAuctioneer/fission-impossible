"""
Vent Codes module (Keypads).
Press symbols in the correct order based on column matching.
"""
import random
from typing import TYPE_CHECKING, List, Set, Optional

from src.modules.base_module import BaseModule
from src.terminal.box_drawing import draw_box, SINGLE
from src.terminal.colors import Color
from src.audio.audio_manager import SFX

if TYPE_CHECKING:
    from src.terminal.text_buffer import TextBuffer
    from src.core.game_state import GameState


class VentCodesModule(BaseModule):
    """
    Vent Codes module - equivalent to Keypads.
    Press 4 symbols in the correct order based on column rules.
    """
    
    # Symbol columns (from original game, with nuclear-themed symbols)
    # Each column defines the order symbols should be pressed
    # NOTE: Using CP437-compatible characters for IBM VGA font compatibility
    # Mapping: ☢→Ω, ★→♦, ◊→♥, ⚡→§, ✱→¤, ℃→°, ◎→◙, ⚠→‼, ∅→φ, ©→©, ⚙→♠
    COLUMNS = [
        ['Ω', '♦', '♥', '§', '¤', '±', '°'],
        ['◙', 'Ω', '°', '‼', '♦', '±', 'φ'],
        ['©', '§', '°', '‼', '¤', '♥', '♦'],
        ['♠', '‼', 'φ', '¤', '♥', '©', '§'],
        ['¤', 'φ', '©', '§', '‼', '◙', 'Ω'],
        ['♠', '◙', 'φ', '♦', '±', '§', '©'],
    ]
    
    # All unique symbols (CP437 compatible)
    ALL_SYMBOLS = ['Ω', '♦', '♥', '§', '¤', '±', '°', '◙', '‼', 'φ', '©', '♠']
    
    def _initialize(self):
        """Initialize module variables."""
        self.symbols: List[str] = []  # 4 symbols on the keypad
        self.correct_order: List[int] = []  # Correct press order (indices into symbols)
        self.pressed: List[bool] = [False, False, False, False]
        self.press_count = 0
    
    def _generate_puzzle(self):
        """Generate keypad configuration."""
        # Find a valid column that can provide 4 symbols
        valid_column = None
        selected_symbols = []
        
        # Try to find a column where we can pick 4 symbols
        column_idx = random.randint(0, len(self.COLUMNS) - 1)
        column = self.COLUMNS[column_idx]
        
        # Pick 4 random symbols from this column
        available_indices = list(range(len(column)))
        random.shuffle(available_indices)
        selected_indices = sorted(available_indices[:4])  # Keep order for solution
        selected_symbols = [column[i] for i in selected_indices]
        
        # Shuffle for display
        display_order = list(range(4))
        random.shuffle(display_order)
        
        self.symbols = [selected_symbols[i] for i in display_order]
        
        # Correct order is based on column position
        self.correct_order = []
        for col_symbol in column:
            for i, sym in enumerate(self.symbols):
                if sym == col_symbol and i not in self.correct_order:
                    self.correct_order.append(i)
                    break
        
        # Reset state
        self.pressed = [False, False, False, False]
        self.press_count = 0
    
    def _handle_click(self, local_x: int, local_y: int) -> bool:
        """Handle symbol button press."""
        # Symbol buttons are in a 2x2 grid (centered)
        # Button 0: x=5-11, y=3-5
        # Button 1: x=16-22, y=3-5
        # Button 2: x=5-11, y=7-9
        # Button 3: x=16-22, y=7-9
        
        button_idx = -1
        
        if 3 <= local_y <= 5:
            if 5 <= local_x <= 11:
                button_idx = 0
            elif 16 <= local_x <= 22:
                button_idx = 1
        elif 7 <= local_y <= 9:
            if 5 <= local_x <= 11:
                button_idx = 2
            elif 16 <= local_x <= 22:
                button_idx = 3
        
        if button_idx >= 0 and not self.pressed[button_idx]:
            self._press_button(button_idx)
            return True
        
        return False
    
    def _press_button(self, idx: int):
        """Press a symbol button."""
        # Check if this is the correct next button
        expected_idx = self.correct_order[self.press_count]
        
        self.play_sound(SFX.SYMBOL_SELECT)
        
        if idx == expected_idx:
            self.pressed[idx] = True
            self.press_count += 1
            
            # Check if all pressed
            if self.press_count >= 4:
                self.play_sound(SFX.CODE_SUBMIT)
                self.solve()
        else:
            # Wrong button - strike
            self.strike()
    
    def _render_content(self, buffer: "TextBuffer"):
        """Render the keypad."""
        # 2x2 grid of symbol buttons - centered
        # Two buttons (7 wide each) + gap (4) = 18 chars, center = (28-18)//2 = 5
        positions = [
            (self.x + 5, self.y + 3),   # Top-left
            (self.x + 16, self.y + 3),  # Top-right
            (self.x + 5, self.y + 7),   # Bottom-left
            (self.x + 16, self.y + 7),  # Bottom-right
        ]
        
        for i, (bx, by) in enumerate(positions):
            symbol = self.symbols[i]
            pressed = self.pressed[i]
            
            # Button frame
            if pressed:
                fg = Color.DARK_GRAY
            else:
                fg = Color.LIGHT_GREEN
            
            draw_box(buffer, bx, by, 7, 3, SINGLE, fg)
            
            # Symbol
            sym_x = bx + 3
            sym_y = by + 1
            
            if pressed:
                buffer.put_char(sym_x, sym_y, '√', Color.LIGHT_GREEN)  # CP437 checkmark
            else:
                buffer.put_char(sym_x, sym_y, symbol, Color.LIGHT_YELLOW)
