import pygame as pg
from typing import Tuple
import os

class Panel:
    """Base class for UI panels"""
    
    def __init__(self, rect: pg.Rect, title: str = ""):
        self.rect = rect
        self.title = title
        self.visible = True
        
        # Border and style properties
        self.border_radius = 8
        self.border_width = 2
        self.background_color = (245, 233, 208)  # Light sand
        self.border_color = (172, 125, 96)       # Brown
        self.title_color = (88, 62, 35)          # Dark brown
        self.title_height = 25
        
        # Initialize font with proper path handling
        try:
            font_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'fonts', 'cedarville.ttf')
            self.font = pg.font.Font(font_path, 18)  # Increased font size
        except (FileNotFoundError, OSError):
            print("Warning: Could not load cedarville font, using system font instead")
            self.font = pg.font.SysFont('Arial', 18)
            
    def draw(self, surface: pg.Surface) -> None:
        """Draw the panel with rounded corners"""
        if not self.visible:
            return
            
        # Draw panel background with rounded corners
        pg.draw.rect(
            surface,
            self.background_color,
            self.rect,
            border_radius=self.border_radius
        )
        
        # Draw border with rounded corners
        pg.draw.rect(
            surface,
            self.border_color,
            self.rect,
            width=self.border_width,
            border_radius=self.border_radius
        )
        
        # Draw title if provided
        if self.title:
            title_rect = pg.Rect(
                self.rect.left,
                self.rect.top,
                self.rect.width,
                self.title_height
            )
            
            # Draw title background
            pg.draw.rect(
                surface,
                self.border_color,
                title_rect,
                border_top_left_radius=self.border_radius,
                border_top_right_radius=self.border_radius
            )
            
            # Draw title text
            title_text = self.font.render(self.title, True, (245, 233, 208))
            text_x = self.rect.left + (self.rect.width - title_text.get_width()) // 2
            text_y = self.rect.top + (self.title_height - title_text.get_height()) // 2
            surface.blit(title_text, (text_x, text_y))
    
    def handle_event(self, event: pg.event.Event) -> bool:
        """Handle events for the panel, to be implemented by subclasses"""
        return False

    def set_visible(self, visible: bool) -> None:
        """Set panel visibility"""
        self.visible = visible 