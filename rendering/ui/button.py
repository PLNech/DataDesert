import pygame as pg
from typing import Callable, Tuple, Optional

class Button:
    """Basic interactive button class"""
    
    def __init__(self, 
                 rect: pg.Rect, 
                 text: str, 
                 callback: Optional[Callable] = None, 
                 color: Tuple[int, int, int] = (100, 100, 100),
                 hover_color: Tuple[int, int, int] = (150, 150, 150),
                 text_color: Tuple[int, int, int] = (255, 255, 255),
                 font_size: int = 16):
        self.rect = rect
        self.text = text
        self.callback = callback
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.font_size = font_size
        self.hovered = False
        self.font = pg.font.SysFont('Arial', font_size)
        
    def draw(self, surface: pg.Surface) -> None:
        """Draw the button on the given surface"""
        # Draw button background
        color = self.hover_color if self.hovered else self.color
        pg.draw.rect(surface, color, self.rect)
        pg.draw.rect(surface, (50, 50, 50), self.rect, 2)  # Border
        
        # Draw button text
        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
    
    def handle_event(self, event: pg.event.Event) -> bool:
        """Handle pygame events, return True if the button was clicked"""
        if event.type == pg.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                if self.callback:
                    self.callback()
                return True
        return False 