"""
Reactor status panel - displays timer, strikes, module progress, and temperature.

PANEL LAYOUT (35 wide × 30 tall, positioned at x=103, y=3)
═════════════════════════════════════════════════════════════════════════════════

    ╔═════════════════════════════════╗
    ║       REACTOR STATUS            ║  <- y+0: Title
    ║                                 ║
    ║  TIME:   04:32                  ║  <- y+2: Timer display
    ║  ERRORS: [■] [■] [·]            ║  <- y+4: Strike indicators
    ║  FIXED:  [■] [■] [■] [·] [·] [·]║  <- y+5: Module progress
    ║  TEMP:   ▓▓▓▓▓▓▓░░░░░░░░        ║  <- y+7-8: Temperature gauge
    ║  ─────────────────────────────  ║  <- y+10: Divider
    ║  SYSTEM LOG:                    ║  <- y+12+: Scrolling log (newest white)
    ║  > Latest message in white...   ║
    ║    Older messages in grey...    ║
    ╚═════════════════════════════════╝

Note: Full edgework (batteries, indicators, parallel port, serial) is displayed
in the EdgewWorkPanel at the bottom of the screen.
"""
from typing import TYPE_CHECKING, List

from src.terminal.box_drawing import draw_titled_box, DOUBLE
from src.terminal.colors import Color
from src.ui.progress_bar import TemperatureGauge, StrikeIndicator, ModuleProgressIndicator
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
        self.module_progress = ModuleProgressIndicator(x + 10, y + 5)
        self.temp_gauge = TemperatureGauge(x + 2, y + 8, width - 4)
        
        # Status messages (themed from THEME.md)
        self.status_messages = [
            "Maintenance Terminal Online. Your predecessor's wasn't.",
            "All systems operational. Legally speaking.",
            "REMINDER: Your life insurance paperwork is still incomplete.",
            "Petrov would have solved this by now. We miss Petrov.",
            "Employee of the Month: Petrov (Month 48). Status: [REDACTED]",
            "NOTICE: Tuesday's evacuation drill cancelled due to actual emergency.",
            "The geiger counter is not a musical instrument. Please stop.",
            "The vending machine in break room 3 has achieved sentience. Avoid.",
            "Coffee machine is making that noise again. Do not investigate.",
            "Radiation levels within acceptable parameters. Parameters have been revised.",
            "Your Form 27-B (Death Waiver) remains unsigned. Please rectify.",
            "The suggestion box remains welded shut. This is for your protection.",
            "Doris from HR is checking on something. Doris has been checking since 1974.",
            "The fluorescent lights have always flickered. Stop asking about it.",
            "NOTICE: This emergency counts as your lunch break.",
            "Previous shift logged 'strange humming.' Disregard.",
            "FUN FACT: The reactor core is older than most employees' children.",
            "The Safety Salamander wishes you a productive shift!",
            "MEMO: Screaming in the reactor room has been resolved. Do not investigate how.",
            "Your exposure badge is glowing. This is normal. Probably.",
            "The window to the reactor room is NOT a door. Stop trying.",
            "REMINDER: Dying on company property requires Form 19-C in triplicate.",
            "The motivational poster is watching. Smile at the atom.",
            "Asbestos inspection: PASSED! You're welcome.",
            "Tonight's mandatory fun activity has been cancelled due to fatalities.",
            "Big Oil infiltration status: unclear. Trust no one. Especially Craig.",
            "NOTICE: The break room microwave has been confiscated for evidence.",
            "Your predecessor's personal effects are still in locker 7-G. No rush.",
            "Temperature nominal. Ignore the smell.",
            "The reactor's 'mood' today: pensive.",
        ]
        self.message_index = 0
        self.message_timer = 0.0
        # Log of displayed messages (newest first) - each entry is (message, wrapped_lines)
        self.message_log: List[str] = [self.status_messages[0]]
        
        # Scroll animation state
        self.scroll_offset = 0.0  # Lines to scroll up (0 = fully visible, positive = hidden above)
        self.scroll_speed = 8.0   # Lines per second for scroll animation
        
        # Border flash state
        self.flash_timer = 0.0
        self.flash_on = True
    
    def update(self, dt: float, game_state: "GameState"):
        """Update the panel state."""
        # Update timer display
        self.timer.set_time(game_state.time_remaining)
        self.timer.fg = self._get_timer_color(game_state.time_remaining)
        
        # Update strikes
        self.strike_indicator.set_strikes(game_state.strikes)
        
        # Update temperature
        self.temp_gauge.set_value(game_state.temperature)
        
        # Animate scroll offset toward 0 (fully visible)
        if self.scroll_offset > 0:
            self.scroll_offset = max(0, self.scroll_offset - self.scroll_speed * dt)
        
        # Add new status messages to log
        self.message_timer += dt
        if self.message_timer >= 5.0:
            self.message_timer = 0.0
            self.message_index = (self.message_index + 1) % len(self.status_messages)
            # Add new message to front of log
            new_msg = self.status_messages[self.message_index]
            self.message_log.insert(0, new_msg)
            # Calculate lines needed for new message (+ 1 for blank line separator)
            max_width = self.width - 6
            wrapped = self._wrap_message(new_msg, max_width, "> ")
            # Set scroll offset to hide new message initially (lines + blank line)
            self.scroll_offset = len(wrapped) + 1
        
        # Update border flash timer based on strikes
        if game_state.strikes >= 1:
            flash_interval = 1.0 if game_state.strikes >= 2 else 2.0
            self.flash_timer += dt
            if self.flash_timer >= flash_interval:
                self.flash_timer = 0.0
                self.flash_on = not self.flash_on
        else:
            # Reset flash state when no strikes
            self.flash_timer = 0.0
            self.flash_on = True
    
    def _get_timer_color(self, time_remaining: float) -> int:
        """Get timer color based on urgency."""
        if time_remaining < 60:
            return Color.LIGHT_RED
        elif time_remaining < 120:
            return Color.LIGHT_YELLOW
        return Color.LIGHT_GREEN
    
    def _get_border_color(self, strikes: int) -> int:
        """Get border color based on current strike count, with flashing."""
        if strikes >= 2:
            # Flash between red and dark red every 1 second
            return Color.LIGHT_RED if self.flash_on else Color.RED
        elif strikes >= 1:
            # Flash between yellow and dark yellow every 2 seconds
            return Color.LIGHT_YELLOW if self.flash_on else Color.YELLOW
        return Color.GREEN
    
    def render(self, buffer: "TextBuffer", game_state: "GameState"):
        """Render the reactor status panel."""
        # Panel frame - color changes based on strike count
        border_color = self._get_border_color(game_state.strikes)
        draw_titled_box(buffer, self.x, self.y, self.width, self.height,
                       "REACTOR STATUS", DOUBLE, border_color, Color.LIGHT_CYAN)
        
        # Timer
        buffer.put_string(self.x + 2, self.y + 2, "TIME:", Color.LIGHT_GREEN)
        self.timer.render(buffer)
        
        # Strikes
        buffer.put_string(self.x + 2, self.y + 4, "ERRORS:", Color.LIGHT_GREEN)
        self.strike_indicator.render(buffer)
        
        # Module progress (below errors)
        buffer.put_string(self.x + 2, self.y + 5, "SOLVED:", Color.LIGHT_GREEN)
        self.module_progress.set_progress(game_state.modules_solved, game_state.modules_total)
        self.module_progress.render(buffer)
        
        # Temperature
        buffer.put_string(self.x + 2, self.y + 7, "TEMP:", Color.LIGHT_GREEN)
        self.temp_gauge.render(buffer)
        
        # Divider
        y = self.y + 10
        buffer.put_string(self.x + 2, y, "─" * (self.width - 4), Color.GREEN)
        
        # Status messages (more vertical space now)
        y += 2
        self._render_status_messages(buffer, y)
    
    def _render_status_messages(self, buffer: "TextBuffer", y: int):
        """Render the scrolling status log with newest message in white."""
        buffer.put_string(self.x + 2, y, "SYSTEM LOG:", Color.LIGHT_CYAN)
        y += 1
        
        max_width = self.width - 6
        # Calculate available lines for log (use full remaining height)
        max_y = self.y + self.height - 2
        
        # Track how many lines we've "scrolled past" for the animation
        lines_to_skip = int(self.scroll_offset)
        lines_skipped = 0
        
        for i, msg in enumerate(self.message_log):
            if y > max_y:
                break
            
            # Newest message (index 0) in white, others in grey
            color = Color.WHITE if i == 0 else Color.DARK_GRAY
            prefix = "> " if i == 0 else "  "
            
            # Word wrap the message
            lines = self._wrap_message(msg, max_width, prefix)
            for line in lines:
                if y > max_y:
                    break
                # Skip lines that are still "scrolling in"
                if lines_skipped < lines_to_skip:
                    lines_skipped += 1
                    continue
                buffer.put_string(self.x + 2, y, line, color)
                y += 1
            
            # Add blank line between messages (if there's room)
            if y <= max_y:
                # Skip the blank line too if we're still scrolling
                if lines_skipped < lines_to_skip:
                    lines_skipped += 1
                else:
                    y += 1  # Blank line separator
    
    def _wrap_message(self, msg: str, max_width: int, prefix: str) -> List[str]:
        """Word-wrap a message to fit within max_width."""
        words = msg.split()
        lines = []
        line = prefix
        
        for word in words:
            if len(line) + len(word) + 1 <= max_width:
                line += word + " "
            else:
                lines.append(line.rstrip())
                line = "  " + word + " "
        
        if line.strip():
            lines.append(line.rstrip())
        
        return lines
