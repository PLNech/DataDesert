from config import *
from models.animals import Herbivore, Carnivore
from models.base import Position, EntityType
from models.plants import PLANT_SPECIES, Plant
from models.water import Water
from rendering.renderer import Renderer
from simulation.analytics import Analytics
from simulation.world import World
import pygame as pg
import numpy as np

class GameManager:
    """Manages the game state and progression"""

    def __init__(self, width: int = 1024, height: int = 768):
        # Initialize simulation components
        grid_width = width // (CELL_WIDTH + CELL_MARGIN)
        grid_height = height // (CELL_HEIGHT + CELL_MARGIN)

        self.world = World(grid_width, grid_height)
        self.analytics = Analytics(self.world)
        self.renderer = Renderer(width, height)

        # Game state
        self.running = True
        self.paused = False
        self.tick_rate = 30
        self.clock = pg.time.Clock()
        
        # Mouse position for UI updates
        self.mouse_pos = (0, 0)

        # Progression system
        self.unlocked_features = {
            "plants": True,  # Start with plants
            "herbivores": False,
            "carnivores": False,
            "weather": False,
            "genetics": False,
            "water": True,  # Start with water tool available
        }

        # Achievement system
        from collections import defaultdict

        # Initialize achievements with proper title-cased names
        self.achievements = {}
        
        # Basic progression achievements
        self.add_achievement("first_plant", "Grow your first plant")
        self.add_achievement("thriving_ecosystem", "Reach 100 plants")
        self.add_achievement("circle_of_life", "Have all three trophic levels present")
        self.add_achievement("genetic_diversity", "Reach 10 generations of animals")
        self.add_achievement("stable_ecosystem", "Maintain stable populations for 100 time steps")
        
        # Water-related achievements
        self.add_achievement("oasis_builder", "Create 5 water sources")
        self.add_achievement("water_world", "Create 10 water sources")
        self.add_achievement("moisture_master", "Achieve 50% average moisture level")
        self.add_achievement("flood_manager", "Survive a major rainfall event")
        
        # Plant-related achievements
        self.add_achievement("desert_gardener", "Grow 10 plants of each species")
        self.add_achievement("botanical_collection", "Have 20 plants of each species")
        self.add_achievement("plant_paradise", "Reach 200 plants")
        self.add_achievement("forest_maker", "Reach 500 plants")
        
        # Animal-related achievements
        self.add_achievement("herbivore_haven", "Have 20 herbivores")
        self.add_achievement("carnivore_country", "Have 10 carnivores")
        self.add_achievement("balanced_predation", "Maintain 3:1 herbivore to carnivore ratio")
        self.add_achievement("survival_expert", "Keep animals alive for 50 time steps")
        
        # Ecosystem-related achievements
        self.add_achievement("nutrient_cycle", "Achieve 70% average nutrient level")
        self.add_achievement("biodiversity_champion", "Reach biodiversity index of 1.0")
        self.add_achievement("ecosystem_engineer", "Reach ecosystem health of 0.8")
        self.add_achievement("long_term_stability", "Run simulation for 500 time steps")

        # Selected tool
        self.selected_tool = "cactus"  # Default tool
        
        # Notification system
        self.notifications = []
        self.notification_duration = 5  # seconds
        
        # Current UI tab (Main, Analytics, Achievements, Settings)
        self.current_tab = "Main"

    def add_achievement(self, slug, description):
        """Add an achievement with a properly formatted title"""
        title = " ".join(word.capitalize() for word in slug.split("_"))
        self.achievements[slug] = {
            "title": title,
            "description": description,
            "unlocked": False
        }

    def initialize(self) -> None:
        """Initialize the game world and UI"""
        # Create environment
        self.world.environment._create_oases(5)

        # Seed with initial plants only
        self.world.seed(plant_density=0.05, herbivore_density=0, carnivore_density=0)
        
        # Initialize UI elements
        self.renderer.initialize_ui(
            self.unlocked_features, 
            self.select_tool,
            self.achievements,
            {
                'toggle_pause': self.toggle_pause  # Pass pause toggle callback to interface
            }
        )
        
        # Set the initial selected tool in the UI
        self.renderer.set_selected_tool(self.selected_tool)
        
        # Add initial notification
        self.add_notification("Welcome to Data Desert! Start by placing plants and water.")

    def select_tool(self, tool_id):
        """Handler for tool selection from UI"""
        self.selected_tool = tool_id
        self.add_notification(f"Selected {self._get_tool_name(tool_id)}")
    
    def _get_tool_name(self, tool_id):
        """Get a friendly name for the tool"""
        tool_names = {
            "cactus": "Cactus",
            "desert_grass": "Desert Grass",
            "succulent": "Succulent",
            "herbivore": "Herbivore",
            "carnivore": "Carnivore",
            "water": "Water Source",
            "rain": "Rain"
        }
        return tool_names.get(tool_id, tool_id)

    def toggle_pause(self) -> None:
        """Toggle the pause state"""
        self.paused = not self.paused
        # Update the interface's pause state
        self.renderer.set_paused(self.paused)
        self.add_notification("Simulation " + ("paused" if self.paused else "resumed"))
        return self.paused

    def update(self) -> None:
        """Update game state for one time step"""
        # Update UI based on mouse position
        self.renderer.update_ui(self.mouse_pos)
        
        if not self.paused:
            self.world.update()
            self.analytics.update()

            # Check for feature unlocks
            self._check_feature_unlocks()

            # Check for achievements
            self._check_achievements()
            
            # Update notifications (remove expired)
            self._update_notifications()
            
            # Update UI with latest achievements
            self.renderer.update_achievements(self.achievements)

    def render(self) -> None:
        """Render the current game state"""
        self.renderer.render(self.world, self.analytics, self.notifications)

    def handle_events(self) -> None:
        """Handle pygame events"""
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.running = False
            elif event.type == pg.MOUSEMOTION:
                self.mouse_pos = event.pos
            elif event.type == pg.KEYDOWN:
                self._handle_key_event(event)
            elif event.type == pg.MOUSEBUTTONDOWN:
                # First, check if the UI handled the event
                if not self.renderer.handle_ui_event(event):
                    # If not, handle it for game interactions
                    self._handle_mouse_event(event)

    def _handle_key_event(self, event) -> None:
        """Handle keyboard events"""
        if event.key == pg.K_ESCAPE:
            self.running = False
        elif event.key == pg.K_SPACE:
            self.toggle_pause()
        elif event.key == pg.K_r:
            self._reset_world()
        elif event.key == pg.K_EQUALS or event.key == pg.K_PLUS:
            self.tick_rate = min(MAX_FPS, self.tick_rate + 5)
            self.add_notification(f"Speed: {self.tick_rate} FPS")
        elif event.key == pg.K_MINUS:
            self.tick_rate = max(MIN_FPS, self.tick_rate - 5)
            self.add_notification(f"Speed: {self.tick_rate} FPS")
        # Tab switching
        elif event.key == pg.K_1:
            self.current_tab = "Main"
            self.add_notification("Switched to Main view")
        elif event.key == pg.K_2:
            self.current_tab = "Analytics"
            self.add_notification("Switched to Analytics view")
        elif event.key == pg.K_3:
            self.current_tab = "Achievements"
            self.add_notification("Switched to Achievements view")
        elif event.key == pg.K_4:
            self.current_tab = "Settings"
            self.add_notification("Switched to Settings view")
        # Tools selection
        elif event.key == pg.K_q:
            if self.unlocked_features["plants"]:
                self.select_tool("cactus")
        elif event.key == pg.K_w:
            if self.unlocked_features["plants"]:
                self.select_tool("desert_grass")
        elif event.key == pg.K_e:
            if self.unlocked_features["plants"]:
                self.select_tool("succulent")
        elif event.key == pg.K_r:
            if self.unlocked_features["herbivores"]:
                self.select_tool("herbivore")
        elif event.key == pg.K_t:
            if self.unlocked_features["carnivores"]:
                self.select_tool("carnivore")
        elif event.key == pg.K_y:
            if self.unlocked_features["weather"]:
                self.select_tool("rain")
        elif event.key == pg.K_u:
            if self.unlocked_features["water"]:
                self.select_tool("water")

    def _handle_mouse_event(self, event) -> None:
        """Handle mouse events"""
        if event.button in (1, 3):  # Left or right click
            # Get grid position
            pos = pg.mouse.get_pos()
            col = pos[0] // (CELL_WIDTH + CELL_MARGIN)
            row = pos[1] // (CELL_HEIGHT + CELL_MARGIN)

            # Check if position is within the grid (not in UI area)
            if col >= 0 and col < self.world.width and row >= 0 and row < self.world.height:
                position = Position(col, row)

                # Left click adds, right click removes
                if event.button == 1:
                    self._use_tool(position)
                elif event.button == 3:
                    # Remove entity at position
                    entity = self.world.get_entity_at(position)
                    if entity:
                        entity_type = entity.entity_type.name.lower().capitalize()
                        self.world.remove_entity(entity.id)
                        self.add_notification(f"Removed {entity_type}")

    def _use_tool(self, position: Position) -> None:
        """Use the currently selected tool at a position"""
        if not self.world.is_position_occupied(position):
            if self.selected_tool in PLANT_SPECIES:
                plant = Plant(self.world.get_next_entity_id(), position, self.selected_tool)
                self.world.add_entity(plant)
                self.add_notification(f"Planted {self.selected_tool}")
                
            elif self.selected_tool == "herbivore" and self.unlocked_features["herbivores"]:
                herbivore = Herbivore(self.world.get_next_entity_id(), position)
                self.world.add_entity(herbivore)
                self.add_notification("Added herbivore")
                
            elif self.selected_tool == "carnivore" and self.unlocked_features["carnivores"]:
                carnivore = Carnivore(self.world.get_next_entity_id(), position)
                self.world.add_entity(carnivore)
                self.add_notification("Added carnivore")
                
            elif self.selected_tool == "water" and self.unlocked_features["water"]:
                water = Water(self.world.get_next_entity_id(), position, size=2.0)
                self.world.add_entity(water)
                self.add_notification("Created water source")
                
            elif self.selected_tool == "rain" and self.unlocked_features["weather"]:
                # Create a small rain shower
                for dx in range(-3, 4):
                    for dy in range(-3, 4):
                        x, y = position.x + dx, position.y + dy
                        if x >= 0 and x < self.world.width and y >= 0 and y < self.world.height:
                            # Add moisture
                            dist = np.sqrt(dx ** 2 + dy ** 2)
                            if dist <= 3:
                                moisture = max(0, 0.8 - (dist / 3) * 0.5)
                                self.world.environment.moisture[x, y] += moisture
                                self.world.environment.moisture[x, y] = min(1.0, self.world.environment.moisture[x, y])
                self.add_notification("Created rainfall")

    def _reset_world(self) -> None:
        """Reset the simulation world"""
        grid_width = self.world.width
        grid_height = self.world.height
        self.world = World(grid_width, grid_height)
        self.analytics = Analytics(self.world)
        
        # Reset achievements that should be reset on world restart
        for key in self.achievements:
            self.achievements[key]["unlocked"] = False
            
        # Update the UI with the reset achievements
        self.renderer.update_achievements(self.achievements)
        
        # Initialize the world
        self.initialize()
        self.add_notification("World reset")

    def _check_feature_unlocks(self) -> None:
        """Check if any features should be unlocked based on progress"""
        plant_count = len([e for e in self.world.entities.values() if e.entity_type == EntityType.PLANT])

        # Unlock herbivores once there are enough plants
        if not self.unlocked_features["herbivores"] and plant_count >= 50:
            self.unlocked_features["herbivores"] = True
            self.add_notification("Herbivores unlocked! Press R to select.")
            # Update the UI with the new available tool
            self.renderer.initialize_ui(self.unlocked_features, self.select_tool, self.achievements)

        # Unlock carnivores once there are enough herbivores
        herbivore_count = len([e for e in self.world.entities.values() if e.entity_type == EntityType.HERBIVORE])
        if not self.unlocked_features["carnivores"] and herbivore_count >= 20:
            self.unlocked_features["carnivores"] = True
            self.add_notification("Carnivores unlocked! Press T to select.")
            # Update the UI with the new available tool
            self.renderer.initialize_ui(self.unlocked_features, self.select_tool, self.achievements)

        # Unlock weather after certain time
        if not self.unlocked_features["weather"] and self.world.time_step >= 200:
            self.unlocked_features["weather"] = True
            self.add_notification("Weather system unlocked! Press Y to create rain.")
            # Update the UI with the new available tool
            self.renderer.initialize_ui(self.unlocked_features, self.select_tool, self.achievements)

    def _check_achievements(self) -> None:
        """Check if any achievements have been unlocked"""
        # Get entity counts
        plant_count = len([e for e in self.world.entities.values() if e.entity_type == EntityType.PLANT])
        herbivore_count = len([e for e in self.world.entities.values() if e.entity_type == EntityType.HERBIVORE])
        carnivore_count = len([e for e in self.world.entities.values() if e.entity_type == EntityType.CARNIVORE])
        water_count = len([e for e in self.world.entities.values() if e.entity_type == EntityType.WATER])
        
        # Get environmental stats
        avg_moisture = np.mean(self.world.environment.moisture)
        avg_nutrients = np.mean(self.world.environment.nutrients)
        
        # Count plants by species
        plant_species_counts = {}
        for entity in self.world.entities.values():
            if entity.entity_type == EntityType.PLANT:
                species_name = entity.species.name.lower()
                plant_species_counts[species_name] = plant_species_counts.get(species_name, 0) + 1

        # First plant
        if not self.achievements["first_plant"]["unlocked"] and plant_count > 0:
            self.achievements["first_plant"]["unlocked"] = True
            self.add_notification(f"Achievement unlocked: {self.achievements['first_plant']['title']}")

        # Thriving ecosystem
        if not self.achievements["thriving_ecosystem"]["unlocked"] and plant_count >= 100:
            self.achievements["thriving_ecosystem"]["unlocked"] = True
            self.add_notification(f"Achievement unlocked: {self.achievements['thriving_ecosystem']['title']}")

        # Circle of life
        if (not self.achievements["circle_of_life"]["unlocked"] and
                plant_count > 0 and herbivore_count > 0 and carnivore_count > 0):
            self.achievements["circle_of_life"]["unlocked"] = True
            self.add_notification(f"Achievement unlocked: {self.achievements['circle_of_life']['title']}")
            
        # Oasis builder
        if not self.achievements["oasis_builder"]["unlocked"] and water_count >= 5:
            self.achievements["oasis_builder"]["unlocked"] = True
            self.add_notification(f"Achievement unlocked: {self.achievements['oasis_builder']['title']}")
            
        # Water world
        if not self.achievements["water_world"]["unlocked"] and water_count >= 10:
            self.achievements["water_world"]["unlocked"] = True
            self.add_notification(f"Achievement unlocked: {self.achievements['water_world']['title']}")
            
        # Moisture master
        if not self.achievements["moisture_master"]["unlocked"] and avg_moisture >= 0.5:
            self.achievements["moisture_master"]["unlocked"] = True
            self.add_notification(f"Achievement unlocked: {self.achievements['moisture_master']['title']}")
            
        # Flood manager (check if rainfall event happened)
        if not self.achievements["flood_manager"]["unlocked"] and avg_moisture >= 0.7:
            self.achievements["flood_manager"]["unlocked"] = True
            self.add_notification(f"Achievement unlocked: {self.achievements['flood_manager']['title']}")
            
        # Desert gardener
        if (not self.achievements["desert_gardener"]["unlocked"] and 
                all(count >= 10 for count in plant_species_counts.values()) and
                len(plant_species_counts) >= 3):  # At least 3 species
            self.achievements["desert_gardener"]["unlocked"] = True
            self.add_notification(f"Achievement unlocked: {self.achievements['desert_gardener']['title']}")
            
        # Botanical collection
        if (not self.achievements["botanical_collection"]["unlocked"] and 
                all(count >= 20 for count in plant_species_counts.values()) and
                len(plant_species_counts) >= 3):  # At least 3 species
            self.achievements["botanical_collection"]["unlocked"] = True
            self.add_notification(f"Achievement unlocked: {self.achievements['botanical_collection']['title']}")
            
        # Plant paradise
        if not self.achievements["plant_paradise"]["unlocked"] and plant_count >= 200:
            self.achievements["plant_paradise"]["unlocked"] = True
            self.add_notification(f"Achievement unlocked: {self.achievements['plant_paradise']['title']}")
            
        # Forest maker
        if not self.achievements["forest_maker"]["unlocked"] and plant_count >= 500:
            self.achievements["forest_maker"]["unlocked"] = True
            self.add_notification(f"Achievement unlocked: {self.achievements['forest_maker']['title']}")
            
        # Herbivore haven
        if not self.achievements["herbivore_haven"]["unlocked"] and herbivore_count >= 20:
            self.achievements["herbivore_haven"]["unlocked"] = True
            self.add_notification(f"Achievement unlocked: {self.achievements['herbivore_haven']['title']}")
            
        # Carnivore country
        if not self.achievements["carnivore_country"]["unlocked"] and carnivore_count >= 10:
            self.achievements["carnivore_country"]["unlocked"] = True
            self.add_notification(f"Achievement unlocked: {self.achievements['carnivore_country']['title']}")
            
        # Balanced predation
        if (not self.achievements["balanced_predation"]["unlocked"] and 
                herbivore_count >= 15 and carnivore_count >= 5 and 
                2.5 <= (herbivore_count / max(1, carnivore_count)) <= 4):
            self.achievements["balanced_predation"]["unlocked"] = True
            self.add_notification(f"Achievement unlocked: {self.achievements['balanced_predation']['title']}")
            
        # Survival expert
        if not self.achievements["survival_expert"]["unlocked"] and self.world.time_step >= 50:
            if herbivore_count >= 5 and carnivore_count >= 2:
                self.achievements["survival_expert"]["unlocked"] = True
                self.add_notification(f"Achievement unlocked: {self.achievements['survival_expert']['title']}")
            
        # Nutrient cycle
        if not self.achievements["nutrient_cycle"]["unlocked"] and avg_nutrients >= 0.7:
            self.achievements["nutrient_cycle"]["unlocked"] = True
            self.add_notification(f"Achievement unlocked: {self.achievements['nutrient_cycle']['title']}")
            
        # Biodiversity champion
        if not self.achievements["biodiversity_champion"]["unlocked"] and self.analytics.get_biodiversity_index() >= 1.0:
            self.achievements["biodiversity_champion"]["unlocked"] = True
            self.add_notification(f"Achievement unlocked: {self.achievements['biodiversity_champion']['title']}")
            
        # Ecosystem engineer
        if not self.achievements["ecosystem_engineer"]["unlocked"] and self.analytics.get_ecosystem_health() >= 0.8:
            self.achievements["ecosystem_engineer"]["unlocked"] = True
            self.add_notification(f"Achievement unlocked: {self.achievements['ecosystem_engineer']['title']}")
            
        # Long term stability
        if not self.achievements["long_term_stability"]["unlocked"] and self.world.time_step >= 500:
            self.achievements["long_term_stability"]["unlocked"] = True
            self.add_notification(f"Achievement unlocked: {self.achievements['long_term_stability']['title']}")

    def add_notification(self, message: str) -> None:
        """Add a notification to the queue"""
        self.notifications.append({
            "message": message,
            "time": self.world.time_step,
            "duration": self.notification_duration
        })
        
    def _update_notifications(self) -> None:
        """Update and remove expired notifications"""
        current_time = self.world.time_step
        self.notifications = [
            notif for notif in self.notifications 
            if (current_time - notif["time"]) < notif["duration"] * self.tick_rate
        ]
        
    def run(self) -> None:
        """Main game loop"""
        self.initialize()
        
        while self.running:
            self.clock.tick(self.tick_rate)
            self.handle_events()
            self.update()
            self.render()

        pg.quit()
