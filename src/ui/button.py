"""
ASCII button UI component.
"""
from typing import TYPE_CHECKING, Callable, Optional

from src.terminal.box_drawing import draw_box, SINGLE, DOUBLE
from src.terminal.colors import Color

if TYPE_CHECKING:
    from src.terminal.text_buffer import TextBuffer


class ASCIIButton:
    """A clickable button rendered in ASCII."""
    
    def __init__(self, x: int, y: int, text: str, width: int = None,
                 on_click: Optional[Callable] = None):
        self.x = x
        self.y = y
        self.text = text
        self.width = width or len(text) + 4
        self.height = 3
        
        self.hovered = False
        self.pressed = False
        self.enabled = True
        self.on_click = on_click
    
    def contains_char(self, cx: int, cy: int) -> bool:
        """Check if character position is inside button."""
        return (self.x <= cx < self.x + self.width and
                self.y <= cy < self.y + self.height)
    
    def handle_mouse_move(self, cx: int, cy: int):
        """Update hover state based on mouse position."""
        self.hovered = self.contains_char(cx, cy) and self.enabled
    
    def handle_mouse_down(self, cx: int, cy: int) -> bool:
        """Handle mouse button down. Returns True if button was pressed."""
        if self.contains_char(cx, cy) and self.enabled:
            self.pressed = True
            return True
        return False
    
    def handle_mouse_up(self, cx: int, cy: int) -> bool:
        """Handle mouse button up. Returns True if click should fire."""
        was_pressed = self.pressed
        self.pressed = False
        
        if was_pressed and self.contains_char(cx, cy) and self.enabled:
            if self.on_click:
                self.on_click()
            return True
        return False
    
    def render(self, buffer: "TextBuffer"):
        """Render button to buffer."""
        if not self.enabled:
            fg = Color.DARK_GRAY
            bg = None
            border = SINGLE
        elif self.pressed:
            fg = Color.BLACK
            bg = Color.LIGHT_GREEN
            border = DOUBLE
        elif self.hovered:
            fg = Color.LIGHT_CYAN
            bg = None
            border = DOUBLE
        else:
            fg = Color.LIGHT_GREEN
            bg = None
            border = SINGLE
        
        # Draw border
        draw_box(buffer, self.x, self.y, self.width, self.height, border, fg)
        
        # Draw text (centered)
        text_x = self.x + (self.width - len(self.text)) // 2
        text_y = self.y + 1
        
        if self.pressed:
            buffer.put_string(text_x, text_y, self.text, Color.BLACK, Color.LIGHT_GREEN)
        else:
            buffer.put_string(text_x, text_y, self.text, fg, bg)


class ASCIIToggle:
    """A toggle switch rendered in ASCII."""
    
    def __init__(self, x: int, y: int, label: str, initial_state: bool = False,
                 on_change: Optional[Callable[[bool], None]] = None):
        self.x = x
        self.y = y
        self.label = label
        self.state = initial_state
        self.width = len(label) + 6
        self.height = 1
        
        self.hovered = False
        self.enabled = True
        self.on_change = on_change
    
    def contains_char(self, cx: int, cy: int) -> bool:
        """Check if character position is inside toggle."""
        return (self.x <= cx < self.x + self.width and
                self.y <= cy < self.y + self.height)
    
    def toggle(self):
        """Toggle the state."""
        if self.enabled:
            self.state = not self.state
            if self.on_change:
                self.on_change(self.state)
    
    def render(self, buffer: "TextBuffer"):
        """Render toggle to buffer."""
        if not self.enabled:
            fg = Color.DARK_GRAY
        elif self.hovered:
            fg = Color.LIGHT_CYAN
        else:
            fg = Color.LIGHT_GREEN
        
        # Draw state indicator
        if self.state:
            indicator = "[●]"
            ind_color = Color.LIGHT_GREEN
        else:
            indicator = "[○]"
            ind_color = Color.DARK_GRAY if not self.enabled else fg
        
        buffer.put_string(self.x, self.y, indicator, ind_color)
        buffer.put_string(self.x + 4, self.y, self.label, fg)
