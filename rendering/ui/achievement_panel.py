import pygame as pg
from typing import List, Dict

from config import BLACK, GREY, SAND_MEDIUM, FIG, SAND_DARK, ACCENT, CACTUS_DARK
from .panel import Panel

class AchievementPanel(Panel):
    """Panel showing player achievements"""
    
    def __init__(self, rect: pg.Rect):
        super().__init__(rect, title="Achievements")
        self.achievements: List[Dict] = []
        self.font = pg.font.SysFont('Arial', 14)
    
    def add_achievement(self, title: str, description: str, completed: bool = False) -> None:
        """Add a new achievement to track"""
        self.achievements.append({
            'title': title,
            'description': description,
            'completed': completed
        })
    
    def draw(self, surface: pg.Surface) -> None:
        """Draw the panel and list of achievements"""
        super().draw(surface)
        if not self.visible:
            return
            
        y_pos = self.rect.top + 35  # Position after title
        
        for achievement in self.achievements:
            # Achievement title - brighter colors for better readability
            title_color = FIG if achievement['completed'] else SAND_DARK
            title_text = self.font.render(achievement['title'], True, title_color)
            surface.blit(title_text, (self.rect.left + 10, y_pos))
            
            # Achievement description - brighter color
            desc_text = self.font.render(achievement['description'], True, CACTUS_DARK)
            surface.blit(desc_text, (self.rect.left + 15, y_pos + 20))
            
            # Check mark for completed achievements
            if achievement['completed']:
                pg.draw.circle(surface, FIG, (self.rect.right - 15, y_pos + 10), 6)
            
            y_pos += 45  # Space between achievements 