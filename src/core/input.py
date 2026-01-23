"""
Input handling utilities for converting pixel to character coordinates.
"""
import pygame
from src.core.settings import SETTINGS


def pixel_to_char(px: int, py: int) -> tuple[int, int]:
    """Convert pixel coordinates to character coordinates."""
    cx = px // SETTINGS.CHAR_WIDTH
    cy = py // SETTINGS.CHAR_HEIGHT
    return (cx, cy)


def char_to_pixel(cx: int, cy: int) -> tuple[int, int]:
    """Convert character coordinates to pixel coordinates (top-left of cell)."""
    px = cx * SETTINGS.CHAR_WIDTH
    py = cy * SETTINGS.CHAR_HEIGHT
    return (px, py)


class InputHandler:
    """
    Handles input and converts to character-grid coordinates.
    Tracks mouse position in both pixel and character space.
    """
    
    def __init__(self):
        self.mouse_char_pos = (0, 0)
        self.mouse_pixel_pos = (0, 0)
        self.mouse_buttons = (False, False, False)
    
    def update(self):
        """Update mouse position tracking."""
        self.mouse_pixel_pos = pygame.mouse.get_pos()
        self.mouse_char_pos = pixel_to_char(*self.mouse_pixel_pos)
        self.mouse_buttons = pygame.mouse.get_pressed()
    
    def get_char_pos(self) -> tuple[int, int]:
        """Get current mouse position in character coordinates."""
        return self.mouse_char_pos
    
    def get_pixel_pos(self) -> tuple[int, int]:
        """Get current mouse position in pixel coordinates."""
        return self.mouse_pixel_pos
    
    def is_left_pressed(self) -> bool:
        """Check if left mouse button is pressed."""
        return self.mouse_buttons[0]
    
    def is_right_pressed(self) -> bool:
        """Check if right mouse button is pressed."""
        return self.mouse_buttons[2]
