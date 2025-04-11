from typing import List, Dict, Optional, Tuple
import numpy as np

from models.base import Entity, EntityType, Position
from models.environment import Environment
from models.plants import Plant, PLANT_SPECIES
from models.water import Water
from models.animals import Herbivore, Carnivore


class World:
    """Main container for the simulation world"""

    def __init__(self, width: int, height: int, create_water: bool = True):
        self.width = width
        self.height = height
        self.environment = Environment(width, height)

        # Entity storage
        self.entities: Dict[int, Entity] = {}
        self.entity_grid: Dict[Tuple[int, int], int] = {}  # Position -> entity_id
        self.next_entity_id = 1

        # Metrics tracking
        self.metrics = {
            "time": [],
            "plant_count": [],
            "herbivore_count": [],
            "carnivore_count": [],
            "water_count": [],  # Add water entity count tracking
            "avg_plant_size": [],
            "avg_herbivore_energy": [],
            "avg_carnivore_energy": [],
            "avg_moisture": [],
            "avg_nutrients": [],
        }
        self.time_step = 0
        
        # Create water entities at oasis positions if flag is set
        if create_water:
            self._create_water_entities()

    def _create_water_entities(self):
        """Create water entities at the oasis positions in the environment"""
        for x, y in self.environment.oasis_positions:
            # Create a water entity at each oasis center
            position = Position(x, y)
            
            # Skip if position is already occupied
            if self.is_position_occupied(position):
                continue
                
            # Create water entity with size based on moisture
            size = min(5.0, self.environment.moisture[x, y] * 5.0)
            water = Water(self.get_next_entity_id(), position, size=max(1.0, size))
            self.add_entity(water)

    def update(self) -> None:
        """Update the world state for one time step"""
        # Update environment first
        self.environment.update()

        # Update all entities
        entity_ids = list(self.entities.keys())
        for entity_id in entity_ids:
            if entity_id in self.entities:  # Check if still exists
                self.entities[entity_id].update(self)

        # Handle reproduction
        self._process_reproduction()

        # Update metrics
        self._update_metrics()

        self.time_step += 1

    def _process_reproduction(self) -> None:
        """Handle reproduction for all entities"""
        new_entities = []

        # Process plant seeding
        for entity in self.entities.values():
            if isinstance(entity, Plant):
                new_plant = entity.try_reproduce(self)
                if new_plant:
                    new_entities.append(new_plant)

        # Process animal mating
        # TODO: Implement animal mating logic

        # Add all new entities
        for entity in new_entities:
            self.add_entity(entity)

    def _update_metrics(self) -> None:
        """Collect data on current world state"""
        plants = [e for e in self.entities.values() if e.entity_type == EntityType.PLANT]
        herbivores = [e for e in self.entities.values() if e.entity_type == EntityType.HERBIVORE]
        carnivores = [e for e in self.entities.values() if e.entity_type == EntityType.CARNIVORE]
        waters = [e for e in self.entities.values() if e.entity_type == EntityType.WATER]

        self.metrics["time"].append(self.time_step)
        self.metrics["plant_count"].append(len(plants))
        self.metrics["herbivore_count"].append(len(herbivores))
        self.metrics["carnivore_count"].append(len(carnivores))
        self.metrics["water_count"].append(len(waters))

        self.metrics["avg_plant_size"].append(
            np.mean([p.size for p in plants]) if plants else 0
        )
        self.metrics["avg_herbivore_energy"].append(
            np.mean([h.energy for h in herbivores]) if herbivores else 0
        )
        self.metrics["avg_carnivore_energy"].append(
            np.mean([c.energy for c in carnivores]) if carnivores else 0
        )

        self.metrics["avg_moisture"].append(np.mean(self.environment.moisture))
        self.metrics["avg_nutrients"].append(np.mean(self.environment.nutrients))

    def get_next_entity_id(self) -> int:
        """Get a unique ID for a new entity"""
        entity_id = self.next_entity_id
        self.next_entity_id += 1
        return entity_id

    def add_entity(self, entity: Entity) -> None:
        """Add an entity to the world"""
        self.entities[entity.id] = entity
        self.entity_grid[(entity.position.x, entity.position.y)] = entity.id

    def remove_entity(self, entity_id: int) -> None:
        """Remove an entity from the world"""
        if entity_id in self.entities:
            entity = self.entities[entity_id]
            pos_key = (entity.position.x, entity.position.y)
            if pos_key in self.entity_grid:
                del self.entity_grid[pos_key]
            del self.entities[entity_id]

    def move_entity(self, entity_id: int, new_position: Position) -> None:
        """Move an entity to a new position"""
        if entity_id in self.entities:
            entity = self.entities[entity_id]
            old_pos_key = (entity.position.x, entity.position.y)
            new_pos_key = (new_position.x, new_position.y)

            # Update entity grid
            if old_pos_key in self.entity_grid:
                del self.entity_grid[old_pos_key]
            self.entity_grid[new_pos_key] = entity_id

            # Update entity position
            entity.position = new_position

    def is_position_occupied(self, position: Position) -> bool:
        """Check if a position contains an entity"""
        return (position.x, position.y) in self.entity_grid

    def get_entity_at(self, position: Position) -> Optional[Entity]:
        """Get the entity at a specific position"""
        pos_key = (position.x, position.y)
        if pos_key in self.entity_grid:
            return self.entities.get(self.entity_grid[pos_key])
        return None

    def get_moisture(self, position: Position) -> float:
        """Get moisture level at a position"""
        return self.environment.moisture[position.x, position.y]

    def get_nutrients(self, position: Position) -> float:
        """Get nutrient level at a position"""
        return self.environment.nutrients[position.x, position.y]

    def consume_moisture(self, position: Position, amount: float) -> None:
        """Consume moisture at a position"""
        self.environment.moisture[position.x, position.y] = max(
            0, self.environment.moisture[position.x, position.y] - amount
        )

    def consume_nutrients(self, position: Position, amount: float) -> None:
        """Consume nutrients at a position"""
        self.environment.nutrients[position.x, position.y] = max(
            0, self.environment.nutrients[position.x, position.y] - amount
        )

    def add_nutrients(self, position: Position, amount: float) -> None:
        """Add nutrients at a position (e.g., from decaying organisms)"""
        self.environment.nutrients[position.x, position.y] = min(
            1.0, self.environment.nutrients[position.x, position.y] + amount
        )

    def get_entities_in_radius(self, position: Position, radius: int,
                               entity_type: Optional[EntityType] = None) -> List[Entity]:
        """Get all entities within a certain radius of a position"""
        entities_in_radius = []

        for dx in range(-radius, radius + 1):
            for dy in range(-radius, radius + 1):
                x = position.x + dx
                y = position.y + dy

                if (x >= 0 and x < self.width and
                        y >= 0 and y < self.height):
                    pos = Position(x, y)
                    entity = self.get_entity_at(pos)

                    if entity is not None:
                        if entity_type is None or entity.entity_type == entity_type:
                            entities_in_radius.append(entity)

        return entities_in_radius

    def seed(self, plant_density: float = 0.05, herbivore_density: float = 0.01,
             carnivore_density: float = 0.005) -> None:
        """Seed the world with initial entities"""
        # Calculate counts
        grid_size = self.width * self.height
        plant_count = int(grid_size * plant_density)
        herbivore_count = int(grid_size * herbivore_density)
        carnivore_count = int(grid_size * carnivore_density)

        # Add plants
        plant_species = list(PLANT_SPECIES.keys())
        for _ in range(plant_count):
            x = np.random.randint(0, self.width)
            y = np.random.randint(0, self.height)
            pos = Position(x, y)

            if not self.is_position_occupied(pos):
                species = np.random.choice(plant_species)
                plant = Plant(self.get_next_entity_id(), pos, species)
                self.add_entity(plant)

        # Add herbivores
        for _ in range(herbivore_count):
            x = np.random.randint(0, self.width)
            y = np.random.randint(0, self.height)
            pos = Position(x, y)

            if not self.is_position_occupied(pos):
                herbivore = Herbivore(self.get_next_entity_id(), pos)
                self.add_entity(herbivore)

        # Add carnivores
        for _ in range(carnivore_count):
            x = np.random.randint(0, self.width)
            y = np.random.randint(0, self.height)
            pos = Position(x, y)

            if not self.is_position_occupied(pos):
                carnivore = Carnivore(self.get_next_entity_id(), pos)
                self.add_entity(carnivore)


