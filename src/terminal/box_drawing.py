"""
Box drawing character helpers for creating UI frames and panels.
"""
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.terminal.text_buffer import TextBuffer


@dataclass
class BoxStyle:
    """Box drawing character set."""
    h: str      # Horizontal
    v: str      # Vertical
    tl: str     # Top-left
    tr: str     # Top-right
    bl: str     # Bottom-left
    br: str     # Bottom-right
    t_down: str # T pointing down
    t_up: str   # T pointing up
    t_right: str# T pointing right
    t_left: str # T pointing left
    cross: str  # Cross/plus


# Predefined styles
SINGLE = BoxStyle('─', '│', '┌', '┐', '└', '┘', '┬', '┴', '├', '┤', '┼')
DOUBLE = BoxStyle('═', '║', '╔', '╗', '╚', '╝', '╦', '╩', '╠', '╣', '╬')
HEAVY  = BoxStyle('━', '┃', '┏', '┓', '┗', '┛', '┳', '┻', '┣', '┫', '╋')
ROUND  = BoxStyle('─', '│', '╭', '╮', '╰', '╯', '┬', '┴', '├', '┤', '┼')


def draw_box(buffer: "TextBuffer", x: int, y: int, w: int, h: int, 
             style: BoxStyle = SINGLE, fg: int = 10, bg: int = None):
    """Draw a box using box-drawing characters."""
    if w < 2 or h < 2:
        return
    
    # Corners
    buffer.put_char(x, y, style.tl, fg, bg)
    buffer.put_char(x + w - 1, y, style.tr, fg, bg)
    buffer.put_char(x, y + h - 1, style.bl, fg, bg)
    buffer.put_char(x + w - 1, y + h - 1, style.br, fg, bg)
    
    # Top and bottom edges
    for i in range(1, w - 1):
        buffer.put_char(x + i, y, style.h, fg, bg)
        buffer.put_char(x + i, y + h - 1, style.h, fg, bg)
    
    # Left and right edges
    for i in range(1, h - 1):
        buffer.put_char(x, y + i, style.v, fg, bg)
        buffer.put_char(x + w - 1, y + i, style.v, fg, bg)


def draw_titled_box(buffer: "TextBuffer", x: int, y: int, w: int, h: int,
                    title: str, style: BoxStyle = DOUBLE, 
                    fg: int = 10, title_fg: int = 14, bg: int = None):
    """Draw a box with a title in the top border."""
    draw_box(buffer, x, y, w, h, style, fg, bg)
    
    # Title (centered in top border)
    title_text = f" {title} "
    title_x = x + (w - len(title_text)) // 2
    buffer.put_string(title_x, y, title_text, title_fg, bg)


def draw_horizontal_line(buffer: "TextBuffer", x: int, y: int, length: int,
                         style: BoxStyle = SINGLE, fg: int = 10, bg: int = None):
    """Draw a horizontal line."""
    for i in range(length):
        buffer.put_char(x + i, y, style.h, fg, bg)


def draw_vertical_line(buffer: "TextBuffer", x: int, y: int, length: int,
                       style: BoxStyle = SINGLE, fg: int = 10, bg: int = None):
    """Draw a vertical line."""
    for i in range(length):
        buffer.put_char(x, y + i, style.v, fg, bg)
