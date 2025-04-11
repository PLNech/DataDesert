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
        
        # Create time control buttons with reliable text instead of Unicode symbols
        time_controls = [
            ("<<", self.time_slow), 
            ("||", self.time_pause),
            (">", self.time_normal),
            (">>", self.time_fast)
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
            button = Button(button_rect, name, callback)
            # Add a control_id attribute to distinguish from tool buttons
            button.control_id = f"time_{name}"
            self.buttons.append(button)
            x_pos += button_width + 5
        
        # Add other controls below
        x_pos = self.rect.left + margin
        y_pos += button_height + margin
        
        for name, callback, width in other_controls:
            button_rect = pg.Rect(x_pos, y_pos, width, button_height)
            button = Button(button_rect, name, callback)
            # Add a control_id attribute to distinguish from tool buttons
            button.control_id = f"control_{name.lower()}"
            self.buttons.append(button)
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
        self.chaos_button.control_id = "control_chaos"
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
        """Set simulation to slow speed"""
        print("Slowing time")
        # Implementation is provided by Interface
    
    def time_pause(self) -> None:
        """Pause the simulation"""
        print("Pausing simulation")
        # Implementation is provided by Interface
    
    def time_normal(self) -> None:
        """Set simulation to normal speed"""
        print("Normal time")
        # Implementation is provided by Interface
    
    def time_fast(self) -> None:
        """Set simulation to fast speed"""
        print("Fast forward")
        # Implementation is provided by Interface
    
    def reset_world(self) -> None:
        """Reset the world simulation"""
        print("Resetting world")
        # Implementation is provided by Interface
    
    def zoom_in(self) -> None:
        """Increase zoom level"""
        print("Zooming in")
        # Implementation is provided by Interface
    
    def zoom_out(self) -> None:
        """Decrease zoom level"""
        print("Zooming out")
        # Implementation is provided by Interface
    
    def toggle_fullscreen(self) -> None:
        """Toggle fullscreen mode"""
        print("Toggling fullscreen")
        # Implementation is provided by Interface
    
    def toggle_chaos(self) -> None:
        """Toggle chaos mode for random entity spawning"""
        self.chaos_active = not self.chaos_active
        self.chaos_button.text = f"Chaos Mode: {'ON' if self.chaos_active else 'OFF'}"
        self.chaos_button.color = (200, 50, 50) if self.chaos_active else (120, 50, 50)
        print(f"Chaos mode {'activated' if self.chaos_active else 'deactivated'}")
        # Implementation of actual entity spawning is provided by Interface 

    def update_speed_buttons(self, active_speed: float) -> None:
        """Update the speed buttons to reflect current speed"""
        # Reset all button states
        self.speed_slow_selected = False
        self.speed_normal_selected = False
        self.speed_fast_selected = False
        
        # Set the active button
        if active_speed == 0.5:
            self.speed_slow_selected = True
        elif active_speed == 1.0:
            self.speed_normal_selected = True
        elif active_speed == 2.0:
            self.speed_fast_selected = True

    def update_pause_button(self, is_paused: bool) -> None:
        """Update the pause button to reflect current pause state"""
        self.pause_selected = is_paused 