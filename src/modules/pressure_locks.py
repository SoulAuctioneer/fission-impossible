"""
Pressure Locks module (Maze).
Navigate through an invisible maze using arrow buttons.
"""
import random
from typing import TYPE_CHECKING, List, Tuple, Set

from src.modules.base_module import BaseModule
from src.terminal.box_drawing import draw_box, SINGLE
from src.terminal.colors import Color
from src.audio.audio_manager import SFX

if TYPE_CHECKING:
    from src.terminal.text_buffer import TextBuffer
    from src.core.game_state import GameState


class PressureLocksModule(BaseModule):
    """
    Pressure Locks module - equivalent to Maze.
    Navigate a 6x6 grid to reach the target without hitting walls.
    """
    
    # Predefined maze layouts (9 mazes)
    # Each maze is defined by walls between cells
    # Format: set of ((x1,y1), (x2,y2)) tuples indicating walls
    # Also includes two reference marker positions to identify the maze
    MAZES = [
        # Maze 0
        {
            'markers': [(0, 1), (5, 2)],
            'walls': {
                ((0,0), (1,0)), ((1,0), (2,0)), ((3,0), (4,0)),
                ((0,0), (0,1)), ((2,0), (2,1)), ((4,0), (4,1)),
                ((1,1), (2,1)), ((3,1), (4,1)), ((5,1), (5,2)),
                ((0,2), (0,3)), ((1,2), (1,3)), ((2,2), (3,2)),
                ((4,2), (4,3)), ((0,3), (1,3)), ((2,3), (2,4)),
                ((3,3), (4,3)), ((5,3), (5,4)), ((1,4), (2,4)),
                ((3,4), (4,4)), ((0,4), (0,5)), ((2,4), (2,5)),
                ((3,5), (4,5)), ((4,4), (4,5)),
            }
        },
        # Maze 1
        {
            'markers': [(4, 1), (1, 3)],
            'walls': {
                ((1,0), (1,1)), ((2,0), (3,0)), ((4,0), (5,0)),
                ((0,1), (1,1)), ((2,1), (2,2)), ((3,1), (3,2)),
                ((5,1), (5,2)), ((0,2), (1,2)), ((1,2), (1,3)),
                ((4,2), (4,3)), ((0,3), (0,4)), ((2,3), (3,3)),
                ((3,3), (3,4)), ((5,3), (5,4)), ((1,4), (2,4)),
                ((4,4), (5,4)), ((0,5), (1,5)), ((2,4), (2,5)),
                ((3,5), (4,5)),
            }
        },
        # Maze 2
        {
            'markers': [(3, 3), (5, 3)],
            'walls': {
                ((0,0), (0,1)), ((2,0), (2,1)), ((3,0), (4,0)),
                ((1,1), (1,2)), ((3,1), (4,1)), ((4,1), (4,2)),
                ((0,2), (1,2)), ((2,2), (2,3)), ((5,2), (5,3)),
                ((0,3), (0,4)), ((1,3), (2,3)), ((3,3), (3,4)),
                ((4,3), (5,3)), ((1,4), (1,5)), ((2,4), (3,4)),
                ((4,4), (4,5)), ((0,5), (1,5)), ((3,5), (4,5)),
            }
        },
        # Maze 3
        {
            'markers': [(0, 0), (0, 3)],
            'walls': {
                ((1,0), (2,0)), ((3,0), (3,1)), ((4,0), (4,1)),
                ((0,1), (1,1)), ((2,1), (2,2)), ((5,1), (5,2)),
                ((0,2), (0,3)), ((1,2), (1,3)), ((3,2), (4,2)),
                ((2,3), (2,4)), ((3,3), (3,4)), ((4,3), (5,3)),
                ((0,4), (1,4)), ((4,4), (4,5)), ((5,4), (5,5)),
                ((1,5), (2,5)), ((2,4), (2,5)), ((3,5), (4,5)),
            }
        },
        # Maze 4
        {
            'markers': [(4, 2), (3, 5)],
            'walls': {
                ((0,0), (1,0)), ((2,0), (2,1)), ((4,0), (4,1)),
                ((0,1), (0,2)), ((1,1), (2,1)), ((3,1), (3,2)),
                ((5,1), (5,2)), ((1,2), (1,3)), ((2,2), (2,3)),
                ((4,2), (5,2)), ((0,3), (1,3)), ((3,3), (4,3)),
                ((2,4), (3,4)), ((4,4), (4,5)), ((5,4), (5,5)),
                ((0,5), (1,5)), ((1,4), (1,5)), ((3,4), (3,5)),
            }
        },
        # Maze 5
        {
            'markers': [(4, 0), (1, 5)],
            'walls': {
                ((0,0), (0,1)), ((1,0), (2,0)), ((3,0), (3,1)),
                ((5,0), (5,1)), ((1,1), (1,2)), ((2,1), (3,1)),
                ((4,1), (4,2)), ((0,2), (1,2)), ((2,2), (2,3)),
                ((5,2), (5,3)), ((0,3), (0,4)), ((1,3), (1,4)),
                ((3,3), (4,3)), ((1,4), (2,4)), ((3,4), (3,5)),
                ((4,4), (5,4)), ((0,5), (1,5)), ((4,5), (5,5)),
            }
        },
        # Simplified mazes for remaining slots
        # Maze 6
        {
            'markers': [(2, 0), (3, 2)],
            'walls': {
                ((0,0), (0,1)), ((1,0), (1,1)), ((3,0), (4,0)),
                ((2,1), (2,2)), ((4,1), (5,1)), ((0,2), (0,3)),
                ((1,2), (2,2)), ((3,2), (3,3)), ((5,2), (5,3)),
                ((0,4), (1,4)), ((2,3), (2,4)), ((4,3), (4,4)),
                ((1,5), (2,5)), ((3,4), (3,5)), ((4,5), (5,5)),
            }
        },
        # Maze 7
        {
            'markers': [(1, 0), (2, 4)],
            'walls': {
                ((0,0), (0,1)), ((2,0), (3,0)), ((4,0), (4,1)),
                ((1,1), (1,2)), ((3,1), (3,2)), ((5,1), (5,2)),
                ((0,2), (1,2)), ((2,2), (3,2)), ((4,2), (4,3)),
                ((0,3), (0,4)), ((2,3), (2,4)), ((5,3), (5,4)),
                ((1,4), (1,5)), ((3,4), (4,4)), ((0,5), (1,5)),
                ((2,5), (3,5)), ((4,5), (5,5)),
            }
        },
        # Maze 8
        {
            'markers': [(0, 4), (4, 4)],
            'walls': {
                ((1,0), (1,1)), ((2,0), (3,0)), ((5,0), (5,1)),
                ((0,1), (0,2)), ((2,1), (2,2)), ((3,1), (4,1)),
                ((1,2), (2,2)), ((4,2), (5,2)), ((0,3), (1,3)),
                ((2,3), (2,4)), ((3,3), (3,4)), ((5,3), (5,4)),
                ((0,4), (0,5)), ((1,4), (2,4)), ((4,4), (4,5)),
                ((1,5), (2,5)), ((3,5), (4,5)),
            }
        },
    ]
    
    def _initialize(self):
        """Initialize module variables."""
        self.maze_index = 0
        self.player_pos = [0, 0]
        self.target_pos = [5, 5]
        self.markers: List[Tuple[int, int]] = []
        self.walls: Set = set()
    
    def _generate_puzzle(self):
        """Generate maze configuration."""
        # Pick a random maze
        self.maze_index = random.randint(0, len(self.MAZES) - 1)
        maze = self.MAZES[self.maze_index]
        
        self.markers = maze['markers']
        self.walls = maze['walls']
        
        # Random start and target positions (not on markers)
        available = []
        for x in range(6):
            for y in range(6):
                if (x, y) not in self.markers:
                    available.append((x, y))
        
        random.shuffle(available)
        self.player_pos = list(available[0])
        self.target_pos = list(available[1])
    
    def _can_move(self, from_pos: Tuple[int, int], to_pos: Tuple[int, int]) -> bool:
        """Check if movement is valid (no wall between cells)."""
        # Check bounds
        if not (0 <= to_pos[0] < 6 and 0 <= to_pos[1] < 6):
            return False
        
        # Check for wall
        wall = (from_pos, to_pos)
        wall_rev = (to_pos, from_pos)
        
        return wall not in self.walls and wall_rev not in self.walls
    
    def _handle_click(self, local_x: int, local_y: int) -> bool:
        """Handle arrow button press."""
        # Arrow buttons at bottom (centered)
        # Up: x=12-14, y=9
        # Down: x=12-14, y=11
        # Left: x=8-10, y=10
        # Right: x=16-18, y=10
        
        direction = None
        
        if 12 <= local_x <= 14:
            if local_y == 9:
                direction = (0, -1)  # Up
            elif local_y == 11:
                direction = (0, 1)   # Down
        elif local_y == 10:
            if 8 <= local_x <= 10:
                direction = (-1, 0)  # Left
            elif 16 <= local_x <= 18:
                direction = (1, 0)   # Right
        
        if direction:
            self._move(direction)
            return True
        
        return False
    
    def _move(self, direction: Tuple[int, int]):
        """Attempt to move in the given direction."""
        current = tuple(self.player_pos)
        new_pos = (self.player_pos[0] + direction[0], 
                   self.player_pos[1] + direction[1])
        
        if self._can_move(current, new_pos):
            self.player_pos = list(new_pos)
            self.play_sound(SFX.GRID_MOVE)
            
            # Check if reached target
            if self.player_pos == list(self.target_pos):
                self.play_sound(SFX.PATH_COMPLETE)
                self.solve()
        else:
            # Hit a wall - strike
            self.strike()
    
    def _render_content(self, buffer: "TextBuffer"):
        """Render the maze grid and controls."""
        # Grid position - centered (6 cells * 2 chars = 12 chars, center = (28-12)//2 = 8)
        grid_x = self.x + 8
        grid_y = self.y + 2
        cell_size = 2
        
        # Draw 6x6 grid
        for gy in range(6):
            for gx in range(6):
                cx = grid_x + gx * cell_size
                cy = grid_y + gy
                
                # Cell content
                is_player = (gx, gy) == tuple(self.player_pos)
                is_target = (gx, gy) == tuple(self.target_pos)
                is_marker = (gx, gy) in self.markers
                
                if is_player:
                    buffer.put_char(cx, cy, '■', Color.LIGHT_GREEN)
                elif is_target:
                    buffer.put_char(cx, cy, '▲', Color.LIGHT_RED)
                elif is_marker:
                    buffer.put_char(cx, cy, '◙', Color.LIGHT_CYAN)
                else:
                    buffer.put_char(cx, cy, '·', Color.DARK_GRAY)
        
        # Arrow controls (using CP437-compatible arrows) - centered
        # Arrows span 11 chars ([◄]...[▲]...[►]), center = (28-11)//2 = 8
        arrow_y = self.y + 10
        buffer.put_string(self.x + 12, arrow_y - 1, "[▲]", Color.LIGHT_GREEN)
        buffer.put_string(self.x + 8, arrow_y, "[<]", Color.LIGHT_GREEN)
        buffer.put_string(self.x + 16, arrow_y, "[>]", Color.LIGHT_GREEN)
        buffer.put_string(self.x + 12, arrow_y + 1, "[▼]", Color.LIGHT_GREEN)
