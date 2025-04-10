import pygame as pg
from typing import List, Callable, Optional
from .panel import Panel
from .button import Button

class ToolPanel(Panel):
    """Panel for tool selection with buttons"""
    
    def __init__(self, rect: pg.Rect):
        super().__init__(rect, title="Tools")
        self.buttons = []
        self.selected_tool = None
        self.tool_info = {}  # Tool information for tooltips
    
    def add_button(self, text: str, tool_id: str, callback: Optional[Callable] = None, info: Optional[str] = None) -> None:
        """Add a tool button to the panel"""
        # Calculate button position
        margin = 10
        button_width = self.rect.width - margin * 2
        button_height = 30
        
        y_pos = self.rect.top + 30 + len(self.buttons) * (button_height + margin)
        
        # Create button
        button = Button(
            pg.Rect(
                self.rect.left + margin,
                y_pos,
                button_width,
                button_height
            ),
            text,
            callback
        )
        
        # Store the tool ID and info
        button.tool_id = tool_id
        if info:
            self.tool_info[tool_id] = info
            
        self.buttons.append(button)
    
    def draw(self, surface: pg.Surface) -> None:
        """Draw the panel and its buttons"""
        super().draw(surface)
        if not self.visible:
            return
            
        for button in self.buttons:
            button.draw(surface)
            
            # Highlight selected tool
            if self.selected_tool and hasattr(button, 'tool_id') and button.tool_id == self.selected_tool:
                highlight_rect = pg.Rect(button.rect)
                highlight_rect.inflate_ip(4, 4)
                pg.draw.rect(surface, (255, 215, 0), highlight_rect, 2)
    
    def handle_event(self, event: pg.event.Event) -> bool:
        """Handle events for the panel and its buttons"""
        if not self.visible:
            return False
            
        for button in self.buttons:
            if button.handle_event(event):
                self.selected_tool = button.tool_id if hasattr(button, 'tool_id') else None
                return True
        return False
    
    def set_selected_tool(self, tool_id: str) -> None:
        """Set the currently selected tool"""
        self.selected_tool = tool_id
