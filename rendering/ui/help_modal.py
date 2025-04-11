import pygame as pg
from typing import List, Tuple, Dict

from config import SAND_DARK, SAND_MEDIUM, SAND_LIGHT, CACTUS_DARK, FIG, BLACK
from .panel import Panel

class HelpModal(Panel):
    """Modal panel that displays keyboard shortcuts and controls help"""
    
    def __init__(self, screen_width: int, screen_height: int):
        # Create a centered modal rect that's 60% of screen width and height
        width = int(screen_width * 0.6)
        height = int(screen_height * 0.6)
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        
        super().__init__(pg.Rect(x, y, width, height), title="Keyboard Shortcuts")
        
        # Initialize shortcuts dictionary
        self.shortcuts: Dict[str, List[Tuple[str, str]]] = {
            "Game Controls": [
                ("Space", "Pause/Resume simulation"),
                ("ESC", "Exit game"),
                ("=", "Increase simulation speed"),
                ("-", "Decrease simulation speed"),
                ("?", "Show/Hide this help")
            ],
            "View Controls": [
                ("1", "Switch to Main view"),
                ("2", "Switch to Analytics view"),
                ("3", "Switch to Achievements view"),
                ("4", "Switch to Settings view")
            ],
            "Tool Shortcuts": [
                ("Q", "Select Cactus tool"),
                ("W", "Select Desert Grass tool"),
                ("E", "Select Succulent tool"),
                ("R", "Select Herbivore tool"),
                ("T", "Select Carnivore tool"),
                ("Y", "Select Rain tool"),
                ("U", "Select Water tool")
            ]
        }
        
        # Visible state
        self.visible = False
        
        # Calculate layout
        self.content_rect = pg.Rect(
            self.rect.left + 20,
            self.rect.top + 40,  # Leave room for title
            self.rect.width - 40,
            self.rect.height - 60
        )
        
        # Font for section titles and shortcuts
        self.title_font = pg.font.Font(None, 28)
        self.shortcut_font = pg.font.Font(None, 24)
        
        # Colors
        self.title_color = CACTUS_DARK
        self.shortcut_color = FIG
        self.description_color = BLACK
        
    def draw(self, surface: pg.Surface) -> None:
        """Draw the help modal with all shortcuts"""
        if not self.visible:
            return
            
        # Draw panel background and border
        super().draw(surface)
        
        # Draw content
        y_offset = self.content_rect.top
        section_spacing = 30
        shortcut_spacing = 25
        
        for section, shortcuts in self.shortcuts.items():
            # Draw section title
            title_surface = self.title_font.render(section, True, self.title_color)
            surface.blit(title_surface, (self.content_rect.left, y_offset))
            y_offset += 30
            
            # Draw shortcuts in this section
            for key, description in shortcuts:
                # Draw key in a box
                key_surface = self.shortcut_font.render(key, True, self.shortcut_color)
                key_rect = key_surface.get_rect()
                key_rect.topleft = (self.content_rect.left + 20, y_offset)
                
                # Draw key background
                pg.draw.rect(surface, (217, 177, 102), key_rect.inflate(10, 4), border_radius=4)
                surface.blit(key_surface, key_rect)
                
                # Draw description
                desc_surface = self.shortcut_font.render(description, True, self.description_color)
                surface.blit(desc_surface, (key_rect.right + 20, y_offset))
                
                y_offset += shortcut_spacing
            
            y_offset += section_spacing
    
    def handle_event(self, event: pg.event.Event) -> bool:
        """Handle events for the help modal"""
        if not self.visible:
            return False
            
        if event.type == pg.KEYDOWN and event.key == pg.K_QUESTION:
            self.toggle()
            return True
            
        if event.type == pg.MOUSEBUTTONDOWN:
            # Close if clicked outside the modal
            if not self.rect.collidepoint(event.pos):
                self.hide()
                return True
                
        return False
    
    def toggle(self) -> None:
        """Toggle the visibility of the help modal"""
        self.visible = not self.visible
    
    def show(self) -> None:
        """Show the help modal"""
        self.visible = True
    
    def hide(self) -> None:
        """Hide the help modal"""
        self.visible = False 