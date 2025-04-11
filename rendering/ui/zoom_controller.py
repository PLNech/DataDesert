import pygame as pg

class ZoomController:
    """Manages zoom level for the simulation view"""
    
    def __init__(self, min_zoom=0.5, max_zoom=2.0, initial_zoom=1.0):
        self.min_zoom = min_zoom
        self.max_zoom = max_zoom
        self.zoom_level = initial_zoom
        self.zoom_step = 0.1
        
    def zoom_in(self):
        """Increase zoom level"""
        self.zoom_level = min(self.max_zoom, self.zoom_level + self.zoom_step)
        return self.zoom_level
        
    def zoom_out(self):
        """Decrease zoom level"""
        self.zoom_level = max(self.min_zoom, self.zoom_level - self.zoom_step)
        return self.zoom_level
        
    def set_zoom(self, level):
        """Set zoom to specific level"""
        self.zoom_level = max(self.min_zoom, min(self.max_zoom, level))
        return self.zoom_level
        
    def get_cell_dimensions(self, base_width, base_height, base_margin):
        """Calculate cell dimensions based on zoom level"""
        width = int(base_width * self.zoom_level)
        height = int(base_height * self.zoom_level)
        margin = max(1, int(base_margin * self.zoom_level))
        return width, height, margin 