import pygame as pg
from typing import Callable, Tuple
from .button import Button

class TabButton(Button):
    """Button specifically for tabs with selected state"""
    
    def __init__(self, 
                 rect: pg.Rect, 
                 text: str, 
                 callback: Callable = None,
                 color: Tuple[int, int, int] = (80, 80, 80)):
        super().__init__(rect, text, callback, color)
        self.selected = False
        self.selected_color = (150, 150, 150)
    
    def draw(self, surface: pg.Surface) -> None:
        """Draw the tab button, with different appearance when selected"""
        # Determine button color based on state
        if self.selected:
            current_color = self.selected_color
        else:
            current_color = self.color
            if self.hover:
                # Lighten color when hovering
                current_color = tuple(min(c + 30, 255) for c in self.color)
            
        # Draw button background with rounded corners (only top corners)
        pg.draw.rect(surface, current_color, self.rect,
                    border_top_left_radius=5,
                    border_top_right_radius=5)
        
        # Draw borders
        border_color = (200, 200, 200)
        if not self.selected:
            # Draw bottom border if not selected
            pg.draw.line(surface, border_color,
                        (self.rect.left, self.rect.bottom - 1),
                        (self.rect.right, self.rect.bottom - 1), 2)
        
        # Draw side and top borders
        pg.draw.line(surface, border_color,
                    (self.rect.left, self.rect.top),
                    (self.rect.right, self.rect.top), 2)
        pg.draw.line(surface, border_color,
                    (self.rect.left, self.rect.top),
                    (self.rect.left, self.rect.bottom), 2)
        pg.draw.line(surface, border_color,
                    (self.rect.right - 2, self.rect.top),
                    (self.rect.right - 2, self.rect.bottom), 2)
        
        # Draw text
        text_surface = self.font.render(self.text, True, (245, 233, 208))
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)
    
    def set_selected(self, selected: bool) -> None:
        """Set the selected state of the tab"""
        self.selected = selected 