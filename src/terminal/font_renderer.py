"""
FontRenderer - Renders TextBuffer to pygame Surface using a bitmap font.
"""
import pygame
from pathlib import Path
from typing import TYPE_CHECKING

from src.terminal.colors import ANSI_COLORS

if TYPE_CHECKING:
    from src.terminal.text_buffer import TextBuffer


class FontRenderer:
    """
    Renders a TextBuffer to a pygame Surface using a monospace font.
    Pre-caches glyphs for performance.
    """
    
    def __init__(self, font_path: Path, char_width: int = 16, char_height: int = 16):
        self.char_width = char_width
        self.char_height = char_height
        
        # Load font (sized to match character dimensions)
        if font_path.exists():
            self.font = pygame.font.Font(str(font_path), char_height)
        else:
            # Fallback to system monospace font
            print(f"Warning: Font not found at {font_path}, using system font")
            self.font = pygame.font.SysFont('monospace', char_height)
        
        # Pre-render glyph cache: {(char_code, fg_color): Surface}
        self._glyph_cache: dict[tuple[int, int], pygame.Surface] = {}
        
        # Pre-render common characters
        self._prerender_common_glyphs()
    
    def _prerender_common_glyphs(self):
        """Pre-render frequently used characters in all colors."""
        common_chars = (
            " !\"#$%&'()*+,-./0123456789:;<=>?@"
            "ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`"
            "abcdefghijklmnopqrstuvwxyz{|}~"
            "─│┌┐└┘├┤┬┴┼═║╔╗╚╝╠╣╦╩╬"
            "░▒▓█▀▄▌▐■□●○◆◇★☆▲▼◀▶"
            "☢⚠✱╳╭╮╰╯━┃┏┓┗┛┣┫┳┻╋"
            "△▽◁▷←→↑↓∙·•¤♦♠♣♥◉◎▪▫◊"
        )
        
        for char in common_chars:
            for color_idx in range(16):
                self._get_glyph(ord(char), color_idx)
    
    def _get_glyph(self, char_code: int, fg_color: int) -> pygame.Surface:
        """Get or create a rendered glyph."""
        key = (char_code, fg_color)
        
        if key not in self._glyph_cache:
            char = chr(char_code)
            color = ANSI_COLORS[fg_color]
            
            # Render with antialiasing off for crisp pixels
            try:
                glyph = self.font.render(char, False, color)
            except Exception:
                # Fallback for characters the font doesn't support
                glyph = self.font.render('?', False, color)
            
            # Ensure consistent size
            if glyph.get_size() != (self.char_width, self.char_height):
                sized = pygame.Surface((self.char_width, self.char_height), pygame.SRCALPHA)
                # Center the glyph if it's smaller
                glyph_w, glyph_h = glyph.get_size()
                offset_x = (self.char_width - glyph_w) // 2
                offset_y = (self.char_height - glyph_h) // 2
                sized.blit(glyph, (max(0, offset_x), max(0, offset_y)))
                glyph = sized
            
            self._glyph_cache[key] = glyph
        
        return self._glyph_cache[key]
    
    def render(self, buffer: "TextBuffer", target: pygame.Surface):
        """Render the entire TextBuffer to target surface."""
        for y in range(buffer.height):
            for x in range(buffer.width):
                char_code = buffer.chars[y, x]
                fg = buffer.fg_colors[y, x]
                bg = buffer.bg_colors[y, x]
                
                px = x * self.char_width
                py = y * self.char_height
                
                # Draw background
                if bg != 0:  # 0 = black, skip for performance
                    bg_rect = pygame.Rect(px, py, self.char_width, self.char_height)
                    pygame.draw.rect(target, ANSI_COLORS[bg], bg_rect)
                
                # Draw character
                if char_code != ord(' '):  # Skip spaces for performance
                    glyph = self._get_glyph(char_code, fg)
                    target.blit(glyph, (px, py))
    
    def render_dirty(self, buffer: "TextBuffer", target: pygame.Surface):
        """Render only dirty rows (optimization)."""
        for y in buffer.get_dirty_rows():
            for x in range(buffer.width):
                char_code = buffer.chars[y, x]
                fg = buffer.fg_colors[y, x]
                bg = buffer.bg_colors[y, x]
                
                px = x * self.char_width
                py = y * self.char_height
                
                # Clear cell
                cell_rect = pygame.Rect(px, py, self.char_width, self.char_height)
                pygame.draw.rect(target, ANSI_COLORS[0], cell_rect)  # Black
                
                # Draw background
                if bg != 0:
                    pygame.draw.rect(target, ANSI_COLORS[bg], cell_rect)
                
                # Draw character
                if char_code != ord(' '):
                    glyph = self._get_glyph(char_code, fg)
                    target.blit(glyph, (px, py))
