"""
Reactor status panel - displays timer, strikes, temperature, and edgework.
"""
from typing import TYPE_CHECKING, List

from src.terminal.box_drawing import draw_titled_box, DOUBLE
from src.terminal.colors import Color
from src.ui.progress_bar import TemperatureGauge, StrikeIndicator
from src.ui.seven_segment import SimpleTimerDisplay

if TYPE_CHECKING:
    from src.terminal.text_buffer import TextBuffer
    from src.core.game_state import GameState


class ReactorStatusPanel:
    """
    Reactor status panel showing all game information.
    """
    
    def __init__(self, x: int, y: int, width: int, height: int):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        
        # Sub-components
        self.timer = SimpleTimerDisplay(x + 10, y + 2, Color.LIGHT_GREEN)
        self.strike_indicator = StrikeIndicator(x + 10, y + 4)
        self.temp_gauge = TemperatureGauge(x + 2, y + 7, width - 4)
        
        # Status messages (themed from THEME.md)
        self.status_messages = [
            "Maintenance Terminal Online.",
            "All systems operational. Probably.",
            "Gary would have solved this by now.",
            "Remember: Safety is YOUR responsibility.",
            "Tip: Refer to manual section 7.4.2",
            "The vending machine in break room 3 has been restocked.",
            "NOTICE: Tuesday's evacuation drill has been postponed.",
            "Coffee machine status: concerning.",
            "Radiation levels within acceptable parameters.",
            "REMINDER: Submit Form 27-B before end of shift.",
            "The suggestion box remains welded shut.",
            "Doris from HR is checking on something.",
            "The fluorescent lights have always flickered.",
            "NOTICE: Overtime requests are automatically denied.",
        ]
        self.message_index = 0
        self.message_timer = 0.0
    
    def update(self, dt: float, game_state: "GameState"):
        """Update the panel state."""
        # Update timer display
        self.timer.set_time(game_state.time_remaining)
        self.timer.fg = self._get_timer_color(game_state.time_remaining)
        
        # Update strikes
        self.strike_indicator.set_strikes(game_state.strikes)
        
        # Update temperature
        self.temp_gauge.set_value(game_state.temperature)
        
        # Rotate status messages
        self.message_timer += dt
        if self.message_timer >= 5.0:
            self.message_timer = 0.0
            self.message_index = (self.message_index + 1) % len(self.status_messages)
    
    def _get_timer_color(self, time_remaining: float) -> int:
        """Get timer color based on urgency."""
        if time_remaining < 60:
            return Color.LIGHT_RED
        elif time_remaining < 120:
            return Color.LIGHT_YELLOW
        return Color.LIGHT_GREEN
    
    def render(self, buffer: "TextBuffer", game_state: "GameState"):
        """Render the reactor status panel."""
        # Panel frame
        draw_titled_box(buffer, self.x, self.y, self.width, self.height,
                       "REACTOR STATUS", DOUBLE, Color.GREEN, Color.LIGHT_CYAN)
        
        # Timer
        buffer.put_string(self.x + 2, self.y + 2, "TIME:", Color.LIGHT_GREEN)
        self.timer.render(buffer)
        
        # Strikes
        buffer.put_string(self.x + 2, self.y + 4, "ERRORS:", Color.LIGHT_GREEN)
        self.strike_indicator.render(buffer)
        
        # Temperature
        buffer.put_string(self.x + 2, self.y + 6, "TEMP:", Color.LIGHT_GREEN)
        self.temp_gauge.render(buffer)
        
        # Divider
        y = self.y + 9
        buffer.put_string(self.x + 2, y, "─" * (self.width - 4), Color.GREEN)
        
        # Edgework section
        y += 2
        self._render_edgework(buffer, y, game_state)
        
        # Divider before status
        y = self.y + 22
        buffer.put_string(self.x + 2, y, "─" * (self.width - 4), Color.GREEN)
        
        # Status messages
        y += 2
        self._render_status_messages(buffer, y)
        
        # Module progress
        y = self.y + self.height - 2
        progress_str = f"SOLVED: {game_state.modules_solved}/{game_state.modules_total}"
        buffer.put_string(self.x + 2, y, progress_str, Color.LIGHT_GREEN)
    
    def _render_edgework(self, buffer: "TextBuffer", y: int, game_state: "GameState"):
        """Render the edgework section."""
        edgework = game_state.edgework
        
        buffer.put_string(self.x + 2, y, "SERIAL:", Color.LIGHT_CYAN)
        buffer.put_string(self.x + 12, y, edgework.serial_number, Color.LIGHT_GREEN)
        
        y += 1
        buffer.put_string(self.x + 2, y, "BATTERIES:", Color.LIGHT_CYAN)
        buffer.put_string(self.x + 13, y, str(edgework.batteries), Color.LIGHT_GREEN)
        
        y += 1
        buffer.put_string(self.x + 2, y, "PARALLEL:", Color.LIGHT_CYAN)
        par_str = "YES" if edgework.has_parallel else "NO"
        buffer.put_string(self.x + 12, y, par_str, Color.LIGHT_GREEN)
        
        y += 2
        buffer.put_string(self.x + 2, y, "INDICATORS:", Color.LIGHT_CYAN)
        y += 1
        
        # Render indicators in rows
        col = 0
        for ind_name, lit in edgework.indicators.items():
            marker = "●" if lit else "○"
            color = Color.LIGHT_YELLOW if lit else Color.DARK_GRAY
            x_offset = self.x + 2 + col * 12
            buffer.put_string(x_offset, y, f"{ind_name}:", Color.DARK_GRAY)
            buffer.put_string(x_offset + 5, y, f"[{marker}]", color)
            col += 1
            if col >= 2:
                col = 0
                y += 1
    
    def _render_status_messages(self, buffer: "TextBuffer", y: int):
        """Render the rotating status message."""
        buffer.put_string(self.x + 2, y, "SYSTEM LOG:", Color.LIGHT_CYAN)
        y += 1
        
        msg = self.status_messages[self.message_index]
        max_width = self.width - 6
        
        # Word wrap
        words = msg.split()
        line = "> "
        for word in words:
            if len(line) + len(word) + 1 <= max_width:
                line += word + " "
            else:
                buffer.put_string(self.x + 2, y, line.rstrip(), Color.DARK_GRAY)
                y += 1
                line = "  " + word + " "
        if line.strip():
            buffer.put_string(self.x + 2, y, line.rstrip(), Color.DARK_GRAY)
