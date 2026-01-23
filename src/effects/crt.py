"""
CRT post-processing effects - applies scanlines, vignette, glow, and refresh line
to the rendered pygame surface for authentic CRT monitor aesthetics.
"""
import pygame
import numpy as np
from typing import Optional


class CRTPostProcessor:
    """
    Applies CRT-style post-processing effects to a pygame Surface.
    
    Effects are applied in this order:
    1. Phosphor glow (subtle brightness boost)
    2. Scanlines overlay
    3. Vignette overlay
    4. Moving refresh line
    """
    
    def __init__(
        self,
        width: int,
        height: int,
        scanlines: bool = True,
        scanline_alpha: int = 40,
        vignette: bool = True,
        vignette_strength: float = 0.3,
        refresh_line: bool = True,
        refresh_speed: float = 200.0,
        glow: bool = True,
        glow_strength: int = 10,
        indicator_glow_strength: int = 60,
    ):
        self.width = width
        self.height = height
        
        # Effect toggles and settings
        self.scanlines_enabled = scanlines
        self.scanline_alpha = scanline_alpha
        self.vignette_enabled = vignette
        self.vignette_strength = vignette_strength
        self.refresh_line_enabled = refresh_line
        self.refresh_speed = refresh_speed
        self.glow_enabled = glow
        self.glow_strength = glow_strength
        self.indicator_glow_strength = indicator_glow_strength  # Stronger glow for lit indicators
        
        # Dynamic state
        self._refresh_y = 0.0
        
        # Pre-render static overlays
        self._scanline_surface: Optional[pygame.Surface] = None
        self._vignette_surface: Optional[pygame.Surface] = None
        
        if self.scanlines_enabled:
            self._scanline_surface = self._create_scanlines()
        if self.vignette_enabled:
            self._vignette_surface = self._create_vignette()
    
    def _create_scanlines(self) -> pygame.Surface:
        """Create a pre-rendered scanline overlay surface."""
        surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # Draw semi-transparent black lines every 2 pixels
        for y in range(0, self.height, 2):
            pygame.draw.line(
                surface,
                (0, 0, 0, self.scanline_alpha),
                (0, y),
                (self.width, y)
            )
        
        return surface
    
    def _create_vignette(self) -> pygame.Surface:
        """Create a pre-rendered vignette overlay using radial gradient."""
        surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # Use numpy for efficient gradient creation
        center_x = self.width / 2
        center_y = self.height / 2
        max_distance = np.sqrt(center_x ** 2 + center_y ** 2)
        
        # Create coordinate arrays
        y_coords, x_coords = np.ogrid[:self.height, :self.width]
        
        # Calculate distance from center (normalized)
        distance = np.sqrt((x_coords - center_x) ** 2 + (y_coords - center_y) ** 2)
        distance = distance / max_distance
        
        # Apply vignette curve (stronger at edges)
        # Use a power function for smooth falloff
        alpha = (distance ** 2) * self.vignette_strength * 255
        alpha = np.clip(alpha, 0, 255).astype(np.uint8)
        
        # Create RGBA array
        pixels = pygame.surfarray.pixels_alpha(surface)
        pixels[:] = alpha.T  # Transpose because pygame uses (x, y) not (y, x)
        del pixels  # Release the surface lock
        
        # Fill with black (alpha already set)
        black_surface = pygame.Surface((self.width, self.height))
        black_surface.fill((0, 0, 0))
        surface.blit(black_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        
        # Re-apply alpha after the blit
        pixels = pygame.surfarray.pixels_alpha(surface)
        pixels[:] = alpha.T
        del pixels
        
        return surface
    
    def apply(self, surface: pygame.Surface, dt: float, glow_layer: pygame.Surface = None) -> pygame.Surface:
        """
        Apply all CRT effects to the surface.
        
        Args:
            surface: The pygame Surface to apply effects to (modified in place)
            dt: Delta time in seconds for animation
            glow_layer: Optional surface containing only high-glow characters (lit indicators)
            
        Returns:
            The modified surface
        """
        # 1. Apply phosphor glow (subtle brightness/color boost)
        if self.glow_enabled:
            self._apply_glow(surface)
        
        # 1b. Apply stronger glow to indicator layer if provided
        if self.glow_enabled and glow_layer is not None:
            self._apply_indicator_glow(surface, glow_layer)
        
        # 2. Apply scanlines overlay
        if self.scanlines_enabled and self._scanline_surface:
            surface.blit(self._scanline_surface, (0, 0))
        
        # 3. Apply vignette overlay
        if self.vignette_enabled and self._vignette_surface:
            surface.blit(self._vignette_surface, (0, 0))
        
        # 4. Draw moving refresh line
        if self.refresh_line_enabled:
            self._draw_refresh_line(surface, dt)
        
        return surface
    
    def _apply_glow(self, surface: pygame.Surface):
        """
        Apply phosphor bloom/glow effect to text.
        
        Creates a bloom effect by:
        1. Downsampling the surface (creates blur via bilinear filtering)
        2. Upsampling back to original size
        3. Adding the blurred version with additive blending
        
        This simulates the phosphor glow of CRT monitors where bright
        pixels bleed light into surrounding areas.
        """
        # Blur scale factor - smaller = more blur, larger = less blur
        # 4 means we downsample to 1/4 size then back up
        blur_scale = 4
        small_width = max(1, self.width // blur_scale)
        small_height = max(1, self.height // blur_scale)
        
        # Downsample (this creates blur via averaging)
        small_surface = pygame.transform.smoothscale(surface, (small_width, small_height))
        
        # Apply a green/cyan phosphor tint to the blurred version
        tint_surface = pygame.Surface((small_width, small_height))
        tint_surface.fill((0, 40, 20))  # Green phosphor tint
        small_surface.blit(tint_surface, (0, 0), special_flags=pygame.BLEND_RGB_ADD)
        
        # Upsample back to original size (this spreads the blur)
        bloom_surface = pygame.transform.smoothscale(small_surface, (self.width, self.height))
        
        # Control bloom intensity - scale the RGB values
        # Using surfarray for efficient pixel manipulation
        bloom_array = pygame.surfarray.pixels3d(bloom_surface)
        intensity_factor = self.glow_strength / 50.0  # Normalize to 0.0-1.0 range (assuming max 50)
        bloom_array[:] = np.clip(bloom_array * intensity_factor, 0, 255).astype(np.uint8)
        del bloom_array  # Release surface lock
        
        # Add the bloom to the original surface
        surface.blit(bloom_surface, (0, 0), special_flags=pygame.BLEND_RGB_ADD)
    
    def _apply_indicator_glow(self, surface: pygame.Surface, glow_layer: pygame.Surface):
        """
        Apply stronger phosphor glow specifically to lit indicators.
        
        Uses the same bloom technique but with higher intensity for
        characters marked as "lit" (high-glow), creating a bright
        LED-like effect for indicator lights.
        """
        # Use a larger blur for more spread
        blur_scale = 3
        small_width = max(1, self.width // blur_scale)
        small_height = max(1, self.height // blur_scale)
        
        # Downsample the glow layer
        small_surface = pygame.transform.smoothscale(glow_layer, (small_width, small_height))
        
        # Upsample back
        bloom_surface = pygame.transform.smoothscale(small_surface, (self.width, self.height))
        
        # Apply stronger intensity
        bloom_array = pygame.surfarray.pixels3d(bloom_surface)
        intensity_factor = self.indicator_glow_strength / 50.0
        bloom_array[:] = np.clip(bloom_array * intensity_factor, 0, 255).astype(np.uint8)
        del bloom_array
        
        # Add the indicator bloom
        surface.blit(bloom_surface, (0, 0), special_flags=pygame.BLEND_RGB_ADD)
    
    def _draw_refresh_line(self, surface: pygame.Surface, dt: float):
        """Draw the moving CRT refresh/scan line."""
        # Update position
        self._refresh_y += self.refresh_speed * dt
        if self._refresh_y >= self.height:
            self._refresh_y = 0.0
        
        y = int(self._refresh_y)
        
        # Draw a brighter horizontal line (the "refresh" beam)
        # Main bright line
        line_surface = pygame.Surface((self.width, 1))
        line_surface.fill((20, 40, 30))  # Slight green-tinted brightness boost
        surface.blit(line_surface, (0, y), special_flags=pygame.BLEND_RGB_ADD)
        
        # Subtle trail above (fading phosphor)
        for i in range(1, 4):
            if y - i >= 0:
                trail_alpha = 15 - (i * 4)
                if trail_alpha > 0:
                    trail_surface = pygame.Surface((self.width, 1))
                    trail_surface.fill((trail_alpha, trail_alpha * 2, trail_alpha))
                    surface.blit(trail_surface, (0, y - i), special_flags=pygame.BLEND_RGB_ADD)
    
    def toggle_scanlines(self, enabled: Optional[bool] = None):
        """Toggle scanlines effect."""
        if enabled is None:
            self.scanlines_enabled = not self.scanlines_enabled
        else:
            self.scanlines_enabled = enabled
    
    def toggle_vignette(self, enabled: Optional[bool] = None):
        """Toggle vignette effect."""
        if enabled is None:
            self.vignette_enabled = not self.vignette_enabled
        else:
            self.vignette_enabled = enabled
    
    def toggle_refresh_line(self, enabled: Optional[bool] = None):
        """Toggle refresh line effect."""
        if enabled is None:
            self.refresh_line_enabled = not self.refresh_line_enabled
        else:
            self.refresh_line_enabled = enabled
    
    def toggle_glow(self, enabled: Optional[bool] = None):
        """Toggle glow effect."""
        if enabled is None:
            self.glow_enabled = not self.glow_enabled
        else:
            self.glow_enabled = enabled
    
    def toggle_all(self, enabled: bool):
        """Enable or disable all effects at once."""
        self.scanlines_enabled = enabled
        self.vignette_enabled = enabled
        self.refresh_line_enabled = enabled
        self.glow_enabled = enabled
