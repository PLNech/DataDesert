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
        
        # Add scrolling support
        self.scroll_offset = 0
        self.max_scroll_offset = 0
        self.scroll_speed = 20
        self.button_height = 30
        self.button_margin = 10
        
    def add_button(self, text: str, tool_id: str, callback: Optional[Callable] = None, info: Optional[str] = None) -> None:
        """Add a tool button to the panel"""
        # Calculate button position
        margin = 10
        button_width = self.rect.width - margin * 2
        button_height = self.button_height
        
        # Position is based on number of buttons, but will be offset during drawing
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
        
        # Update max scroll offset based on total height of buttons
        total_buttons_height = len(self.buttons) * (button_height + margin)
        visible_height = self.rect.height - 30  # Subtract title height
        if total_buttons_height > visible_height:
            self.max_scroll_offset = total_buttons_height - visible_height
    
    def draw(self, surface: pg.Surface) -> None:
        """Draw the panel and its buttons"""
        super().draw(surface)
        if not self.visible:
            return
        
        # Create a clipping rect to prevent drawing outside the panel
        original_clip = surface.get_clip()
        clip_rect = pg.Rect(self.rect.left, self.rect.top + 30, 
                           self.rect.width, self.rect.height - 30)
        surface.set_clip(clip_rect)
            
        for button in self.buttons:
            # Apply scroll offset to button position
            adjusted_rect = button.rect.copy()
            adjusted_rect.y -= self.scroll_offset
            
            # Only draw if within visible area
            if adjusted_rect.bottom >= self.rect.top + 30 and adjusted_rect.top <= self.rect.bottom:
                # Temporarily modify button rect for drawing
                original_pos = button.rect.topleft
                button.rect.topleft = adjusted_rect.topleft
                
                button.draw(surface)
                
                # Highlight selected tool
                if self.selected_tool and hasattr(button, 'tool_id') and button.tool_id == self.selected_tool:
                    highlight_rect = pg.Rect(button.rect)
                    highlight_rect.inflate_ip(4, 4)
                    pg.draw.rect(surface, (255, 215, 0), highlight_rect, 2)
                
                # Restore original position
                button.rect.topleft = original_pos
                
        # Draw scroll indicators if needed
        if self.max_scroll_offset > 0:
            if self.scroll_offset > 0:
                # Draw up arrow
                pg.draw.polygon(surface, (255, 255, 255), [
                    (self.rect.right - 15, self.rect.top + 40),
                    (self.rect.right - 25, self.rect.top + 50),
                    (self.rect.right - 5, self.rect.top + 50),
                ])
            
            if self.scroll_offset < self.max_scroll_offset:
                # Draw down arrow
                pg.draw.polygon(surface, (255, 255, 255), [
                    (self.rect.right - 15, self.rect.bottom - 10),
                    (self.rect.right - 25, self.rect.bottom - 20),
                    (self.rect.right - 5, self.rect.bottom - 20),
                ])
        
        # Restore original clip
        surface.set_clip(original_clip)
    
    def handle_event(self, event: pg.event.Event) -> bool:
        """Handle events for the panel and its buttons"""
        if not self.visible:
            return False
        
        # Handle mouse wheel scrolling
        if event.type == pg.MOUSEWHEEL and self.rect.collidepoint(pg.mouse.get_pos()):
            self.scroll_offset = max(0, min(self.max_scroll_offset, 
                                      self.scroll_offset - event.y * self.scroll_speed))
            return True
            
        # Handle button clicks with scroll offset
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            for button in self.buttons:
                # Create an adjusted rect with scroll offset
                adjusted_rect = button.rect.copy()
                adjusted_rect.y -= self.scroll_offset
                
                # Check if click is on the adjusted position
                if adjusted_rect.collidepoint(event.pos):
                    if hasattr(button, 'tool_id'):
                        self.selected_tool = button.tool_id
                    if button.callback:
                        button.callback()
                    return True
        
        return False
    
    def set_selected_tool(self, tool_id: str) -> None:
        """Set the currently selected tool"""
        self.selected_tool = tool_id
