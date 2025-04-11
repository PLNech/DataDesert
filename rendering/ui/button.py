import pygame as pg
from typing import Callable, Optional, Tuple

class Button:
    """Interactive button with hover and click effects"""
    
    def __init__(self, rect: pg.Rect, text: str, callback: Optional[Callable] = None, color: Tuple[int, int, int] = (120, 120, 120)):
        self.rect = rect
        self.text = text
        self.callback = callback
        self.color = color
        self.hover = False
        
        # Create font
        self.font = pg.font.Font(None, 24)
        
    def draw(self, surface: pg.Surface) -> None:
        """Draw the button with current state"""
        # Determine button color based on state
        current_color = self.color
        if self.hover:
            # Lighten color when hovering
            current_color = tuple(min(c + 30, 255) for c in self.color)
            
        # Draw button background with rounded corners
        pg.draw.rect(surface, current_color, self.rect, border_radius=5)
        
        # Draw button border
        border_color = (200, 200, 200)
        pg.draw.rect(surface, border_color, self.rect, width=1, border_radius=5)
        
        # Render text
        text_surface = self.font.render(self.text, True, (245, 233, 208))
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)
        
    def handle_event(self, event: pg.event.Event) -> bool:
        """Handle mouse events for the button"""
        if event.type == pg.MOUSEMOTION:
            # Update hover state
            self.hover = self.rect.collidepoint(event.pos)
            return False
            
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                if self.callback:
                    self.callback()
                return True
                
        return False 