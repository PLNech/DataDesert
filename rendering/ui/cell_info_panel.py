import pygame as pg
from .panel import Panel

class CellInfoPanel(Panel):
    """Panel displaying information about the currently selected cell"""
    
    def __init__(self, rect: pg.Rect):
        super().__init__(rect, title="Cell Info")
        self.entity = None
        self.cell_position = None
        self.moisture = 0.0
        self.nutrients = 0.0
        self.font = pg.font.SysFont('Arial', 14)
    
    def update_info(self, entity, position=None, moisture=0.0, nutrients=0.0) -> None:
        """Update the panel with information about an entity and environment"""
        self.entity = entity
        self.cell_position = position
        self.moisture = moisture
        self.nutrients = nutrients
    
    def draw(self, surface: pg.Surface) -> None:
        """Draw the panel with entity and environmental information"""
        super().draw(surface)
        if not self.visible:
            return
            
        y_pos = self.rect.top + 30
        text_color = (220, 220, 220)
        
        # Draw position info if available
        if self.cell_position:
            pos_text = f"Position: ({self.cell_position[0]}, {self.cell_position[1]})"
            text_surf = self.font.render(pos_text, True, text_color)
            surface.blit(text_surf, (self.rect.left + 10, y_pos))
            y_pos += 20
        
        # Draw environmental info
        moisture_text = f"Moisture: {self.moisture:.2f}"
        text_surf = self.font.render(moisture_text, True, text_color)
        surface.blit(text_surf, (self.rect.left + 10, y_pos))
        y_pos += 20
        
        nutrients_text = f"Nutrients: {self.nutrients:.2f}"
        text_surf = self.font.render(nutrients_text, True, text_color)
        surface.blit(text_surf, (self.rect.left + 10, y_pos))
        y_pos += 20
        
        # Draw entity info if available
        if self.entity:
            # Draw divider
            pg.draw.line(surface, (100, 100, 100), 
                        (self.rect.left + 10, y_pos), 
                        (self.rect.right - 10, y_pos), 1)
            y_pos += 10
            
            # Entity type header
            type_text = f"Entity: {type(self.entity).__name__}"
            text_surf = self.font.render(type_text, True, (255, 255, 150))
            surface.blit(text_surf, (self.rect.left + 10, y_pos))
            y_pos += 20
            
            # Entity properties
            props = vars(self.entity)
            for i, (key, value) in enumerate(props.items()):
                if key.startswith('_') or key == 'id' or key == 'position':
                    continue
                    
                # Format the value based on its type
                if isinstance(value, float):
                    formatted_value = f"{value:.2f}"
                else:
                    formatted_value = str(value)
                    
                prop_text = f"{key}: {formatted_value}"
                
                # Truncate if too long
                if len(prop_text) > 30:
                    prop_text = prop_text[:27] + "..."
                
                text_surf = self.font.render(prop_text, True, text_color)
                surface.blit(text_surf, (self.rect.left + 15, y_pos))
                y_pos += 18
                
                # Stop if we're running out of space
                if y_pos > self.rect.bottom - 20:
                    break 