from config import CELL_WIDTH, CELL_HEIGHT, CELL_MARGIN, GREY, BLUE, RED, WHITE
import pygame as pg

from models.base import EntityType
from simulation.analytics import Analytics
from simulation.world import World
from rendering.ui import UIManager


class Renderer:
    """Responsible for rendering the simulation to the screen"""

    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.cell_width = CELL_WIDTH
        self.cell_height = CELL_HEIGHT
        self.cell_margin = CELL_MARGIN

        # Initialize pygame
        pg.init()
        self.display = pg.display.set_mode((width, height), pg.HWSURFACE | pg.DOUBLEBUF)
        pg.display.set_caption("DataDesert v2")

        # Create surfaces
        self.background = pg.Surface(self.display.get_size())
        self.background = self.background.convert()
        self.background.fill(GREY)

        # Font for displaying information
        self.font = pg.font.SysFont('Arial', 18)
        self.notification_font = pg.font.SysFont('Arial', 16)
        
        # UI Manager
        self.ui_manager = UIManager(width, height)

    def render(self, world: World, analytics: Analytics = None, notifications = None) -> None:
        """Render the current state of the world"""
        # Clear screen
        self.display.blit(self.background, (0, 0))

        # Render environment (moisture as background intensity)
        self._render_environment(world)

        # Render entities
        self._render_entities(world)

        # Render UI stats
        self._render_stats(world, analytics)
        
        # Render notifications if provided
        if notifications:
            self._render_notifications(notifications)
            
        # Render UI elements
        self.ui_manager.draw(self.display)

        # Update display
        pg.display.update()
        
    def update_ui(self, mouse_pos):
        """Update UI elements based on mouse position"""
        self.ui_manager.update(mouse_pos)
        
    def handle_ui_event(self, event):
        """Handle UI events"""
        return self.ui_manager.handle_event(event)
    
    def initialize_ui(self, available_tools, select_tool_callback, achievements):
        """Initialize UI with available tools and achievements"""
        self.ui_manager.initialize_tools(available_tools, select_tool_callback)
        self.ui_manager.update_achievements(achievements)
    
    def set_selected_tool(self, tool_id):
        """Set the currently selected tool in the UI"""
        self.ui_manager.set_selected_tool(tool_id)
    
    def update_achievements(self, achievements):
        """Update the achievements display"""
        self.ui_manager.update_achievements(achievements)

    def _render_environment(self, world: World) -> None:
        """Render environmental factors like moisture levels"""
        for x in range(world.width):
            for y in range(world.height):
                moisture = world.environment.moisture[x, y]
                nutrients = world.environment.nutrients[x, y]

                # Calculate position
                rect_x = (self.cell_margin + self.cell_width) * x + self.cell_margin
                rect_y = (self.cell_margin + self.cell_height) * y + self.cell_margin

                # Draw moisture as blue tint with alpha based on moisture level
                blue_tint = (200, 200, 255, int(moisture * 128))

                # Create a small surface for the cell
                cell_surface = pg.Surface((self.cell_width, self.cell_height))
                cell_surface.fill(GREY)

                # Draw blue tint based on moisture
                if moisture > 0.1:
                    # Calculate color based on moisture
                    blue = int(min(255, 100 + moisture * 155))
                    cell_surface.fill((100, 100, blue))

                # Draw on the display
                self.display.blit(cell_surface, (rect_x, rect_y))

    def _render_entities(self, world: World) -> None:
        """Render all entities in the world"""
        for entity in world.entities.values():
            rect_x = (self.cell_margin + self.cell_width) * entity.position.x + self.cell_margin
            rect_y = (self.cell_margin + self.cell_height) * entity.position.y + self.cell_margin
            rect = [rect_x, rect_y, self.cell_width, self.cell_height]

            if entity.entity_type == EntityType.PLANT:
                plant = entity  # type: Plant
                # Color based on plant species and size
                base_color = plant.species.color
                # Adjust brightness based on size
                size_factor = min(1.0, plant.size / plant.species.max_size)
                color = (
                    int(base_color[0] * size_factor),
                    int(base_color[1] * size_factor),
                    int(base_color[2] * size_factor)
                )
                pg.draw.rect(self.display, color, rect)

            elif entity.entity_type == EntityType.HERBIVORE:
                # Blue for herbivores
                pg.draw.rect(self.display, BLUE, rect)

            elif entity.entity_type == EntityType.CARNIVORE:
                # Red for carnivores
                pg.draw.rect(self.display, RED, rect)

            elif entity.entity_type == EntityType.WATER:
                # Render water as a blue circle
                water = entity  # type: Water
                # Deeper blue for water
                water_color = (0, 0, int(min(255, 150 + water.size * 20)))
                
                # Draw circle for water, size based on water size
                center_x = rect_x + self.cell_width // 2
                center_y = rect_y + self.cell_height // 2
                radius = int(min(self.cell_width, self.cell_height) * 0.5 * min(1.0, water.size / 3.0))
                
                pg.draw.circle(self.display, water_color, (center_x, center_y), radius)
                
                # Add a slightly lighter blue border
                border_color = (50, 150, 255)
                pg.draw.circle(self.display, border_color, (center_x, center_y), radius, 1)

    def _render_stats(self, world: World, analytics: Analytics = None) -> None:
        """Render stats and metrics on screen"""
        stats = [
            f"Time: {world.time_step}",
            f"Plants: {len([e for e in world.entities.values() if e.entity_type == EntityType.PLANT])}",
            f"Herbivores: {len([e for e in world.entities.values() if e.entity_type == EntityType.HERBIVORE])}",
            f"Carnivores: {len([e for e in world.entities.values() if e.entity_type == EntityType.CARNIVORE])}",
            f"Water Sources: {len([e for e in world.entities.values() if e.entity_type == EntityType.WATER])}",
        ]

        if analytics:
            stats.extend([
                f"Biodiversity: {analytics.get_biodiversity_index():.2f}",
                f"Ecosystem Health: {analytics.get_ecosystem_health():.2f}"
            ])

        for i, stat in enumerate(stats):
            text = self.font.render(stat, True, WHITE)
            self.display.blit(text, (10, 10 + i * 25))
    
    def _render_notifications(self, notifications) -> None:
        """Render notifications on screen"""
        if not notifications:
            return
            
        # Display notifications at the bottom of the screen
        notification_height = 25
        notification_margin = 5
        
        # Start from the bottom and go up
        y_pos = self.height - notification_margin - notification_height
        
        # Show the latest 5 notifications at most
        for notification in notifications[-5:]:
            message = notification["message"]
            
            # Create semi-transparent background
            notification_surface = pg.Surface((self.width * 0.8, notification_height))
            notification_surface.set_alpha(180)  # Semi-transparent
            notification_surface.fill((30, 30, 50))  # Dark blue-gray
            
            # Draw notification background
            notification_x = self.width * 0.1  # Centered with 10% margin on each side
            self.display.blit(notification_surface, (notification_x, y_pos))
            
            # Render text on top
            text = self.notification_font.render(message, True, WHITE)
            text_x = notification_x + 10  # Add some padding
            text_y = y_pos + (notification_height - text.get_height()) // 2  # Center vertically
            self.display.blit(text, (text_x, text_y))
            
            # Move up for the next notification
            y_pos -= notification_height + notification_margin
