import pygame as pg
from typing import Callable, Tuple
from .button import Button

class TabButton(Button):
    """Button specifically for tabs with selected state"""
    
    def __init__(self, 
                 rect: pg.Rect, 
                 text: str, 
                 callback: Callable = None,
                 color: Tuple[int, int, int] = (80, 80, 80),
                 hover_color: Tuple[int, int, int] = (120, 120, 120),
                 selected_color: Tuple[int, int, int] = (150, 150, 150),
                 text_color: Tuple[int, int, int] = (255, 255, 255),
                 font_size: int = 16):
        super().__init__(rect, text, callback, color, hover_color, text_color, font_size)
        self.selected = False
        self.selected_color = selected_color
    
    def draw(self, surface: pg.Surface) -> None:
        """Draw the tab button, with different appearance when selected"""
        if self.selected:
            color = self.selected_color
        elif self.hovered:
            color = self.hover_color
        else:
            color = self.color
            
        pg.draw.rect(surface, color, self.rect)
        # Only draw bottom border if not selected
        if not self.selected:
            pg.draw.line(surface, (50, 50, 50), 
                        (self.rect.left, self.rect.bottom - 1),
                        (self.rect.right, self.rect.bottom - 1), 2)
        
        # Always draw other borders
        pg.draw.line(surface, (50, 50, 50), 
                    (self.rect.left, self.rect.top),
                    (self.rect.right, self.rect.top), 2)
        pg.draw.line(surface, (50, 50, 50), 
                    (self.rect.left, self.rect.top),
                    (self.rect.left, self.rect.bottom), 2)
        pg.draw.line(surface, (50, 50, 50), 
                    (self.rect.right - 2, self.rect.top),
                    (self.rect.right - 2, self.rect.bottom), 2)
        
        # Draw button text
        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
    
    def set_selected(self, selected: bool) -> None:
        """Set the selected state of the tab"""
        self.selected = selected 