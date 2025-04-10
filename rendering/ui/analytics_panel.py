import pygame as pg
from typing import Dict, List
from .panel import Panel

class AnalyticsPanel(Panel):
    """Panel for displaying analytics and graphs"""
    
    def __init__(self, rect: pg.Rect):
        super().__init__(rect, title="Analytics")
        self.metrics: Dict[str, List[float]] = {}
        self.max_history = 100  # Maximum number of data points to keep
        self.graph_rect = pg.Rect(
            rect.left + 10, 
            rect.top + 30, 
            rect.width - 20, 
            rect.height - 40
        )
    
    def update_metrics(self, metrics: Dict[str, float]) -> None:
        """Update tracked metrics with new values"""
        for key, value in metrics.items():
            if key not in self.metrics:
                self.metrics[key] = []
            
            self.metrics[key].append(value)
            
            # Trim history if needed
            if len(self.metrics[key]) > self.max_history:
                self.metrics[key] = self.metrics[key][-self.max_history:]
    
    def draw(self, surface: pg.Surface) -> None:
        """Draw the panel and analytics graphs"""
        super().draw(surface)
        if not self.visible or not self.metrics:
            return
            
        # Define colors for different metrics
        colors = {
            "plant_count": (100, 200, 100),
            "herbivore_count": (200, 150, 100),
            "carnivore_count": (200, 100, 100),
            "water_count": (100, 100, 200),
            "avg_moisture": (100, 150, 255),
            "avg_nutrients": (150, 200, 100)
        }
        
        # Draw graph background
        pg.draw.rect(surface, (50, 50, 50), self.graph_rect)
        
        # Draw lines for each metric
        metrics_to_show = [m for m in colors.keys() if m in self.metrics and len(self.metrics[m]) > 1]
        
        for metric in metrics_to_show:
            values = self.metrics[metric]
            if not values:
                continue
                
            # Normalize values to fit in the graph
            max_val = max(values) if max(values) > 0 else 1
            normalized = [v / max_val for v in values]
            
            # Draw the line
            points = []
            for i, val in enumerate(normalized):
                x = self.graph_rect.left + (i / len(normalized)) * self.graph_rect.width
                y = self.graph_rect.bottom - val * self.graph_rect.height
                points.append((x, y))
            
            if len(points) > 1:
                try:
                    # Validate points before drawing
                    valid_points = [(float(x), float(y)) for x, y in points]
                    pg.draw.lines(surface, colors[metric], False, valid_points, 2)
                except (TypeError, ValueError):
                    # Skip drawing this line if there's an error
                    print(f"Error drawing metric {metric}, invalid points detected")
        
        # Draw legend
        legend_y = self.graph_rect.top + 10
        for metric in metrics_to_show:
            # Draw color indicator
            pg.draw.rect(surface, colors[metric], 
                        (self.graph_rect.left + 5, legend_y, 10, 10))
            
            # Draw metric name
            font = pg.font.SysFont('Arial', 12)
            text = font.render(metric.replace('_', ' ').title(), True, (220, 220, 220))
            surface.blit(text, (self.graph_rect.left + 20, legend_y))
            
            legend_y += 20 