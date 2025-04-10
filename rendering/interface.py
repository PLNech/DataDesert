import pygame as pg
from typing import Dict, Tuple, Optional, Any, Callable

from .ui.manager import UIManager
from models.base import EntityType, Entity

class Interface:
    """Main interface class that manages all UI interactions"""
    
    def __init__(self, screen_width: int, screen_height: int):
        """Initialize the interface with screen dimensions"""
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.ui_manager = UIManager(screen_width, screen_height)
        self.active_tool = None
        self.current_entity_to_place = None
        
        # Time speed scale (1.0 = normal)
        self.time_scale = 1.0
        self.paused = False
        
        # Setup initial achievements
        self._setup_achievements()
    
    def _setup_achievements(self) -> None:
        """Initialize achievements"""
        achievements = [
            {
                "title": "First Steps",
                "description": "Create your first plant",
                "completed": False
            },
            {
                "title": "Thriving Ecosystem",
                "description": "Have 50+ plants alive at once",
                "completed": False
            },
            {
                "title": "Water World",
                "description": "Create 5 water sources",
                "completed": False
            },
            {
                "title": "Circle of Life",
                "description": "Watch a full life cycle",
                "completed": False
            },
            {
                "title": "Desert Master",
                "description": "Create a sustainable ecosystem",
                "completed": False
            }
        ]
        
        for achievement in achievements:
            self.ui_manager.achievement_panel.add_achievement(
                achievement["title"], 
                achievement["description"], 
                achievement["completed"]
            )
    
    def draw(self, surface: pg.Surface) -> None:
        """Draw the interface on the given surface"""
        self.ui_manager.draw(surface)
    
    def handle_event(self, event: pg.event.Event, world=None) -> bool:
        """Process events for UI and game interactions"""
        # Handle UI interactions
        if self.ui_manager.handle_event(event):
            return True
        
        # Handle map clicks if a tool is active and we have a world
        if world and event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            # Only process clicks on the game area (not the UI sidebar)
            if event.pos[0] < self.screen_width - 240:  # 240 is sidebar width
                grid_x, grid_y = self._screen_to_grid(event.pos, world)
                
                if 0 <= grid_x < world.width and 0 <= grid_y < world.height:
                    # Update cell info panel
                    self._update_cell_info(world, grid_x, grid_y)
                    
                    # Process interactions based on active tool
                    if self.active_tool == "plant":
                        self._place_plant(world, grid_x, grid_y)
                    elif self.active_tool == "water":
                        self._place_water(world, grid_x, grid_y)
                    elif self.active_tool == "clear":
                        self._clear_cell(world, grid_x, grid_y)
                    
                    return True
        
        return False
    
    def _screen_to_grid(self, screen_pos: Tuple[int, int], world) -> Tuple[int, int]:
        """Convert screen coordinates to grid coordinates"""
        # TODO This would need to account for any zoom or pan
        # For simplicity, assuming 1:1 mapping initially
        grid_width = (self.screen_width - 240) / world.width
        grid_height = self.screen_height / world.height
        
        grid_x = int(screen_pos[0] / grid_width)
        grid_y = int(screen_pos[1] / grid_height)
        
        return grid_x, grid_y
    
    def _update_cell_info(self, world, grid_x: int, grid_y: int) -> None:
        """Update cell info panel with data about the selected cell"""
        from models.base import Position
        
        # Get entity at position if any
        pos = Position(grid_x, grid_y)
        entity = world.get_entity_at(pos)
        
        # Get environmental data
        moisture = world.get_moisture(pos)
        nutrients = world.get_nutrients(pos)
        
        # Update info panel
        self.ui_manager.update_cell_info(
            entity=entity,
            position=(grid_x, grid_y),
            moisture=moisture,
            nutrients=nutrients
        )
    
    def _place_plant(self, world, grid_x: int, grid_y: int) -> None:
        """Place a new plant in the world"""
        from models.base import Position
        from models.plants import Plant
        
        pos = Position(grid_x, grid_y)
        if not world.is_position_occupied(pos):
            # TODO this only creates a random plant (SHOULD be based on selected plant type)
            plant = Plant(
                world.get_next_entity_id(),
                pos,
                species="cactus"  # Default, would be set based on UI selection
            )
            world.add_entity(plant)
            
            # Update achievement for first plant
            self._complete_achievement("First Steps")
    
    def _place_water(self, world, grid_x: int, grid_y: int) -> None:
        """Place a new water source in the world"""
        from models.base import Position
        from models.water import Water
        
        pos = Position(grid_x, grid_y)
        if not world.is_position_occupied(pos):
            # Create water entity
            water = Water(
                world.get_next_entity_id(),
                pos,
                size=3.0  # Default size
            )
            world.add_entity(water)
            
            # Check for water achievement
            water_count = len([e for e in world.entities.values() 
                              if e.entity_type == EntityType.WATER])
            if water_count >= 5:
                self._complete_achievement("Water World")
    
    def _clear_cell(self, world, grid_x: int, grid_y: int) -> None:
        """Remove entity at the specified position"""
        from models.base import Position
        
        pos = Position(grid_x, grid_y)
        entity = world.get_entity_at(pos)
        
        if entity:
            world.remove_entity(entity.id)
    
    def _complete_achievement(self, title: str) -> None:
        """Mark an achievement as completed"""
        for i, achievement in enumerate(self.ui_manager.achievement_panel.achievements):
            if achievement['title'] == title and not achievement['completed']:
                self.ui_manager.achievement_panel.achievements[i]['completed'] = True
                # Here you could add a notification or sound effect
                print(f"Achievement unlocked: {title}")
                break
    
    def update(self, world) -> None:
        """Update interface state, check achievements, etc."""
        # Update analytics panel with world metrics
        if world.metrics and all(len(v) > 0 for v in world.metrics.values()):
            current_metrics = {
                key: values[-1] 
                for key, values in world.metrics.items()
            }
            self.ui_manager.update_analytics(current_metrics)
            
            # Check for achievements based on world state
            self._check_achievements(world)
    
    def _check_achievements(self, world) -> None:
        """Check for achievements that should be completed based on world state"""
        # Check for "Thriving Ecosystem" achievement
        plant_count = len([e for e in world.entities.values() 
                          if e.entity_type == EntityType.PLANT])
        if plant_count >= 50:
            self._complete_achievement("Thriving Ecosystem")
        
        # Other achievement checks could go here
    
    def resize(self, screen_width: int, screen_height: int) -> None:
        """Handle window resize"""
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.ui_manager.resize(screen_width, screen_height)
    
    def add_tool(self, text: str, tool_id: str, callback: Callable, info: Optional[str] = None) -> None:
        """Add a tool button to the tool panel"""
        self.ui_manager.add_tool(text, tool_id, callback, info)
    
    def set_active_tool(self, tool_id: str) -> None:
        """Set the currently selected tool"""
        self.active_tool = tool_id
        self.ui_manager.set_selected_tool(tool_id)
    
    def get_time_scale(self) -> float:
        """Get the current time scale"""
        return 0.0 if self.paused else self.time_scale
    
    def set_time_scale(self, scale: float) -> None:
        """Set simulation time scale"""
        self.time_scale = scale
    
    def toggle_pause(self) -> None:
        """Toggle pause state"""
        self.paused = not self.paused
    
    def is_paused(self) -> bool:
        """Check if simulation is paused"""
        return self.paused
    
    def add_achievement(self, title: str, description: str, completed: bool = False) -> None:
        """Add an achievement to the achievement panel"""
        self.ui_manager.achievement_panel.add_achievement(title, description, completed)
    
    def update_cell_info(self, entity, position, moisture, nutrients) -> None:
        """Update the cell info panel"""
        self.ui_manager.cell_info_panel.update_info(entity, position, moisture, nutrients)
    
    def update_analytics(self, metrics: Dict[str, float]) -> None:
        """Update the analytics panel with new metrics"""
        self.ui_manager.analytics_panel.update_metrics(metrics) 