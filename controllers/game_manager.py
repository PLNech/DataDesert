from config import *
from models.animals import Herbivore, Carnivore
from models.base import Position, EntityType
from models.plants import PLANT_SPECIES, Plant
from rendering.renderer import Renderer
from simulation.analytics import Analytics
from simulation.world import World
import pygame as pg

class GameManager:
    """Manages the game state and progression"""

    def __init__(self, width: int, height: int):
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

        # Progression system
        self.unlocked_features = {
            "plants": True,  # Start with plants
            "herbivores": False,
            "carnivores": False,
            "weather": False,
            "genetics": False,
        }

        # Achievement system
        self.achievements = {
            "first_plant": {"description": "Grow your first plant", "unlocked": False},
            "thriving_ecosystem": {"description": "Reach 100 plants", "unlocked": False},
            "circle_of_life": {"description": "Have all three trophic levels present", "unlocked": False},
            "genetic_diversity": {"description": "Reach 10 generations of animals", "unlocked": False},
            "stable_ecosystem": {"description": "Maintain stable populations for 100 time steps", "unlocked": False},
        }

        # Selected tool
        self.selected_tool = "cactus"  # Default tool

    def initialize(self) -> None:
        """Initialize the game world"""
        # Create environment
        self.world.environment._create_oases(5)

        # Seed with initial plants only
        self.world.seed(plant_density=0.05, herbivore_density=0, carnivore_density=0)

    def update(self) -> None:
        """Update game state for one time step"""
        if not self.paused:
            self.world.update()
            self.analytics.update()

            # Check for feature unlocks
            self._check_feature_unlocks()

            # Check for achievements
            self._check_achievements()

    def render(self) -> None:
        """Render the current game state"""
        self.renderer.render(self.world, self.analytics)

    def handle_events(self) -> None:
        """Handle pygame events"""
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.running = False
            elif event.type == pg.KEYDOWN:
                self._handle_key_event(event)
            elif event.type == pg.MOUSEBUTTONDOWN:
                self._handle_mouse_event(event)

    def _handle_key_event(self, event) -> None:
        """Handle keyboard events"""
        if event.key == pg.K_ESCAPE:
            self.running = False
        elif event.key == pg.K_SPACE:
            self.paused = not self.paused
        elif event.key == pg.K_r:
            self._reset_world()
        elif event.key == pg.K_EQUALS or event.key == pg.K_PLUS:
            self.tick_rate = min(MAX_FPS, self.tick_rate + 5)
        elif event.key == pg.K_MINUS:
            self.tick_rate = max(MIN_FPS, self.tick_rate - 5)
        # Tools selection
        elif event.key == pg.K_1:
            self.selected_tool = "cactus"
        elif event.key == pg.K_2:
            self.selected_tool = "desert_grass"
        elif event.key == pg.K_3:
            self.selected_tool = "succulent"
        elif event.key == pg.K_4 and self.unlocked_features["herbivores"]:
            self.selected_tool = "herbivore"
        elif event.key == pg.K_5 and self.unlocked_features["carnivores"]:
            self.selected_tool = "carnivore"
        elif event.key == pg.K_6 and self.unlocked_features["weather"]:
            self.selected_tool = "rain"

    def _handle_mouse_event(self, event) -> None:
        """Handle mouse events"""
        if event.button in (1, 3):  # Left or right click
            # Get grid position
            pos = pg.mouse.get_pos()
            col = pos[0] // (CELL_WIDTH + CELL_MARGIN)
            row = pos[1] // (CELL_HEIGHT + CELL_MARGIN)

            if col >= 0 and col < self.world.width and row >= 0 and row < self.world.height:
                position = Position(col, row)

                # Left click adds, right click removes
                if event.button == 1:
                    self._use_tool(position)
                elif event.button == 3:
                    # Remove entity at position
                    entity = self.world.get_entity_at(position)
                    if entity:
                        self.world.remove_entity(entity.id)

    def _use_tool(self, position: Position) -> None:
        """Use the currently selected tool at a position"""
        if not self.world.is_position_occupied(position):
            if self.selected_tool in PLANT_SPECIES:
                plant = Plant(self.world.get_next_entity_id(), position, self.selected_tool)
                self.world.add_entity(plant)
            elif self.selected_tool == "herbivore" and self.unlocked_features["herbivores"]:
                herbivore = Herbivore(self.world.get_next_entity_id(), position)
                self.world.add_entity(herbivore)
            elif self.selected_tool == "carnivore" and self.unlocked_features["carnivores"]:
                carnivore = Carnivore(self.world.get_next_entity_id(), position)
                self.world.add_entity(carnivore)
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

    def _reset_world(self) -> None:
        """Reset the simulation world"""
        grid_width = self.world.width
        grid_height = self.world.height
        self.world = World(grid_width, grid_height)
        self.analytics = Analytics(self.world)
        self.initialize()

    def _check_feature_unlocks(self) -> None:
        """Check if any features should be unlocked based on progress"""
        plant_count = len([e for e in self.world.entities.values() if e.entity_type == EntityType.PLANT])

        # Unlock herbivores once there are enough plants
        if not self.unlocked_features["herbivores"] and plant_count >= 50:
            self.unlocked_features["herbivores"] = True
            print("Herbivores unlocked!")

        # Unlock carnivores once there are enough herbivores
        herbivore_count = len([e for e in self.world.entities.values() if e.entity_type == EntityType.HERBIVORE])
        if not self.unlocked_features["carnivores"] and herbivore_count >= 20:
            self.unlocked_features["carnivores"] = True
            print("Carnivores unlocked!")

        # Unlock weather after certain time
        if not self.unlocked_features["weather"] and self.world.time_step >= 200:
            self.unlocked_features["weather"] = True
            print("Weather system unlocked!")

    def _check_achievements(self) -> None:
        """Check if any achievements have been unlocked"""
        # Get entity counts
        plant_count = len([e for e in self.world.entities.values() if e.entity_type == EntityType.PLANT])
        herbivore_count = len([e for e in self.world.entities.values() if e.entity_type == EntityType.HERBIVORE])
        carnivore_count = len([e for e in self.world.entities.values() if e.entity_type == EntityType.CARNIVORE])

        # First plant
        if not self.achievements["first_plant"]["unlocked"] and plant_count > 0:
            self.achievements["first_plant"]["unlocked"] = True
            print(f"Achievement unlocked: {self.achievements['first_plant']['description']}")

        # Thriving ecosystem
        if not self.achievements["thriving_ecosystem"]["unlocked"] and plant_count >= 100:
            self.achievements["thriving_ecosystem"]["unlocked"] = True
            print(f"Achievement unlocked: {self.achievements['thriving_ecosystem']['description']}")

        # Circle of life
        if (not self.achievements["circle_of_life"]["unlocked"] and
                plant_count > 0 and herbivore_count > 0 and carnivore_count > 0):
            self.achievements["circle_of_life"]["unlocked"] = True
            print(f"Achievement unlocked: {self.achievements['circle_of_life']['description']}")

        # TODO: Implement other achievement checks

    def run(self) -> None:
        """Main game loop"""
        while self.running:
            self.clock.tick(self.tick_rate)
            self.handle_events()
            self.update()
            self.render()

        pg.quit()
