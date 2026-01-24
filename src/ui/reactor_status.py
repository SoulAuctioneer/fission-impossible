"""
Reactor status panel - displays timer, strikes, module progress, and temperature.

PANEL LAYOUT (35 wide × 30 tall, positioned at x=103, y=3)
═════════════════════════════════════════════════════════════════════════════════

    ╔═════════════════════════════════╗
    ║       REACTOR STATUS            ║  <- y+0: Title
    ║                                 ║
    ║  TIME:   04:32                  ║  <- y+2: Timer display
    ║  ERRORS: [■] [■] [·]            ║  <- y+4: Strike indicators
    ║                                 ║  <- y+5: (blank)
    ║  FIXED:  [■] [■] [■] [·] [·] [·]║  <- y+6: Module progress
    ║                                 ║  <- y+7: (blank)
    ║  TEMP: ▓▓▓▓▓▓▓░░░░░░░░░░░░░░░░░░ ║  <- y+8: Temperature gauge (inline)
    ║  ─────────────────────────────  ║  <- y+10: Divider
    ║  SYSTEM LOG:                    ║  <- y+12: Log header
    ║                                 ║  <- y+14: (blank)
    ║  > Latest message in white...   ║  <- y+15+: Scrolling log
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
        self.module_progress = ModuleProgressIndicator(x + 10, y + 6)
        self.temp_gauge = TemperatureGauge(x + 10, y + 8, width - 12)  # Inline, aligned with other readouts
        
        # Status messages (themed from THEME.md)
        self.status_messages = [
            "All systems operational. Legally speaking.",
            "REMINDER: Your Form 27-B (Death Waiver) remains unsigned. Please rectify.",
            "REMINDER: Oleg is not authorized to seduce the fuel rods. Please report breaches to HR.",
            "NOTICE: Tuesday's evacuation drill cancelled due to actual emergency.",
            "The geiger counter is not a musical instrument. Please stop.",
            "ALERT: Immaculate vibes detected in reactor core. System overload imminent.",
            "REMINDER: Team meeting at 12:00AM.",
            "NOTICE: 'Cool fusion' research proposal rejected. Again. See: Incident Report #4024.",
            "MEMO: Consulting ChatGPT for reactor calculations is NOT an approved safety protocol.",
            "CORRECTION: Uranium isotope error detected. ChatGPT has been notified.",
            "Radiation levels within acceptable parameters. Parameters have been revised.",
            "NOTICE: 'Take his rod' is not standard reactor terminology. Please use Form 44-R.",
            "REMINDER: Fuel rods are not face-caressing implements. See: Incident Report #4024.",
            "Elena's safety record remains ZERO. Elena is always watching.",
            "The vending machine in break room 3 has achieved sentience. Avoid.",
            "NOTICE: This emergency counts as your lunch break.",
            "Stasia has enacted the Personal Emergency Protocol. Who's a good boss?",
            "WARNING: Your predecessor tried Cool Fusion. Your predecessor is now a cautionary tale.",
            "Coffee machine is making that noise again. Do not investigate.",
            "REMINDER: These are we-anium problems, not uranium problems.",
            "The suggestion box remains welded shut. This is for your protection.",
            "MEMO: Sergei's retirement paperwork is 69 days overdue. Forms are accumulating.",
            "Stasia from HR is checking on something. Stasia has been checking since 1974.",
            "ALERT: Someone pressed The Button again. Culprit search in progress.",
            "The fluorescent lights have always flickered. Stop asking about it.",
            "The President's visit has been cancelled. He was informed about The Button.",
            "MEMO: Screaming in the reactor room has been resolved. Do not investigate how.",
            "Your dosimeter is glowing. This is normal. Probably.",
            "Sergei's Wordle streak: 1,247 days. Safety streak: Pending.",
            "REMINDER: Dying on company property requires Form 19-C in triplicate.",
            "The motivational poster is watching. Smile at the atom.",
            "NOTICE: 'Vibes' are not a recognized coolant. Stop trying.",
            "Tonight's mandatory fun activity has been cancelled due to fatalities.",
            "Big Oil infiltration status: unclear. Trust no one. Especially Craig.",
            "MEMO: Oleg's fuel rods have been quarantined. Do not ask where.",
            "WARNING: Your vibes are too strong. The reactor cannot handle this.",
            "NOTICE: The break room microwave has been confiscated for evidence.",
            "Temperature nominal. Ignore the smell.",
            "The reactor's 'mood' today: OVERWHELMED BY VIBES.",
            "NOTICE: The next employee to yell 'take his rod' receives a write-up.",
            "MEMO: 'Projectile dysfunction' is now the official term. Thank Elena.",
            "NOTICE: Level 7 accidents and Level 7 personal crises use the same form.",
            "The easy button was too easy. We should have known.",
            "The turbines have prematurely actuated. Cleanup crew dispatched.",
            "REMINDER: Retirement can be accelerated by pressing The Button. Not recommended.",
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
        
        # Timer flash state (separate from border)
        self.timer_flash_timer = 0.0
        self.timer_flash_on = True
    
    def update(self, dt: float, game_state: "GameState"):
        """Update the panel state."""
        time_remaining = game_state.time_remaining
        
        # Update timer flash based on time remaining
        # Flash faster as time gets lower: 4min=2s, 3min=1.5s, 2min=1s, 1min=0.5s, 30s=0.25s
        if time_remaining < 30:
            flash_interval = 0.25
        elif time_remaining < 60:
            flash_interval = 0.5
        elif time_remaining < 120:
            flash_interval = 1.0
        elif time_remaining < 180:
            flash_interval = 1.5
        elif time_remaining < 240:
            flash_interval = 2.0
        else:
            flash_interval = 0  # No flashing above 4 minutes
        
        if flash_interval > 0:
            self.timer_flash_timer += dt
            if self.timer_flash_timer >= flash_interval:
                self.timer_flash_timer = 0.0
                self.timer_flash_on = not self.timer_flash_on
        else:
            self.timer_flash_on = True
            self.timer_flash_timer = 0.0
        
        # Update timer display
        self.timer.set_time(time_remaining)
        self.timer.fg = self._get_timer_color(time_remaining)
        
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
            flash_interval = 0.5 if game_state.strikes >= 2 else 1.0
            self.flash_timer += dt
            if self.flash_timer >= flash_interval:
                self.flash_timer = 0.0
                self.flash_on = not self.flash_on
        else:
            # Reset flash state when no strikes
            self.flash_timer = 0.0
            self.flash_on = True
    
    def _get_timer_color(self, time_remaining: float) -> int:
        """Get timer color based on urgency, with flashing."""
        # Determine base color based on time
        # Dim colors are much darker for dramatic contrast
        if time_remaining < 60:
            bright_color = Color.LIGHT_RED
            dim_color = Color.DARK_GRAY
        elif time_remaining < 120:
            bright_color = Color.LIGHT_YELLOW
            dim_color = Color.DARK_GRAY
        elif time_remaining < 180:
            bright_color = Color.LIGHT_GREEN
            dim_color = Color.DARK_GRAY
        elif time_remaining < 240:
            bright_color = Color.LIGHT_GREEN
            dim_color = Color.GREEN
        else:
            # No flashing above 4 minutes, always bright
            return Color.LIGHT_GREEN
        
        # Apply flash state
        return bright_color if self.timer_flash_on else dim_color
    
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
        
        # Module progress (below errors, with blank line)
        buffer.put_string(self.x + 2, self.y + 6, "FIXED:", Color.LIGHT_GREEN)
        self.module_progress.set_progress(game_state.modules_solved, game_state.modules_total)
        self.module_progress.render(buffer)
        
        # Temperature (inline with label)
        buffer.put_string(self.x + 2, self.y + 8, "TEMP:", Color.LIGHT_GREEN)
        self.temp_gauge.render(buffer)
        
        # Divider (moved up one line)
        y = self.y + 10
        buffer.put_string(self.x + 2, y, "─" * (self.width - 4), Color.GREEN)
        
        # Status messages (gained one line for log)
        y += 2
        self._render_status_messages(buffer, y)
    
    def _render_status_messages(self, buffer: "TextBuffer", y: int):
        """Render the scrolling status log with newest message in white."""
        buffer.put_string(self.x + 2, y, "MAINTENANCE LOG:", Color.LIGHT_CYAN)
        y += 2  # Blank line after header
        
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
