import pygame as pg
from typing import Tuple

class Panel:
    """Base class for UI panels"""
    
    def __init__(self, rect: pg.Rect, title: str = "", bg_color: Tuple[int, int, int] = (70, 70, 70)):
        self.rect = rect
        self.title = title
        self.bg_color = bg_color
        self.font = pg.font.SysFont('Arial', 18)
        self.visible = True
    
    def draw(self, surface: pg.Surface) -> None:
        """Draw the panel and its title"""
        if not self.visible:
            return
            
        # Draw panel background
        pg.draw.rect(surface, self.bg_color, self.rect)
        pg.draw.rect(surface, (40, 40, 40), self.rect, 2)  # Border
        
        # Draw panel title if provided
        if self.title:
            title_surf = self.font.render(self.title, True, (255, 255, 255))
            title_rect = title_surf.get_rect(midtop=(self.rect.centerx, self.rect.top + 5))
            surface.blit(title_surf, title_rect)
    
    def handle_event(self, event: pg.event.Event) -> bool:
        """Handle events for the panel, to be implemented by subclasses"""
        return False

    def set_visible(self, visible: bool) -> None:
        """Set panel visibility"""
        self.visible = visible 