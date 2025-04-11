from config import CELL_WIDTH, CELL_HEIGHT, CELL_MARGIN, GREY, BLUE, RED, WHITE, FIG
import pygame as pg

from models.base import EntityType
from models.water import Water
from simulation.analytics import Analytics
from simulation.world import World
from rendering.interface import Interface


class Renderer:
    """Responsible for rendering the simulation to the screen"""

    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.base_cell_width = CELL_WIDTH
        self.base_cell_height = CELL_HEIGHT
        self.base_cell_margin = CELL_MARGIN

        # Initialize pygame
        pg.init()
        self.display = pg.display.set_mode((width, height), pg.HWSURFACE | pg.DOUBLEBUF)
        pg.display.set_caption("DataDesert v2")

        # Create surfaces
        self.background = pg.Surface(self.display.get_size())
        
        # Only convert if display is initialized (checks for headless test environment)
        try:
            self.background = self.background.convert()
            self.background.fill(GREY)
        except pg.error:
            # We're in a test environment without a display
            self.background.fill(GREY)

        # Font for displaying information
        self.font = pg.font.SysFont('Arial', 18)
        self.notification_font = pg.font.SysFont('Arial', 16)
        
        # Initialize Interface instead of UIManager
        self.interface = Interface(width, height)

        # Initialize zoom controller
        from rendering.ui.zoom_controller import ZoomController
        self.zoom_controller = ZoomController()
        self.cell_width, self.cell_height, self.cell_margin = self.zoom_controller.get_cell_dimensions(
            self.base_cell_width, self.base_cell_height, self.base_cell_margin)
 
        # Add fullscreen attribute
        self.is_fullscreen = False

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
            
        # Update interface with world metrics
        if world.metrics:
            self.interface.update(world)
            
        # Render UI elements
        self.interface.draw(self.display)

        # Update display
        pg.display.update()
        
    def update_ui(self, mouse_pos):
        """Update UI elements based on mouse position"""
        # No need to explicitly update mouse position in new interface
        pass
        
    def handle_ui_event(self, event):
        """Handle UI events"""
        return self.interface.handle_event(event, None)  # Pass None for world, will be updated in render
    
    def initialize_ui(self, available_tools, select_tool_callback, achievements, control_callbacks=None):
        """Initialize UI with available tools and achievements"""
        # We need to clear existing tools to prevent duplicates 
        # (the interface.add_tool has protection, but just to be safe)
        if hasattr(self.interface.ui_manager, 'tool_panel'):
            self.interface.ui_manager.tool_panel.buttons = []
            
        # Map available tools to the new interface's tool system
        for tool_type, tools in available_tools.items():
            if not tools:
                continue
                
            if tool_type == "plants":
                self.interface.add_tool(
                    "Cactus", "cactus", 
                    lambda: select_tool_callback("cactus"),
                    "Drought-resistant, slow growing"
                )
                self.interface.add_tool(
                    "Desert Grass", "desert_grass", 
                    lambda: select_tool_callback("desert_grass"),
                    "Fast growing, needs more water"
                )
                self.interface.add_tool(
                    "Succulent", "succulent", 
                    lambda: select_tool_callback("succulent"),
                    "Stores water, moderate growth"
                )
            
            elif tool_type == "water":
                self.interface.add_tool(
                    "Water Source", "water", 
                    lambda: select_tool_callback("water"),
                    "Creates permanent water source"
                )
            
            elif tool_type == "herbivores":
                self.interface.add_tool(
                    "Herbivore", "herbivore", 
                    lambda: select_tool_callback("herbivore"),
                    "Plant eater, needs water"
                )
            
            elif tool_type == "carnivores":
                self.interface.add_tool(
                    "Carnivore", "carnivore", 
                    lambda: select_tool_callback("carnivore"),
                    "Hunts herbivores, needs water"
                )
        
        # Initialize achievements - clear existing ones first
        if hasattr(self.interface.ui_manager, 'achievement_panel'):
            self.interface.ui_manager.achievement_panel.achievements = []
            
        for achievement in achievements.values():
            self.interface.add_achievement(
                achievement["title"],
                achievement["description"],
                achievement["unlocked"]
            )
        
        # Merge default callbacks with any provided callbacks
        default_callbacks = {
            'reset': self.reset_callback,
            'zoom_in': self.zoom_in_callback,
            'zoom_out': self.zoom_out_callback,
            'fullscreen': self.toggle_fullscreen_callback,
            'chaos': self.toggle_chaos_callback
        }
        
        # Merge with provided callbacks, giving priority to provided ones
        if control_callbacks:
            default_callbacks.update(control_callbacks)
            
        self.interface.connect_controls(default_callbacks)
    
    def set_paused(self, paused: bool) -> None:
        """Set the pause state in the interface"""
        self.interface.set_paused(paused)
    
    def set_selected_tool(self, tool_id):
        """Set the currently selected tool in the UI"""
        self.interface.set_active_tool(tool_id)
    
    def update_achievements(self, achievements):
        """Update the achievements display"""
        # Clear existing achievements (this should be handled by the interface)
        for achievement in achievements.values():
            self.interface.add_achievement(
                achievement["title"],
                achievement["description"],
                achievement["unlocked"]
            )

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
                # Fig for herbivores
                pg.draw.rect(self.display, FIG, rect)

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

    # Add callback methods for the control panel
    def reset_callback(self):
        """Reset world callback - will be connected to game manager"""
        print("Reset world requested")
        # This will be overridden by game manager
        return "reset_world"
    
    def zoom_in_callback(self):
        """Zoom in callback"""
        print("Zooming in...")
        self.zoom_controller.zoom_in()
        self.cell_width, self.cell_height, self.cell_margin = self.zoom_controller.get_cell_dimensions(
            self.base_cell_width, self.base_cell_height, self.base_cell_margin)
        # Return a status for the calling code to use
        return "zoom_in"
    
    def zoom_out_callback(self):
        """Zoom out callback"""
        print("Zooming out...")
        self.zoom_controller.zoom_out()
        self.cell_width, self.cell_height, self.cell_margin = self.zoom_controller.get_cell_dimensions(
            self.base_cell_width, self.base_cell_height, self.base_cell_margin)
        # Return a status for the calling code to use
        return "zoom_out"
    
    def toggle_fullscreen_callback(self):
        """Toggle fullscreen callback"""
        print("Toggling fullscreen")
        # Store current dimensions
        current_w, current_h = self.display.get_size()
        
        # Toggle fullscreen state first
        self.is_fullscreen = not self.is_fullscreen
        
        # Create a new display with appropriate flags based on fullscreen state
        if self.is_fullscreen:
            self.display = pg.display.set_mode(
                (current_w, current_h), 
                pg.FULLSCREEN | pg.HWSURFACE | pg.DOUBLEBUF
            )
        else:
            self.display = pg.display.set_mode(
                (current_w, current_h), 
                pg.HWSURFACE | pg.DOUBLEBUF
            )
            
        # Recreate background surface with the new display size
        self.background = pg.Surface(self.display.get_size())
        
        # Only convert if display is initialized (checks for headless test environment)
        try:
            self.background = self.background.convert()
            self.background.fill(GREY)
        except pg.error:
            # We're in a test environment without a display
            self.background.fill(GREY)
        
        # Return a status for the calling code to use
        return "toggle_fullscreen"
    
    def toggle_chaos_callback(self):
        """Toggle chaos mode callback"""
        print("Chaos mode toggle requested")
        # Return a status for the calling code to use
        return "toggle_chaos"
