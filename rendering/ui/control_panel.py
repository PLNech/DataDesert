import pygame as pg
from typing import List
from .panel import Panel
from .button import Button

class ControlPanel(Panel):
    """Panel for game controls like time control, reset, zoom"""
    
    def __init__(self, rect: pg.Rect):
        super().__init__(rect, title="Controls")
        self.buttons: List[Button] = []
        self.setup_buttons()
    
    def setup_buttons(self) -> None:
        """Initialize control buttons"""
        button_width, button_height = 40, 30
        margin = 10
        
        # Create time control buttons
        time_controls = [
            ("⏪", self.time_slow), 
            ("⏸", self.time_pause),
            ("▶", self.time_normal),
            ("⏩", self.time_fast)
        ]
        
        # Create other control buttons
        other_controls = [
            ("Reset", self.reset_world, 80),
            ("Zoom+", self.zoom_in, 70),
            ("Zoom-", self.zoom_out, 70),
            ("Fullscr", self.toggle_fullscreen, 70)
        ]
        
        # Add time control buttons in a row
        x_pos = self.rect.left + margin
        y_pos = self.rect.top + 30
        
        for name, callback in time_controls:
            button_rect = pg.Rect(x_pos, y_pos, button_width, button_height)
            self.buttons.append(Button(button_rect, name, callback))
            x_pos += button_width + 5
        
        # Add other controls below
        x_pos = self.rect.left + margin
        y_pos += button_height + margin
        
        for name, callback, width in other_controls:
            button_rect = pg.Rect(x_pos, y_pos, width, button_height)
            self.buttons.append(Button(button_rect, name, callback))
            x_pos += width + margin
            if x_pos + width > self.rect.right - margin:
                x_pos = self.rect.left + margin
                y_pos += button_height + 5
        
        # Add chaos god toggle button
        toggle_rect = pg.Rect(
            self.rect.left + margin,
            y_pos + button_height + margin,
            120,
            button_height
        )
        self.chaos_button = Button(
            toggle_rect, 
            "Chaos Mode: OFF", 
            self.toggle_chaos,
            color=(120, 50, 50)
        )
        self.buttons.append(self.chaos_button)
        self.chaos_active = False
    
    def draw(self, surface: pg.Surface) -> None:
        """Draw the control panel and its buttons"""
        super().draw(surface)
        if not self.visible:
            return
            
        for button in self.buttons:
            button.draw(surface)
    
    def handle_event(self, event: pg.event.Event) -> bool:
        """Process events for the control panel and its buttons"""
        if not self.visible:
            return False
            
        for button in self.buttons:
            if button.handle_event(event):
                return True
        return False
    
    # Control callback methods
    def time_slow(self) -> None:
        print("Slowing time")
        # To be connected to game time control
    
    def time_pause(self) -> None:
        print("Pausing simulation")
        # To be connected to game pause functionality
    
    def time_normal(self) -> None:
        print("Normal time")
        # To be connected to game time control
    
    def time_fast(self) -> None:
        print("Fast forward")
        # To be connected to game time control
    
    def reset_world(self) -> None:
        print("Resetting world")
        # To be connected to world reset functionality
    
    def zoom_in(self) -> None:
        print("Zooming in")
        # To be connected to zoom functionality
    
    def zoom_out(self) -> None:
        print("Zooming out")
        # To be connected to zoom functionality
    
    def toggle_fullscreen(self) -> None:
        print("Toggling fullscreen")
        # To be connected to fullscreen toggle
    
    def toggle_chaos(self) -> None:
        """Toggle the chaos mode on/off"""
        self.chaos_active = not self.chaos_active
        self.chaos_button.text = f"Chaos Mode: {'ON' if self.chaos_active else 'OFF'}"
        self.chaos_button.color = (200, 50, 50) if self.chaos_active else (120, 50, 50)
        print(f"Chaos mode {'activated' if self.chaos_active else 'deactivated'}")
        # To be connected to chaos spawn functionality 